from drawquest.tests.tests_helpers import (CanvasTestCase, create_content, create_user, create_group,
                                           create_comment, create_staff, PASSWORD,
                                           create_quest, create_current_quest, create_quest_comment)
from canvas.exceptions import DeactivatedUserError
from services import Services, override_service
from drawquest.middleware import AppVersionMiddleware


class TestInactiveUsers(CanvasTestCase):
    def after_setUp(self):
        self.inactive_user = create_user()
        self.client = self.get_client(user=self.inactive_user)
        self.client.login(username=self.inactive_user.username, password=PASSWORD)
        self.inactive_user.is_active = False
        self.inactive_user.save()

    #def test_403(self):
    #    with self.assertRaises(DeactivatedUserError):
    #        self.api_post('/api/quests/archive', client=self.client)

    def test_app_version_in_user_agent(self):
        user_agent = 'DrawQuest/1.0.2 CFNetwork/609 Darwin/13.0.0'
        self.assertEqual(AppVersionMiddleware.get_version_from_user_agent(user_agent), '1.0.2')

        user_agent = 'DrawQuest-staging/1.0.2 CFNetwork/609 Darwin/13.0.0'
        self.assertEqual(AppVersionMiddleware.get_version_from_user_agent(user_agent), '1.0.2')

