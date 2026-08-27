from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AccountTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPassword123",
            role=User.CUSTOMER,
            is_verified=True,
        )

    def test_signup(self):
        response = self.client.post(reverse("signup"), {
            "username": "newuser",
            "email": "new@example.com",
            "password": "TestPassword123",
            "role": User.CUSTOMER,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login(self):
        response = self.client.post(reverse("login"), {
            "email": "test@example.com",
            "password": "TestPassword123",
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)
        self.assertIn("refresh_token", response.data)

    def test_login_unverified_user(self):
        self.user.is_verified = False
        self.user.save(update_fields=["is_verified"])

        response = self.client.post(reverse("login"), {
            "email": "test@example.com",
            "password": "TestPassword123",
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_login(self):
        response = self.client.post(reverse("login"), {
            "email": "test@example.com",
            "password": "WrongPassword",
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_requires_authentication(self):
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile_update(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(reverse("profile"), {
            "bio": "SupportFlow customer",
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.bio, "SupportFlow customer")