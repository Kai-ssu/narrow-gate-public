"""
The Secret of Susa: Esther, Mordecai and Haman's decree, Esther 2–9.

Built from docs/secret-of-susa/ (the Facilitator Guide), with clues checked
against the NIV and NKJV. Its templates are in templates/game/games/susa/.

Rated 4 out of 5. The puzzles alone come to about 3.8, so the game is pushed up
to 4 with a shorter timer (40 minutes rather than the guide's 45) and no chapter
or verse references on the cards: teams find their own way through Esther 2–9.
Keep references out of the clue cards and hints; the answer key still has them.
"""

from .base import Entrance, Game, Stage

GAME = Game(
    slug="susa",
    title="The Secret of Susa",
    passage="Esther 2–9",
    summary="Haman's decree threatens every Jew in the Persian Empire. Search the royal archives in four "
    "stages to help Queen Esther unmask him, “for such a time as this.”",
    setting="Susa · 474 BC",
    minutes=40,
    team_size="4–8",
    difficulty=4,
    show_references=False,
    story_note="A dramatized retelling from the book of Esther. Read the whole book in your Bible for every detail.",
    room="palace",
    time_up_line="Haman has returned to the king's court.",
    stages=(
        Stage(
            1,
            "The Lineage & the Decree",
            "Esther 2:5–3:13",
            "Enter the 4-digit code",
            ("3123",),
            Entrance("dark", "Susa, 474 BC. The archive doors close behind you.", padlock=False),
            key=(
                ("3", "Esther 2:5 names three ancestors: Jair, Shimei and Kish."),
                ("1", "Esther 3:7: the first month, the month of Nisan."),
                ("2", "Esther 2:21: Bigthana (NKJV: Bigthan) and Teresh."),
                ("3", "Esther 3:13: destroy, kill and annihilate."),
            ),
        ),
        Stage(
            2,
            "The Cipher of the Scepter",
            "Esther 4:16",
            "Enter the 5-letter word",
            ("FAITH",),
            Entrance("scroll", "A sealed scroll arrives from the King's Gate."),
            key=(
                ("K = 3", "Esther 4:16: “do not eat or drink for three days” (NKJV: “neither eat nor drink”)."),
                ("FAITH", "I D L W K, each shifted back 3 letters: F A I T H."),
            ),
            numeric=False,
        ),
        Stage(
            3,
            "The Sleepless Night",
            "Esther 5–7",
            "Enter the 5-digit code",
            ("71842",),
            Entrance("night", "That night the king could not sleep."),
            key=(
                ("Set aside", "Strip 3 (Nebuchadnezzar, Daniel 3) and strip 5 (Nehemiah, Nehemiah 2)."),
                ("7", "Esther's first banquet (Esther 5:4–8)."),
                ("1", "The king cannot sleep and has the records read (6:1)."),
                ("8", "Haman leads Mordecai through the city on horseback (6:10–11)."),
                ("4", "Esther reveals Haman's plot at the second banquet (7:1–6)."),
                ("2", "Harbona (NKJV: Harbonah) points out the pole (NKJV: gallows) and Haman dies on it (7:9–10)."),
            ),
            key_note="Both Bibles give the same code.",
        ),
        Stage(
            4,
            "The King's Royal Decree",
            "Esther 8–9",
            "Enter the 4-digit code",
            ("2312",),
            Entrance("seal", "A new decree must be written."),
            key=(
                ("2", "Esther receives Haman's estate (8:1) and Mordecai the signet ring (8:2)."),
                ("3", "Esther 8:9: Sivan is the third month."),
                ("1", "Esther 8:15: one crown of gold (NIV: large, NKJV: great)."),
                ("2", "The 14th and 15th days of Adar (9:17–21)."),
            ),
        ),
    ),
    freedom_entrance=Entrance("doors", "The new decree is sealed. God's people will stand."),
    backdrop_lines=(
        "Lamps flicker in the royal archive.",
        "Purple and gold hang still in the night air.",
        "Somewhere in the court, Haman's informers are listening.",
        "Mordecai waits at the King's Gate.",
        "The golden scepter rests in the king's hand.",
        "The decree has been sealed with the king's ring.",
        "Every hour brings Haman closer.",
        "Perhaps you have come for such a time as this.",
    ),
    # Each scene sets the look, plays an optional cue, then shows its lines one at a time.
    #   setting: "outside" (Susa at dusk, from story_scenery.html) or "inside" (the palace hall)
    #   tint:    red wash over the scene      moon: the moon brightens in the palace window
    #   effect:  crowd | beating | slam | finale (see story.js)
    story_scenes=(
        {
            "setting": "outside",
            "lines": [
                "The year is 474 BC.",
                "You stand within the grand winter citadel of Susa, imperial capital of the Persian Empire.",
            ],
        },
        {
            "setting": "outside",
            "tint": True,
            "effect": "slam",
            "lines": [
                "Outside these palace walls, darkness looms over the Jewish nation.",
                "Haman the Agagite, prime minister to King Ahasuerus (Xerxes), has cast the Pur, the lot,",
                "and secured an irrevocable royal decree ordering the slaughter of every Jewish man, woman, "
                "and child on a single day.",
            ],
        },
        {
            "setting": "inside",
            "lines": [
                "You are trusted scribes and confidants within the household of Mordecai and Queen Esther.",
                "Mordecai has sent word through the King's Gate, but royal guards and informers surround the court.",
            ],
        },
        {
            "setting": "inside",
            "lines": [
                "To save our people, Queen Esther must enter the king's inner court unsummoned:",
                "an act punishable by death, unless the king holds out his golden scepter.",
                "But Esther needs the strength, wisdom, and undeniable facts to unmask Haman before the king.",
            ],
        },
        {
            "setting": "inside",
            "moon": True,
            "lines": [
                "Four locked archives sit before you: ancestral records, intercepted scrolls, royal court "
                "chronicles, and official decrees.",
                "Deciphering these records will equip Esther to break Haman's snare.",
            ],
        },
        {
            "setting": "inside",
            "moon": True,
            "lines": [
                "You have 40 minutes before Haman returns to the king's court.",
                "Seek the truth in the Scriptures, hold fast to faith,",
                "and remember: perhaps you have come to your position for such a time as this.",
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
