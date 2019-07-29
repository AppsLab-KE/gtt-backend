from django.test import TestCase, Client
from django.contrib.auth import get_user_model

User = get_user_model()

class UsersTest(TestCase):

    def test_users(self):
        pass
