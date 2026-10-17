import time
from functools import wraps

import segno
from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_http_methods, require_POST

from .games import DEFAULT_GAME, GAMES

# Proof this device entered the leader passcode (tied to the passcode itself).
LEADER = "leader"


class Progress:
    """One device's place in one game, kept in the signed session cookie.

    Keys are prefixed with the game's slug, so a phone can play several games
    without them mixing. "progress" is the highest stage the team may open:
    0 = not started, 1..final = on that stage, final + 1 = escaped.
    """

    def __init__(self, request, game):
        self.session = request.session
        self.game = game
        self.prefix = f"{game.slug}:"

    def get(self, name, default=None):
        return self.session.get(self.prefix + name, default)

    def set(self, name, value):
        self.session[self.prefix + name] = value

    @property
    def stage(self):
        return self.get("progress", 0)

    def unlock(self, number):
        self.set("progress", number)
        self.set("entrance", number)  # play this page's unlock scene once

    def take_entrance(self, number):
        """True only on the first view of a page the team has just unlocked."""
        return self.session.pop(self.prefix + "entrance", None) == number

    def clear(self):
        for key in [key for key in self.session.keys() if key.startswith(self.prefix)]:
            del self.session[key]

    def resume_url(self, stage=None):
        stage = self.stage if stage is None else stage
        slug = self.game.slug
        if stage < 1:
            return reverse("intro", args=[slug])
        if stage > self.game.final_stage:
            return reverse("freedom", args=[slug])
        return reverse("stage", args=[slug, stage])

    def timer_context(self):
        started_at = self.get("started_at")
        if started_at is None:
            return {}
        deadline = started_at + self.game.minutes * 60
        return {"deadline": deadline, "time_up": time.time() >= deadline}


def game_view(view):
    """Look up the game from the address (/<slug>/…) or 404."""

    @wraps(view)
    def wrapper(request, game, **kwargs):
        found = GAMES.get(game)
        if found is None:
            raise Http404
        return view(request, found, **kwargs)

    return wrapper


def legacy(name):
    """Redirect an old single-game address (e.g. /play/) to the default game."""

    def view(request, **kwargs):
        url = reverse(name, kwargs={"game": DEFAULT_GAME, **kwargs})
        query = request.META.get("QUERY_STRING")
        return redirect(f"{url}?{query}" if query else url)

    return view


# ---- Site pages ----


def landing(request):
    """Narrow Gate home page: every escape room on the site."""
    return render(request, "game/landing.html", {"games": GAMES.values()})


def about(request):
    return render(request, "game/about.html", {"games": GAMES.values()})


# ---- Players ----


@game_view
def game_home(request, game):
    return redirect("intro", game=game.slug)


@game_view
def intro(request, game):
    progress = Progress(request, game)
    return render(
        request,
        "game/intro.html",
        {"game": game, "progress": progress.stage, "resume_url": progress.resume_url()},
    )


@require_POST
@game_view
def start(request, game):
    progress = Progress(request, game)
    if progress.stage == 0:
        progress.unlock(1)
        progress.set("started_at", int(time.time()))
    return redirect(progress.resume_url())


@require_http_methods(["GET", "POST"])
@game_view
def stage(request, game, number):
    current = game.stage(number)
    if current is None:
        raise Http404
    progress = Progress(request, game)
    if number > progress.stage:
        return redirect(progress.resume_url())

    solved = number < progress.stage
    error = None
    if request.method == "POST":
        if solved:
            return redirect(progress.resume_url())
        if current.accepts(request.POST.get("code", "")):
            progress.unlock(number + 1)
            if number == game.final_stage:
                progress.set("finished_at", int(time.time()))
            return redirect(progress.resume_url(number + 1))
        error = "The lock doesn't budge. Check the Scriptures and try again."

    return render(
        request,
        "game/stage.html",
        {
            "game": game,
            "stage": current,
            "card_template": game.card_template(current),
            "solved": solved,
            "error": error,
            "reached": [s for s in game.stages if s.number <= progress.stage],
            "next_url": progress.resume_url(number + 1) if solved else None,
            "entrance": current.entrance if progress.take_entrance(number) else None,
            **progress.timer_context(),
        },
    )


@game_view
def freedom(request, game):
    progress = Progress(request, game)
    if progress.stage <= game.final_stage:
        return redirect(progress.resume_url())
    elapsed = progress.get("finished_at", 0) - progress.get("started_at", 0)
    minutes, seconds = divmod(max(elapsed, 0), 60)
    return render(
        request,
        "game/freedom.html",
        {
            "game": game,
            "elapsed": f"{minutes}:{seconds:02d}",
            "reached": game.stages,
            "entrance": game.freedom_entrance if progress.take_entrance(game.final_stage + 1) else None,
        },
    )


@require_http_methods(["GET", "POST"])
@game_view
def reset(request, game):
    """For the Gamemaster: wipe this device's progress in this game between groups."""
    if request.method == "POST":
        Progress(request, game).clear()
        return redirect("intro", game=game.slug)
    return render(request, "game/reset.html", {"game": game})


# ---- Leaders ----


def _join_link(request, game):
    """The game's player start page as a full address, plus a QR code for it as inline SVG."""
    url = request.build_absolute_uri(reverse("intro", args=[game.slug]))
    qr = segno.make(url, error="m").svg_inline(omitsize=True, border=2, dark="#120d09", light="#f1e3c4")
    return {
        "join_url": url,
        "join_url_short": url.split("://", 1)[-1].rstrip("/"),
        "join_qr": mark_safe(qr),  # generated by segno from our own URL
    }


@game_view
def facilitator(request, game):
    """Run-of-show for leaders. Public, so it must never show answers."""
    return render(request, "game/facilitator.html", {"game": game, **_join_link(request, game)})


def _leader_token():
    """Changes whenever LEADER_CODE changes, so a new passcode locks every device."""
    return salted_hmac("leader-answer-key", settings.LEADER_CODE).hexdigest()


@require_http_methods(["GET", "POST"])
@game_view
def answers(request, game):
    """Answer key for leaders, behind the LEADER_CODE passcode (one passcode for every game)."""
    configured = bool(settings.LEADER_CODE)
    error = None
    if request.method == "POST":
        if request.POST.get("action") == "lock":
            request.session.pop(LEADER, None)
            return redirect("answers", game=game.slug)
        if configured and constant_time_compare(request.POST.get("passcode", "").strip(), settings.LEADER_CODE):
            request.session[LEADER] = _leader_token()
            return redirect("answers", game=game.slug)
        error = "That passcode isn't right."
    unlocked = configured and constant_time_compare(request.session.get(LEADER, ""), _leader_token())
    return render(
        request,
        "game/answers.html",
        {
            "game": game,
            "configured": configured,
            "unlocked": unlocked,
            "error": error,
            "stages": game.stages if unlocked else [],
        },
    )


# ---- Projector ----


@game_view
def backdrop(request, game):
    """Full-screen projector display with the room countdown. No game state."""
    return render(request, "game/backdrop.html", {"game": game, **_join_link(request, game)})


@game_view
def story(request, game):
    """Projector story mode: the backstory as captions over moving scenery."""
    return render(request, "game/story.html", {"game": game})


@game_view
def debrief(request, game):
    """Projector slides with the debrief discussion questions."""
    return render(request, "game/debrief.html", {"game": game})
