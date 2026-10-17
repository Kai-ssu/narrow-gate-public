"""
Building blocks for a Narrow Gate escape room. Each game is a Game made of
Stages; see philippi.py for a complete example. Answers stay on the server and
are never sent to the browser.
"""

import re
from dataclasses import dataclass


def normalize(code: str) -> str:
    """Ignore case, spaces and dashes so "2-8-4", "2 8 4" and "284" all match."""
    return re.sub(r"[^A-Z0-9]", "", code.upper())


@dataclass(frozen=True)
class Entrance:
    """The animation played once when a team first arrives on a page."""

    scene: str  # dark | songs | quake | torch | doors (see entrance.html)
    caption: str
    padlock: bool = True  # open a padlock first, since a code was just entered


@dataclass(frozen=True)
class Stage:
    number: int
    title: str
    reference: str
    code_prompt: str
    answers: tuple[str, ...]
    entrance: Entrance
    # Answer key for leaders: (part of the code, how players find it).
    key: tuple[tuple[str, str], ...]
    key_note: str = ""
    numeric: bool = True

    def accepts(self, code: str) -> bool:
        return normalize(code) in self.answers

    @property
    def display_code(self) -> str:
        """The main answer as written on a lock, e.g. "2-8-4"."""
        return "-".join(self.answers[0])


class Templates:
    """A game's own templates, by name: game.templates.intro_story
    is "game/games/<slug>/intro_story.html"."""

    def __init__(self, slug: str):
        self._slug = slug

    def __getattr__(self, name: str) -> str:
        return f"game/games/{self._slug}/{name}.html"


@dataclass(frozen=True)
class Game:
    # Used in every address, e.g. /philippi/play/. Must not clash with the
    # site's own pages (about, static) or the old addresses in urls.py.
    slug: str
    title: str
    passage: str  # e.g. "Acts 16:16–34"
    summary: str  # a sentence or two for the home page card
    setting: str  # small heading on the projector backdrop, e.g. "Philippi · AD 50"
    stages: tuple[Stage, ...]
    freedom_entrance: Entrance
    minutes: int = 40
    team_size: str = "4–8"
    story_note: str = ""  # shown before the story plays (a dramatized retelling, etc.)
    # Atmosphere lines on the backdrop. Keep them free of answers.
    backdrop_lines: tuple[str, ...] = ()
    # Story mode captions, as scenes for story.js (see philippi.py for the format).
    story_scenes: tuple[dict, ...] = ()

    @property
    def templates(self) -> Templates:
        return Templates(self.slug)

    @property
    def final_stage(self) -> int:
        return max(stage.number for stage in self.stages)

    def stage(self, number: int) -> Stage | None:
        return next((stage for stage in self.stages if stage.number == number), None)

    def card_template(self, stage: Stage) -> str:
        return f"game/games/{self.slug}/stages/stage_{stage.number}.html"
