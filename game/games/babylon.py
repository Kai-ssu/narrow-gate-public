"""
The Writing on the Wall: Babylon on the night it fell, Daniel 1–5.

Built from docs/writing-on-the-wall/ (the revised Facilitator Guide), with
clues checked against the NIV and NKJV. Its templates are in
templates/game/games/babylon/.

Rated 5 out of 5: no chapter or verse references on the cards, one jump outside
Daniel (Solomon's temple), and every stage needs the one before it. Stage 2
uses Stage 1's code, Stage 3's genuine fragment is the one Stage 2's code points
to (the card doesn't say so; teams must make the link), and
Stage 4's last clue is written in the cipher built in Stage 3. Keep references
out of the clue cards and hints; the answer key still has them.
"""

from .base import Entrance, Game, Stage

GAME = Game(
    slug="babylon",
    title="The Writing on the Wall",
    passage="Daniel 1–5",
    summary="Babylon, the night it fell. Four sealed archives, no chapter or verse references, and every "
    "stage holds the key to the next. For teams who know their Bibles.",
    setting="Babylon · 539 BC",
    minutes=50,
    team_size="4–8",
    difficulty=5,
    show_references=False,
    story_note="A dramatized setting inspired by the book of Daniel. Read Daniel 1–5 in your Bible for the full account.",
    room="palace",
    time_up_line="That very night, Babylon fell.",
    stages=(
        Stage(
            1,
            "The Captives' Identity Matrix",
            "Daniel 1:5–7; 2:48–49",
            "Enter the 4-digit code",
            ("4233",),
            Entrance("dark", "Babylon, 539 BC. The feast has begun.", padlock=False),
            key=(
                ("Grid", "1:6 lists Daniel, Hananiah, Mishael, Azariah. Daniel = Belteshazzar, Hananiah = Shadrach, "
                 "Mishael = Meshach, Azariah = Abednego (1:7)."),
                ("4", "Azariah, renamed Abednego, is 4th in the list."),
                ("2", "Hananiah, renamed Shadrach, is 2nd."),
                ("3", "Trained for three years (1:5)."),
                ("3", "Shadrach, Meshach and Abednego set over the province at Daniel's request (2:49)."),
            ),
            key_note="Teams who find Daniel 1:7 can skip the grid, but still need the list order from 1:6.",
        ),
        Stage(
            2,
            "The Sanctuary & the Furnace",
            "1 Kings 6:20; Daniel 3:21–27",
            "Enter the 4-digit code",
            ("5403",),
            Entrance("torch", "The furnace roars."),
            key=(
                ("5", "Inner sanctuary 20 cubits long (1 Kings 6:20; also 2 Chronicles 3:8), ÷ 4 from Stage 1."),
                ("4", "Daniel 3:21: robes, trousers, turbans, other clothes (NKJV: coats … other garments)."),
                ("0", "Daniel 3:27: not a hair of their heads was singed."),
                ("3", "Daniel 3:23: these three men fell bound into the furnace (the four of 3:25 are the trap)."),
            ),
        ),
        Stage(
            3,
            "The Cipher of Babylon",
            "Jeremiah 25:26; Daniel 4:37",
            "Enter the 5-letter word",
            ("PRIDE",),
            Entrance("scroll", "Five fragments from the palace records."),
            key=(
                ("III", "The card only says one fragment is genuine. Stage 2's last digit (3) points to fragment III, KIRWV."),
                ("PRIDE", "K→P, I→R, R→I, W→D, V→E. Daniel 4:37: “those who walk in pride…”"),
            ),
            key_note="The decoys decode to WRATH, GREED, FOLLY and SCORN. Teams who miss the link to Stage 2 can decode "
            "all five and check which word is in Daniel 4:37. Teams keep their cipher table for Stage 4.",
            numeric=False,
        ),
        Stage(
            4,
            "Weighed and Found Wanting",
            "Daniel 5",
            "Enter the 4-digit code",
            ("3642",),
            Entrance("writing", "The fingers of a human hand appear."),
            key=(
                ("3", "Daniel 5:7 (also 16, 29): third highest ruler (NKJV: third ruler)."),
                ("6", "Daniel 5:4: gold, silver, bronze, iron, wood and stone."),
                ("4", "Daniel 5:25: mene, mene, tekel, parsin (NKJV: UPHARSIN)."),
                ("2", "The enciphered clue asks the last digit of Darius's age: sixty-two (5:31)."),
            ),
        ),
    ),
    freedom_entrance=Entrance("doors", "The archives are open. God's kingdom endures."),
    backdrop_lines=(
        "A thousand nobles drink in the king's hall.",
        "Gold and silver goblets catch the lamplight.",
        "They praise gods of gold and silver, bronze, iron, wood and stone.",
        "Beyond the walls, the night is too quiet.",
        "The armies of the Medes and Persians are waiting.",
        "The lampstand burns beside the plaster wall.",
        "Each archive holds the key to the next.",
        "The kingdom of God will never be destroyed.",
    ),
    # Each scene sets the look, plays an optional cue, then shows its lines one at a time.
    #   setting: "outside" (Babylon at dusk, from story_scenery.html) or "inside" (the banquet hall)
    #   tint:    red wash over the scene      moon: the moon brightens in the hall's window
    #   effect:  crowd | beating | slam | finale (see story.js)
    story_scenes=(
        {
            "setting": "outside",
            "lines": [
                "Babylon, 539 BC.",
                "The greatest city on earth is feasting.",
            ],
        },
        {
            "setting": "inside",
            "effect": "crowd",
            "lines": [
                "King Belshazzar has thrown a great banquet for a thousand of his nobles.",
                "Wine is poured into the gold and silver goblets that Nebuchadnezzar carried off from the temple "
                "of God in Jerusalem,",
                "and the guests raise them in praise of gods of gold and silver, bronze, iron, wood and stone.",
            ],
        },
        {
            "setting": "outside",
            "tint": True,
            "lines": ["Outside the walls, the armies of the Medes and Persians are waiting."],
        },
        {
            "setting": "inside",
            "moon": True,
            "lines": [
                "You are scribes among the exiles of Judah, keepers of the records of Daniel,",
                "who was carried to Babylon as a young man more than sixty years ago.",
                "Tonight his archives lie sealed in four locked chests.",
            ],
        },
        {
            "setting": "inside",
            "moon": True,
            "lines": [
                "Nothing in them is labelled. No book, no chapter, no verse.",
                "Only those who know the Scriptures will find their way through,",
                "and each archive holds the key to the next.",
            ],
        },
        {
            "setting": "inside",
            "moon": True,
            "effect": "slam",
            "lines": [
                "You have fifty minutes.",
                "When the hand begins to write, it will be too late.",
            ],
        },
        {
            "setting": "inside",
            "moon": True,
            "effect": "finale",
            "lines": ["Your time begins now."],
        },
    ),
)
