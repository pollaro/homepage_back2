from django.urls import re_path

from hbl.views.auth_views import CheckLoggedInView, OauthView, RedirectURIView
from hbl.views.team_views import TeamsView

urlpatterns = [
    re_path(r"^login/?$", OauthView.as_view()),
    re_path(r"^redirect/?$", RedirectURIView.as_view()),
    re_path(r"^check/?$", CheckLoggedInView.as_view()),
    re_path(r"^teams/?$", TeamsView.as_view()),
]
