# For Leaders

Want to run a Narrow Gate escape room with your own youth group? You're welcome to. Everything runs in the browser at **https://narrow-gate.onrender.com**. You don't need to install anything or create an account.

## Leader passcode

Each game's answer key is behind this passcode (the same one for every game):

```
thunder-midnight-compass-77
```

Please don't share it with players. If the passcode on the site ever stops working, it has been changed: check this file again for the new one.

## Running a game

Open the site and choose **Lead** on the game you're running. That page walks you through the night and links to the answer key:

1. **Before:** open the projector backdrop. Players scan its QR code to join, one phone per team.
2. **Start:** play the story on the projector (or read it aloud). It ends with **Start the game**, which starts the room timer. Then have teams tap **Begin**.
3. **During:** every clue has its own hint button. The leader page lists any cues for that game, like the earthquake in Midnight in Philippi.
4. **After:** press <kbd>D</kbd> on the backdrop to open the debrief questions.

You'll need:

- one phone per team (each game lists its team size)
- an **NIV** or **NKJV** Bible for each team (teams choose theirs in the app)
- the game's time (shown on the home page), plus 10–15 minutes for the debrief
- a projector or TV for the backdrop (optional, but it adds a lot)

## Hosting your own copy

If you'd rather run your own copy, deploy this repo to Render using `render.yaml`, then set your own passcode in the `LEADER_CODE` environment variable. The README lists every setting.
