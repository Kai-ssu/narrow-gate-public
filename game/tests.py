from dataclasses import replace
from types import SimpleNamespace

from django.test import SimpleTestCase, override_settings
from django.urls import reverse

from .games import GAMES
from .games.base import normalize
from .games.philippi import GAME as PHILIPPI
from .views import Progress

SLUG = PHILIPPI.slug


def url(name, *args):
    """Address of a Midnight in Philippi page, e.g. url("stage", 2)."""
    return reverse(name, args=[SLUG, *args])


class NormalizeTests(SimpleTestCase):
    def test_ignores_case_spaces_and_dashes(self):
        self.assertEqual(normalize(" j-p m-h "), "JPMH")
        self.assertEqual(normalize("2-8-4"), "284")


class ProgressTests(SimpleTestCase):
    def test_each_game_keeps_its_own_progress(self):
        request = SimpleNamespace(session={})
        other = replace(PHILIPPI, slug="another-game")
        Progress(request, PHILIPPI).unlock(3)
        Progress(request, other).unlock(1)
        self.assertEqual(Progress(request, PHILIPPI).stage, 3)
        self.assertEqual(Progress(request, other).stage, 1)

        Progress(request, other).clear()
        self.assertEqual(Progress(request, other).stage, 0)
        self.assertEqual(Progress(request, PHILIPPI).stage, 3)


class SiteTests(SimpleTestCase):
    def test_home_page_lists_every_game(self):
        response = self.client.get(reverse("landing"))
        self.assertContains(response, "Narrow Gate")
        for game in GAMES.values():
            self.assertContains(response, game.title)
            self.assertContains(response, f'href="{reverse("intro", args=[game.slug])}"')
            self.assertContains(response, f'href="{reverse("facilitator", args=[game.slug])}"')

    def test_about_page(self):
        self.assertContains(self.client.get(reverse("about")), "Kye Laurel")

    def test_game_address_opens_its_start_page(self):
        self.assertRedirects(self.client.get(reverse("game", args=[SLUG])), url("intro"))

    def test_unknown_game_404(self):
        self.assertEqual(self.client.get("/no-such-game/play/").status_code, 404)

    def test_old_addresses_redirect_to_midnight_in_philippi(self):
        for old, new in [
            ("/play/", url("intro")),
            ("/lead/", url("facilitator")),
            ("/lead/answers/", url("answers")),
            ("/story/", url("story")),
            ("/debrief/", url("debrief")),
            ("/backdrop/?timer=off", url("backdrop") + "?timer=off"),
        ]:
            self.assertRedirects(self.client.get(old), new, fetch_redirect_response=False)


class GameFlowTests(SimpleTestCase):
    def start(self):
        return self.client.post(url("start"))

    def submit(self, stage, code):
        return self.client.post(url("stage", stage), {"code": code})

    def test_intro_renders(self):
        response = self.client.get(url("intro"))
        self.assertContains(response, "Begin")
        self.assertContains(response, "The year is AD 50")

    def test_stages_locked_before_start(self):
        self.assertRedirects(self.client.get(url("stage", 1)), url("intro"))

    def test_start_opens_stage_one(self):
        self.assertRedirects(self.start(), url("stage", 1))
        self.assertContains(self.client.get(url("stage", 1)), "The Accusation")

    def test_wrong_code_stays_on_stage(self):
        self.start()
        self.assertContains(self.submit(1, "123"), "Check the Scriptures and try again")
        self.assertRedirects(self.client.get(url("stage", 2)), url("stage", 1))

    def test_cannot_skip_ahead(self):
        self.start()
        self.assertRedirects(self.submit(3, "16425"), url("stage", 1))

    def test_old_word_lock_answer_is_rejected(self):
        self.start()
        self.submit(1, "284")
        self.assertContains(self.submit(2, "SONG"), "Check the Scriptures and try again")

    def test_full_playthrough(self):
        self.start()
        self.assertRedirects(self.submit(1, "2-8-4"), url("stage", 2))
        self.assertRedirects(self.submit(2, "j p m h"), url("stage", 3))
        self.assertRedirects(self.submit(3, "1-6-4-2-5"), url("stage", 4))
        self.assertRedirects(self.submit(4, "7302"), url("freedom"))
        response = self.client.get(url("freedom"))
        self.assertContains(response, "You escaped in")
        self.assertContains(response, "The Doors Are Open")

    def test_solved_stage_can_be_revisited(self):
        self.start()
        self.submit(1, "284")
        self.assertContains(self.client.get(url("stage", 1)), "Unlocked")

    def test_freedom_locked_until_finished(self):
        self.start()
        self.assertRedirects(self.client.get(url("freedom")), url("stage", 1))

    def test_answers_not_in_page(self):
        self.start()
        self.assertNotContains(self.client.get(url("stage", 1)), "284")

    def test_entrance_plays_once_after_unlock(self):
        self.start()
        self.assertContains(self.client.get(url("stage", 1)), "entrance--dark")
        self.assertNotContains(self.client.get(url("stage", 1)), 'class="entrance')
        self.submit(1, "284")
        self.assertContains(self.client.get(url("stage", 2)), "entrance--songs")
        self.assertNotContains(self.client.get(url("stage", 1)), 'class="entrance')
        self.assertNotContains(self.client.get(url("stage", 2)), 'class="entrance')

    def test_entrance_on_freedom(self):
        self.start()
        for stage, code in [(1, "284"), (2, "JPMH"), (3, "16425"), (4, "7302")]:
            self.submit(stage, code)
        response = self.client.get(url("freedom"))
        self.assertContains(response, "entrance--doors")
        self.assertContains(response, f'action="{url("reset")}"')
        self.assertNotContains(self.client.get(url("freedom")), 'class="entrance')

    def test_reset_clears_progress(self):
        self.start()
        self.submit(1, "284")
        self.client.post(url("reset"))
        self.assertRedirects(self.client.get(url("stage", 1)), url("intro"))

    def test_stage_three_has_strips_for_each_bible(self):
        self.start()
        self.submit(1, "284")
        self.submit(2, "JPMH")
        response = self.client.get(url("stage", 3))
        self.assertContains(response, 'data-bible="niv"')
        self.assertContains(response, 'data-bible="nkjv"')
        self.assertContains(response, "NO HARM")
        self.assertNotContains(response, "{#")  # no leaked template comments

    def test_every_stage_has_the_bible_switch(self):
        self.start()
        for stage, code in [(1, "284"), (2, "JPMH"), (3, "16425"), (4, None)]:
            self.assertContains(self.client.get(url("stage", stage)), 'data-bible-pick="nkjv"')
            if code:
                self.submit(stage, code)
        self.assertContains(self.client.get(url("intro")), 'data-bible-pick="nkjv"')

    def test_unknown_stage_404(self):
        self.start()
        self.assertEqual(self.client.get(url("stage", 9)).status_code, 404)


class LeaderTests(SimpleTestCase):
    def test_leader_page_has_join_qr_and_no_answers(self):
        response = self.client.get(url("facilitator"))
        self.assertContains(response, "<svg")
        self.assertContains(response, "press <kbd>E</kbd>")  # this game's own tips
        for stage in PHILIPPI.stages:
            for answer in stage.answers:
                self.assertNotContains(response, answer)

    @override_settings(LEADER_CODE="open sesame")
    def test_answer_key_needs_the_passcode(self):
        locked = self.client.get(url("answers"))
        self.assertContains(locked, 'name="passcode"')
        self.assertNotContains(locked, "2-8-4")

        wrong = self.client.post(url("answers"), {"passcode": "guess"})
        self.assertContains(wrong, "That passcode")
        self.assertNotContains(wrong, "2-8-4")

        self.client.post(url("answers"), {"passcode": "open sesame"})
        unlocked = self.client.get(url("answers"))
        for code in ["2-8-4", "J-P-M-H", "1-6-4-2-5", "7-3-0-2"]:
            self.assertContains(unlocked, code)

        self.client.post(url("answers"), {"action": "lock"})
        self.assertNotContains(self.client.get(url("answers")), "2-8-4")

    def test_new_passcode_locks_unlocked_devices(self):
        with override_settings(LEADER_CODE="old code"):
            self.client.post(url("answers"), {"passcode": "old code"})
            self.assertContains(self.client.get(url("answers")), "2-8-4")
        with override_settings(LEADER_CODE="new code"):
            self.assertNotContains(self.client.get(url("answers")), "2-8-4")

    @override_settings(LEADER_CODE="")
    def test_answer_key_stays_locked_without_a_passcode(self):
        self.assertNotContains(self.client.post(url("answers"), {"passcode": ""}), "2-8-4")
        self.assertContains(self.client.get(url("answers")), "LEADER_CODE")


class ProjectorTests(SimpleTestCase):
    def test_backdrop_has_join_qr_and_links(self):
        response = self.client.get(url("backdrop"))
        self.assertContains(response, 'id="clock"')
        self.assertContains(response, "<svg")
        self.assertContains(response, f"testserver{url('intro')}".rstrip("/"))
        self.assertContains(response, f'href="{url("debrief")}"')
        self.assertContains(response, f'href="{url("story")}"')
        self.assertContains(response, 'id="backdrop-lines"')

    def test_backdrop_needs_no_game_progress(self):
        self.client.get(url("backdrop"))
        self.assertFalse(any(key.endswith("progress") for key in self.client.session.keys()))

    def test_story_page_has_scenes_and_scenery(self):
        response = self.client.get(url("story"))
        self.assertContains(response, 'id="caption"')
        self.assertContains(response, 'id="story-scenes"')
        self.assertContains(response, 'class="skyline"')

    def test_debrief_shows_questions_only(self):
        response = self.client.get(url("debrief"))
        for title in ["Praise in the Dark", "Mercy Over Self-Preservation", "The Domino Effect of Faith"]:
            self.assertContains(response, title)
        self.assertNotContains(response, "Facilitator Focus")
