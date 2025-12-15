from django.test import TestCase
from django.utils.timezone import is_aware
from user.models import User


class UserModelTest(TestCase):
    def setUp(self):
        """
        Create a test user instance for use in all test methods.
        """
        self.user = User.objects.create(
            email="testuser@example.com",
            password="securepassword123",
            firstname="Test",
            lastname="User",
            phone="1234567890",
            role="Initiator",  # Ensure ROLE_OPTIONS has this role
            verified=False,
        )

    def test_user_creation(self):
        """
        Test a User instance is created properly.
        """
        self.assertEqual(self.user.email, "testuser@example.com")
        self.assertEqual(self.user.firstname, "Test")
        self.assertEqual(self.user.lastname, "User")
        self.assertEqual(self.user.phone, "1234567890")
        self.assertEqual(self.user.role, "Initiator")
        self.assertFalse(self.user.is_staff)  # Default value
        self.assertTrue(self.user.is_active)  # Default value
        self.assertFalse(self.user.verified)  # Default value

    def test_user_string_representation(self):
        """
        Test the __str__ method of the User model.
        """
        self.assertEqual(str(self.user), self.user.email)

    def test_user_fullname_property(self):
        """
        Test the 'fullname' property of the User model.
        """
        self.assertEqual(self.user.fullname, "Test User")

    def test_user_last_login(self):
        """
        Test the 'save_last_login' custom method.
        """
        self.user.save_last_login()

        # Check if last_login is updated and timezone-aware
        self.assertIsNotNone(self.user.last_login)
        self.assertTrue(is_aware(self.user.last_login))

    def test_user_verify_user_method(self):
        """
        Test the 'verify_user' custom method.
        """
        self.user.verify_user()

        # Check if the verified flag is set to True
        self.assertTrue(self.user.verified)

    def test_created_at_and_updated_at(self):
        """
        Test 'created_at' and 'updated_at' auto fields.
        """
        # The 'created_at' should not be None after creation
        self.assertIsNotNone(self.user.created_at)
        # Capture 'updated_at' before saving
        old_updated_at = self.user.updated_at
        # Save the user again to update the 'updated_at' field
        self.user.save()
        self.assertNotEqual(self.user.updated_at, old_updated_at)

    def test_user_with_null_fields(self):
        """
        Test creating a user with nullable and blank fields.
        """
        user = User.objects.create(
            email="nullfields@example.com",
            firstname="Nullable",
            lastname="Fields",
            role="Admin",
            phone=None,  # This should be allowed
            image=None,  # This should be allowed
            transaction_pin=None,  # This should be allowed
        )

        self.assertEqual(user.phone, None)
        self.assertEqual(user.image, None)
        self.assertEqual(user.transaction_pin, None)

    def test_user_role_field(self):
        """
        Test the 'role' field choices.
        """
        with self.assertRaises(ValueError):
            # Assuming ROLE_OPTIONS doesn't include an invalid value like "invalid_role"
            User.objects.create(
                email="invalidrole@example.com",
                password="password123",
                role="invalid_role",  # Invalid choice
            )

    def test_user_creation_by_other_user(self):
        """
        Test the 'created_by' field by assigning another user.
        """
        admin_user = User.objects.create(
            email="admin@example.com",
            password="adminpassword",
            firstname="Admin",
            lastname="User",
            role="Admin",
        )
        # Assign admin_user as the creator of another user
        user = User.objects.create(
            email="createdbyuser@example.com",
            password="password",
            firstname="Created",
            lastname="ByAdmin",
            role="Initiator",
            created_by=admin_user,
        )

        self.assertEqual(user.created_by, admin_user)
