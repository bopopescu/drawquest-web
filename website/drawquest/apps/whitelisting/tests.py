import time

from django.conf import settings

from drawquest.tests.tests_helpers import (CanvasTestCase, create_content, create_user, create_group,
                                           create_comment, create_staff, create_quest, create_quest_comment,
                                           create_current_quest)
from canvas.redis_models import redis
from services import Services, override_service
from drawquest.apps.whitelisting.models import allow, deny, moderate


class TestWhitelisting(CanvasTestCase):
    def after_setUp(self):
        self.quest = create_current_quest()
        self.content = create_content()
        settings.CACHE_KEY_PREFIX = 'DQv' + str(int(settings.CACHE_KEY_PREFIX[-1]) + 1)

    def _gallery(self):
        return self.api_post('/api/quests/comments', {'quest_id': self.quest.id})['comments']

    def _assert_not_in_gallery(self, comment):
        self.assertFalse(str(comment.id) in [str(c['id']) for c in self._gallery()])

    def _assert_in_gallery(self, comment):
        self.assertTrue(str(comment.id) in [str(c['id']) for c in self._gallery()])

    def test_unjudged(self):
        cmt = create_quest_comment(self.quest)
        self._assert_in_gallery(cmt)

    def test_allow(self):
        cmt = create_quest_comment(self.quest)
        self.api_post('/api/whitelisting/allow', {'comment_id': cmt.id}, user=create_staff())
        self._assert_in_gallery(cmt)

    def test_deny(self):
        cmt = create_quest_comment(self.quest)
        self.api_post('/api/whitelisting/deny', {'comment_id': cmt.id}, user=create_staff())
        self._assert_not_in_gallery(cmt)

    def test_deny_and_ban(self):
        cmt = create_quest_comment(self.quest)
        cmt2 = create_quest_comment(self.quest, author=cmt.author)
        self.api_post('/api/whitelisting/deny', {'comment_id': cmt.id, 'disable_author': True}, user=create_staff())
        self._assert_not_in_gallery(cmt)
        self._assert_not_in_gallery(cmt2)

    def test_rejudge(self):
        cmt = create_quest_comment(self.quest)
        self.api_post('/api/whitelisting/deny', {'comment_id': cmt.id}, user=create_staff())
        self._assert_not_in_gallery(cmt)

        self.api_post('/api/whitelisting/allow', {'comment_id': cmt.id}, user=create_staff())
        self._assert_in_gallery(cmt)

    def test_divvy(self):
        cmt = create_quest_comment(self.quest)
        cmt.id = 9001
        cmt.save()
        
        for mode in ['']:
            def divvy(from_, to):
                return self.get('/admin/staff/moderation{}/divvy/{}-{}'.format(mode, from_, to), user=create_staff()).content

            self.assertFalse(str(cmt.id) in divvy(2, 4))
            self.assertTrue(str(cmt.id) in divvy(0, 9))
            self.assertTrue(str(cmt.id) in divvy(0, 1))

