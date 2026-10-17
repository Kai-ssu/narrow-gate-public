"""
Midnight in Philippi: Paul and Silas in prison, Acts 16:16–34.

Built from docs/midnight-in-philippi/ (the Facilitator Guide and Printable Kit),
with clues reworked for the NIV and NKJV. Its templates are in
templates/game/games/philippi/.
"""

from .base import Entrance, Game, Stage

GAME = Game(
    slug="philippi",
    title="Midnight in Philippi",
    passage="Acts 16:16–34",
    summary="Paul and Silas are beaten and locked in the stocks. Work through four stages, from the "
    "accusation to the jailer's question, “What must I do to be saved?”",
    setting="Philippi · AD 50",
    minutes=40,
    team_size="4–8",
    story_note="A dramatized retelling of Acts 16:16–24. Read the full passage in your Bible for every detail.",
    stages=(
        Stage(
            1,
            "The Accusation",
            "Acts 16:16–24",
            "Enter the 3-digit code",
            ("284",),
            Entrance("dark", "Philippi, AD 50. The cell door slams shut.", padlock=False),
            key=(
                ("2", "Paul and Silas were seized and dragged into the marketplace (16:19)."),
                ("8", "The spirit left the girl in verse 18."),
                ("4", "Their feet were fastened in the stocks in verse 24."),
            ),
        ),
        Stage(
            2,
            "Songs in the Stocks",
            "Acts 16:25–26",
            "Enter the 4-letter code",
            ("JPMH",),
            Entrance("songs", "Midnight. In the darkness, a song begins…"),
            key=(
                ("J", "Nehemiah 8:10: “the joy of the LORD is your strength.”"),
                ("P", "Psalm 119:164: “Seven times a day I praise you.”"),
                ("M", "Acts 16:25: the time of night was midnight."),
                ("H", "Acts 16:25: they were singing hymns."),
            ),
            key_note="Letters go in Bible order: Nehemiah, Psalms, then Acts (time of night before what they sang).",
            numeric=False,
        ),
        Stage(
            3,
            "The Earthquake & the Blade",
            "Acts 16:26–28",
            "Enter the 5-digit code",
            ("16425",),
            Entrance("quake", "Suddenly, a violent earthquake!"),
            key=(
                ("NIV", "DON'T (I) · HARM (VI) · YOURSELF! (IV) · WE ARE ALL (II) · HERE! (V)"),
                ("NKJV", "DO (I) · YOURSELF (VI) · NO HARM (IV) · FOR WE ARE ALL (II) · HERE (V)"),
            ),
            key_note="Strips in the order of Paul's shout in Acts 16:28. Both Bibles give the same code.",
        ),
        Stage(
            4,
            "What Must I Do?",
            "Acts 16:29–34",
            "Enter the 4-digit code",
            ("7302",),
            Entrance("torch", "The jailer calls for lights…"),
            key=(
                ("7", "BELIEVE has 7 letters (16:31)."),
                ("3", "The jailer washed their wounds (NKJV: stripes) in verse 33."),
                ("0", "No prisoners fled: “We are all here” (16:28)."),
                ("2", "Faith and joy in the jailer's household (16:34)."),
            ),
        ),
    ),
    freedom_entrance=Entrance("doors", "Every door flies open."),
    backdrop_lines=(
        "The inner cell is dark and damp.",
        "The stocks bite into your ankles.",
        "Somewhere above, a guard paces the stone floor.",
        "A single torch hisses on the wall.",
        "The outer doors are bolted fast.",
        "Midnight approaches…",
        "Do not lose heart.",
        "The other prisoners are listening.",
    ),
    # Each scene sets the look, plays an optional cue, then shows its lines one at a time.
    #   setting: "outside" (the city at dusk, from story_scenery.html) or "inside" (the cell)
    #   tint:    red wash over the scene      moon: the moon brightens in the cell window
    #   effect:  crowd | beating | slam | finale (see story.js)
    story_scenes=(
        {
            "setting": "outside",
            "lines": [
                "The year is AD 50.",
                "You are traveling with the apostle Paul and Silas through the Roman colony of Philippi,",
                "a proud military outpost filled with pagan worship, Roman law, and economic greed.",
            ],
        },
        {
            "setting": "outside",
            "lines": [
                "For days, as you walked to the place of prayer, a young slave girl possessed by a spirit "
                "of prediction followed you, crying out:",
                "“These men are servants of the Most High God, who proclaim to you the way of salvation!”",
                "Finally Paul, deeply troubled, turned and commanded the spirit in the name of Jesus Christ to leave her.",
                "It left her that very hour.",
            ],
        },
        {
            "setting": "outside",
            "tint": True,
            "effect": "crowd",
            "lines": [
                "Her owners realized their hope of making money was gone.",
                "Enraged, they seized Paul and Silas and dragged them into the marketplace before the Roman rulers.",
                "The crowds joined in the attack.",
            ],
        },
        {
            "setting": "outside",
            "tint": True,
            "effect": "beating",
            "lines": ["The magistrates tore their clothes off them and commanded them to be beaten with rods."],
        },
        {
            "setting": "inside",
            "effect": "slam",
            "lines": [
                "After many blows, Paul and Silas were thrown into the inner prison,",
                "their feet secured in painful wooden stocks. The outer doors are bolted.",
            ],
        },
        {
            "setting": "inside",
            "moon": True,
            "lines": [
                "Midnight approaches. The prison is dark, damp, and hopeless.",
                "To break free and witness the power of God tonight, you must work through four stages of testing:",
                "confronting the accusation, singing in the darkness, surviving the earthquake, and delivering "
                "the message of life to your jailer.",
            ],
        },
        {
            "setting": "inside",
            "moon": True,
            "effect": "finale",
            "lines": ["Your 40 minutes begin now."],
        },
    ),
)
