from canvas.bgwork import defer
from canvas.notifications import expander
from canvas.notifications.notification_models import PendingNotification


# In all these methods, the first parameter is the Actor. ie, the person who comitted the action. For example. the
# person who replied to a thread or remixed a threaed. The recipient can be figured out from the second param, which
# is typically a Comment.


class Actions(object):
    """ Each item in the ACTIONS dict gets turned into a method of this class. """
    ACTIONS = {
        # When you @reply in a thread, current_user is the user who created the reply
        'replied': ['comment'],
        # When you remix someone else's image
        'remixed': ['comment'],
        # When you just reply in a thread. We need to tell the OP.
        'thread_replied': ['comment'],
        # When you sticker a comment. But only non-epic stickers.
        'stickered': ['comment_sticker'],
        'epic_stickered': ['comment_sticker'],
        'first_starred': ['comment_sticker'],
        'leveled_up': ['reward_stickers'],
        # Received daily number ones
        'daily_free_stickers': ['reward_stickers'],
        # Use this to schedule sending out the newsletter to a user.
        'newsletter': [],
        # Digest and 24-hour emails.
        'digest': [],
        # Invite another user to remix your OP.
        'invite_remixer': ['comment', 'invitee'],
        # Invite another user to complete a monster
        'invite_monster_remixer': ['comment', 'invitee'],
        # When a user follows another
        'followed_by_user': ['followee'],
        # Post promoted in feed
        'post_promoted': ['comment'],
        # Thread promoted in feed
        'thread_promoted': ['comment'],

        # DrawQuest
        'playback': ['comment'],
        'starred': ['comment_sticker'],
        'facebook_friend_joined': ['facebook_friends'],
        'twitter_friend_joined': ['twitter_friends'],
        'followee_posted': ['comment'],
        'followee_created_ugq': ['quest'],
        'quest_of_the_day': ['quest'],
        'new_color_alert': ['message'],
        'featured_in_explore': ['comment'],
        'invite_user': ['quest', 'invitee'],
    }

    @classmethod
    def _create_action(cls, action_name, arg_names):
        @classmethod
        def action(cls, actor, *args, **kwargs):
            action_kwargs = dict(zip(arg_names, args))
            pending_notification = PendingNotification(actor, action_name, **action_kwargs)
            if not getattr(action, 'do_not_deliver', False):
                deliver = lambda: expander.expand_and_deliver(pending_notification)
                if kwargs.get('defer', True):
                    defer(deliver)
                else:
                    deliver()
            return pending_notification
        setattr(Actions, action_name, action)


for action_name, arg_names in Actions.ACTIONS.iteritems():
    Actions._create_action(action_name, arg_names)

