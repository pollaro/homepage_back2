import functools

from django.core.cache import cache
from django.shortcuts import redirect

from hbl.views.auth_views import refresh_token


def auth_required(view, redirect_url="/hbl"):
    """
    This wrapper will check authorization for restricted views in hbl that require yahoo auth
    """

    @functools.wraps(view)
    def wrapper_auth_required(request, *args, **kwargs):
        if not cache.get("access_token"):
            return redirect(redirect_url)
        elif cache.ttl("access_token") <= 0 and cache.get("refresh_token"):
            refresh_token()
        return view(request, *args, **kwargs)

    return wrapper_auth_required
