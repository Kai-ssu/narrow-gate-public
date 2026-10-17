import time
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings
from django.urls import reverse
from django.utils.html import escape

from .games import GAMES
from .games.base import normalize
from .games.philippi import GAME as PHILIPPI
from .games.susa import GAME as SUSA
from .games.babylon import GAME as BABYLON
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

    def test_home_page_shows_each_difficulty(self):
        response = self.client.get(reverse("landing"))
        self.assertContains(response, "Difficulty 2.5 out of 5")
        self.assertContains(response, "Difficulty 4 out of 5")

    def test_difficulty_pips(self):
        self.assertEqual(PHILIPPI.difficulty_pips, ["full", "full", "half", "empty", "empty"])
        self.assertEqual(SUSA.difficulty_pips, ["full", "full", "full", "full", "empty"])

    def test_philippi_cards_still_show_references(self):
        self.client.post(url("start"))
        self.assertContains(self.client.get(url("stage", 1)), "Stage 1 · Acts 16:16–24")

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

    def test_reset_offered_once_time_is_up(self):
        self.start()
        self.assertContains(self.client.get(url("stage", 1)), 'class="card time-up" hidden')
        later = time.time() + PHILIPPI.minutes * 60 + 1
        with patch("game.views.time.time", return_value=later):
            response = self.client.get(url("stage", 1))
        self.assertContains(response, 'class="card time-up">')
        self.assertContains(response, f'action="{url("reset")}"')

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


class EveryGameTests(SimpleTestCase):
    """Each game, played start to finish, renders every page."""

    @override_settings(LEADER_CODE="open sesame")
    def test_every_page_renders(self):
        for game in GAMES.values():
            with self.subTest(game=game.slug):
                go = lambda name, *args: reverse(name, args=[game.slug, *args])
                self.client.post(go("reset"))
                for name in ["intro", "facilitator", "backdrop", "story", "debrief"]:
                    self.assertEqual(self.client.get(go(name)).status_code, 200, name)
                self.client.post(go("start"))
                for stage in game.stages:
                    page = self.client.get(go("stage", stage.number))
                    self.assertContains(page, escape(stage.title))
                    self.assertNotContains(page, "{#")  # no leaked template comments
                    self.client.post(go("stage", stage.number), {"code": stage.answers[0]})
                self.assertContains(self.client.get(go("freedom")), "You escaped in")
                self.client.post(go("answers"), {"passcode": "open sesame"})
                answers = self.client.get(go("answers"))
                for stage in game.stages:
                    self.assertContains(answers, stage.display_code)


def susa_url(name, *args):
    return reverse(name, args=[SUSA.slug, *args])


class SusaTests(SimpleTestCase):
    def submit(self, stage, code):
        return self.client.post(susa_url("stage", stage), {"code": code})

    def test_full_playthrough(self):
        self.client.post(susa_url("start"))
        self.assertRedirects(self.submit(1, "3-1-2-3"), susa_url("stage", 2))
        self.assertRedirects(self.submit(2, "faith"), susa_url("stage", 3))
        self.assertRedirects(self.submit(3, "7 1 8 4 2"), susa_url("stage", 4))
        self.assertRedirects(self.submit(4, "2312"), susa_url("freedom"))
        self.assertContains(self.client.get(susa_url("freedom")), "The Decree Is Sealed")

    def test_wrong_codes_are_rejected(self):
        self.client.post(susa_url("start"))
        self.assertContains(self.submit(1, "3923"), "Check the Scriptures and try again")
        self.submit(1, "3123")
        self.assertContains(self.submit(2, "IDLWK"), "Check the Scriptures and try again")

    def test_new_unlock_scenes(self):
        self.client.post(susa_url("start"))
        for stage, code, scene in [(1, "3123", "scroll"), (2, "FAITH", "night"), (3, "71842", "seal")]:
            self.submit(stage, code)
            self.assertContains(self.client.get(susa_url("stage", stage + 1)), f"entrance--{scene}")

    def test_strips_name_the_king_by_each_bible(self):
        self.client.post(susa_url("start"))
        self.submit(1, "3123")
        self.submit(2, "FAITH")
        response = self.client.get(susa_url("stage", 3))
        self.assertContains(response, "strips--events")
        self.assertContains(response, "Harbona points out the pole")
        self.assertContains(response, "Harbonah points out the gallows")

    def test_progress_is_separate_from_philippi(self):
        self.client.post(susa_url("start"))
        self.assertRedirects(self.client.get(url("stage", 1)), url("intro"))

    def test_cards_give_no_chapter_or_verse_references(self):
        import re

        self.client.post(susa_url("start"))
        for stage in SUSA.stages:
            page = self.client.get(susa_url("stage", stage.number)).content.decode()
            self.assertIsNone(re.search(r"Esther \d|[Vv]erses? \d", page), f"stage {stage.number}")
            self.client.post(susa_url("stage", stage.number), {"code": stage.answers[0]})

    @override_settings(LEADER_CODE="open sesame")
    def test_answer_key_keeps_the_references(self):
        self.client.post(susa_url("answers"), {"passcode": "open sesame"})
        response = self.client.get(susa_url("answers"))
        for stage in SUSA.stages:
            self.assertContains(response, stage.reference)

    def test_forty_minutes_and_difficulty_four(self):
        self.assertEqual(SUSA.minutes, 40)
        self.assertContains(self.client.get(susa_url("intro")), "Difficulty 4/5")
        self.assertContains(self.client.get(susa_url("facilitator")), "no chapter or verse references")

    def test_palace_backdrop_has_no_earthquake(self):
        response = self.client.get(susa_url("backdrop"))
        self.assertContains(response, "room-palace")
        self.assertContains(response, 'class="frieze"')
        self.assertContains(response, "Haman has returned")
        self.assertNotContains(response, 'data-action="quake"')
        self.assertNotContains(self.client.get(susa_url("facilitator")), "Earthquake")

    def test_philippi_keeps_its_cell_and_earthquake(self):
        response = self.client.get(url("backdrop"))
        self.assertContains(response, "room-cell")
        self.assertContains(response, 'data-action="quake"')
        self.assertNotContains(response, 'class="frieze"')


def babylon_url(name, *args):
    return reverse(name, args=[BABYLON.slug, *args])


class BabylonTests(SimpleTestCase):
    CODES = [(1, "4233"), (2, "5403"), (3, "PRIDE"), (4, "3642")]

    def submit(self, stage, code):
        return self.client.post(babylon_url("stage", stage), {"code": code})

    def test_full_playthrough(self):
        self.client.post(babylon_url("start"))
        for stage, code in self.CODES[:-1]:
            self.assertRedirects(self.submit(stage, code), babylon_url("stage", stage + 1))
        self.assertRedirects(self.submit(4, "3-6-4-2"), babylon_url("freedom"))
        self.assertContains(self.client.get(babylon_url("freedom")), "His Kingdom Endures")

    def test_old_guide_codes_are_rejected(self):
        self.client.post(babylon_url("start"))
        self.assertContains(self.submit(1, "1313"), "Check the Scriptures and try again")
        self.submit(1, "4233")
        self.assertContains(self.submit(2, "4403"), "Check the Scriptures and try again")

    def test_rated_five_with_fifty_minutes(self):
        self.assertEqual((BABYLON.difficulty, BABYLON.minutes), (5, 50))
        self.assertContains(self.client.get(reverse("landing")), "Difficulty 5 out of 5")

    def test_cards_give_no_chapter_or_verse_references(self):
        import re

        self.client.post(babylon_url("start"))
        for stage, code in self.CODES:
            page = self.client.get(babylon_url("stage", stage)).content.decode()
            self.assertIsNone(re.search(r"(Daniel|Kings|Chronicles|Jeremiah) \d|[Vv]erses? \d", page), f"stage {stage}")
            self.submit(stage, code)

    def test_solved_stage_shows_its_code_for_the_next_one(self):
        self.client.post(babylon_url("start"))
        self.submit(1, "4233")
        self.assertContains(self.client.get(babylon_url("stage", 1)), '<p class="solved-code">4-2-3-3</p>')

    def test_writing_scene_before_the_last_stage(self):
        self.client.post(babylon_url("start"))
        for stage, code in self.CODES[:-1]:
            self.submit(stage, code)
        response = self.client.get(babylon_url("stage", 4))
        self.assertContains(response, "entrance--writing")
        self.assertContains(response, "GSV OZHG WRTRG")  # the enciphered clue
