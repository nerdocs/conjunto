from django.test import TestCase

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from conjunto.tools import create_groups_permissions

# noinspection PyPep8Naming
User = get_user_model()

TEST_GROUP_NAME = "Test group 234"


class GroupPermissionsTest(TestCase):
    def setUp(self) -> None:
        self.group = Group(name=TEST_GROUP_NAME)
        self.group.save()

        self.user = User.objects.create_user(username="demo_user", password="foo")
        self.user.groups.add(self.group)

    def test_check_user_in_group(self):
        groups = self.user.groups
        filtered = groups.filter(name=self.group)
        self.assertTrue(filtered.exists())
        # assert demo_user.groups.filter(name=group).exists()

    def test_add_permissions_to_group_with_user_as_model(self):
        groups_permissions = {TEST_GROUP_NAME: {User: ["add", "view"]}}
        create_groups_permissions(groups_permissions)
        self.assertEqual(len(self.group.permissions.filter(codename="view_user")), 1)
        self.assertTrue(self.group.permissions.filter(codename="view_user").exists())
        self.assertTrue(self.group.permissions.filter(codename="add_user").exists())

    def test_add_permissions_to_group_with_user_as_dotted_string(self):
        groups_permissions = {TEST_GROUP_NAME: {"auth.User": ["add", "view"]}}
        create_groups_permissions(groups_permissions)
        self.assertTrue(self.group.permissions.filter(codename="view_user").exists())
        self.assertTrue(self.group.permissions.filter(codename="add_user").exists())
