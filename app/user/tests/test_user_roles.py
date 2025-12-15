from django.test import TestCase
from user.models import User


class UserRoleFieldTest(TestCase):
    def test_valid_roles(self):
        """
        Test creating users with each valid role.
        """
        valid_roles = ["Admin", "Initiator", "Verifier", "Approver"]

        for role in valid_roles:
            user = User.objects.create(
                email=f"test_{role.lower()}@example.com",
                password="securepassword123",
                firstname="Test",
                lastname=role,
                role=role,
            )
            self.assertEqual(user.role, role)

    def test_invalid_role(self):
        """
        Test creating a user with an invalid role raises an error.
        """
        with self.assertRaises(ValueError):
            User.objects.create(
                email="invalidrole@example.com",
                password="securepassword123",
                firstname="Invalid",
                lastname="Role",
                role="InvalidRole",  # Not in ROLE_OPTIONS
            )
