from django.shortcuts import get_object_or_404

from canvas.exceptions import ServiceError, ValidationError
from drawquest.apps.drawquest_auth.models import User
from drawquest.apps.following import models
from drawquest.models import user_profile
from canvas import bgwork
from drawquest.api_decorators import api_decorator
from canvas.metrics import Metrics
from canvas.view_guards import require_user

urlpatterns = []
api = api_decorator(urlpatterns)


def _delete_user_profile_cache(follower, followee):
    user_profile.delete_cache(follower.username)
    user_profile.delete_cache(followee.username)

@api('follow_user')
@require_user
def follow_user(request, username):
    """ `username` can be a string or a list of strings. """
    usernames = username
    if isinstance(username, basestring):
        usernames = [username]

    for username in usernames:
        Metrics.follow_user.record(request, username=username)
        user_to_follow = get_object_or_404(User, username=username)

        try:
            request.user.follow(user_to_follow)
        except ValueError as e:
            raise ValidationError(e.message)

        _delete_user_profile_cache(request.user, user_to_follow)

@api('unfollow_user')
@require_user
def unfollow_user(request, username):
    Metrics.unfollow_user.record(request, username=username)
    user_to_unfollow = get_object_or_404(User, username=username)
    request.user.unfollow(user_to_unfollow)

    _delete_user_profile_cache(request.user, user_to_unfollow)

@api('followers')
def followers(request, username, offset='top', direction='next'):
    user = get_object_or_404(User, username=username)
    followers, pagination = models.followers(user, offset=offset, direction=direction, viewer=request.user, request=request)

    return {'followers': followers, 'pagination': pagination}

@api('following')
def following(request, username, offset='top', direction='next'):
    user = get_object_or_404(User, username=username)
    following, pagination = models.following(user, offset=offset, direction=direction, viewer=request.user, request=request)

    return {'following': following, 'pagination': pagination}

@api('is_following')
def is_following(request, username):
    if not request.user.is_authenticated():
        is_following = False
    else:
        user = get_object_or_404(User, username=username)
        is_following = request.user.is_following(user)

    return {'is_following': is_following}

