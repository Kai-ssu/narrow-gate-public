from django.urls import include, path

from . import views

# Pages for one game, under /<slug>/ (e.g. /philippi/play/).
game_patterns = [
    path("", views.game_home, name="game"),
    path("play/", views.intro, name="intro"),
    path("start/", views.start, name="start"),
    path("stage/<int:number>/", views.stage, name="stage"),
    path("freedom/", views.freedom, name="freedom"),
    path("reset/", views.reset, name="reset"),
    path("lead/", views.facilitator, name="facilitator"),
    path("lead/answers/", views.answers, name="answers"),
    path("backdrop/", views.backdrop, name="backdrop"),
    path("story/", views.story, name="story"),
    path("debrief/", views.debrief, name="debrief"),
]

# Addresses from before the site held several games. They redirect to Midnight in
# Philippi, so old links and bookmarks keep working. Listed before the game pages
# so that, e.g., /lead/ isn't mistaken for a game called "lead".
legacy_patterns = [
    path("play/", views.legacy("intro")),
    path("stage/<int:number>/", views.legacy("stage")),
    path("freedom/", views.legacy("freedom")),
    path("reset/", views.legacy("reset")),
    path("lead/", views.legacy("facilitator")),
    path("lead/answers/", views.legacy("answers")),
    path("backdrop/", views.legacy("backdrop")),
    path("story/", views.legacy("story")),
    path("debrief/", views.legacy("debrief")),
]

urlpatterns = [
    path("", views.landing, name="landing"),
    path("about/", views.about, name="about"),
    *legacy_patterns,
    path("<slug:game>/", include(game_patterns)),
]
