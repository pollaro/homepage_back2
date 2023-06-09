from django.urls import re_path

from hbl.views.auth_views import CheckLoggedInView, OauthView, RedirectURIView
from hbl.views.player_views import (
    ProspectAddView,
    ProspectRemoveView,
    ProspectRosterView,
    TeamRosterView,
)
from hbl.views.team_views import TeamDetailView, TeamsView

urlpatterns = [
    re_path(r"^login/?$", OauthView.as_view()),
    re_path(r"^redirect/?$", RedirectURIView.as_view()),
    re_path(r"^check/?$", CheckLoggedInView.as_view()),
    re_path(r"^teams/?$", TeamsView.as_view()),
    re_path(r"^team/(?P<team_id>[0-9]{1,2})/?$", TeamDetailView.as_view()),
    re_path(r"^roster/(?P<team_id>[0-9]{1,2})/?$", TeamRosterView.as_view()),
    re_path(r"^prospects/?$", ProspectRosterView.as_view()),
    re_path(r"^prospects/(?P<team_id>[0-9]{1,2})/?$", ProspectRosterView.as_view()),
    re_path(r"^prospects/add/?$", ProspectAddView.as_view()),
    re_path(r"^prospects/remove/?$", ProspectRemoveView.as_view()),
]
