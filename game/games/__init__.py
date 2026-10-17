"""
The escape rooms on the site, in the order they appear on the home page.

To add a game: copy philippi.py to a new file, change its content, give it a new
slug, put its templates in templates/game/games/<slug>/, and add it here.
"""

from . import babylon, philippi, susa

GAMES = {game.slug: game for game in [philippi.GAME, susa.GAME, babylon.GAME]}

# Where the site's old single-game addresses (/play/, /backdrop/ …) now point.
DEFAULT_GAME = philippi.GAME.slug
