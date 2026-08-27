from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Membership, Organization

User = get_user_model()

class OrganizationAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="owner", email="owner@example.com", password="TestPassword123", is_verified=True)
        self.other_user = User.objects.create_user(username="other", email="other@example.com", password="TestPassword123", is_verified=True)
        self.organization = Organization.objects.create(name="SupportFlow", slug="supportflow", owner=self.user)
        Membership.objects.create(organization=self.organization, user=self.user, role=Membership.OWNER)
        self.list_url = reverse("organization-list-create")
        self.detail_url = reverse("organization-detail", kwargs={"pk": self.organization.pk})

    def test_unauthenticated_user_cannot_list_organizations(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_create_organization(self):
        response = self.client.post(self.list_url, {"name": "New Org", "slug": "new-org"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_create_organization(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_url, {"name": "New Org", "slug": "new-org"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        organization = Organization.objects.get(slug="new-org")
        self.assertEqual(organization.owner, self.user)
        self.assertTrue(Membership.objects.filter(organization=organization, user=self.user, role=Membership.OWNER).exists())

    def test_authenticated_user_can_list_own_organizations(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "SupportFlow")

    def test_member_can_see_organization(self):
        Membership.objects.create(organization=self.organization, user=self.other_user, role=Membership.AGENT)
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cannot_see_another_users_organization(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_update_another_users_organization(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(self.detail_url, {"name": "Hacked Organization"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.organization.refresh_from_db()
        self.assertEqual(self.organization.name, "SupportFlow")

    def test_owner_can_retrieve_organization(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "SupportFlow")

    def test_owner_can_update_organization(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.detail_url, {"name": "SupportFlow Updated"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.organization.refresh_from_db()
        self.assertEqual(self.organization.name, "SupportFlow Updated")

    def test_owner_is_read_only(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.detail_url, {"owner": self.other_user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.organization.refresh_from_db()
        self.assertEqual(self.organization.owner, self.user)

    def test_duplicate_slug_is_rejected(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_url, {"name": "Another Org", "slug": "supportflow"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_organization_name_is_rejected(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_url, {"name": "   ", "slug": "empty-org"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_inactive_membership_cannot_access_organization(self):
        Membership.objects.create(organization=self.organization, user=self.other_user, role=Membership.AGENT, is_active=False)
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_access_other_organization(self):
        other_organization = Organization.objects.create(name="Other Org", slug="other-org", owner=self.other_user)
        Membership.objects.create(organization=other_organization, user=self.other_user, role=Membership.OWNER)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("organization-detail", kwargs={"pk": other_organization.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_inactive_organization_cannot_be_accessed(self):
        self.organization.is_active = False
        self.organization.save(update_fields=["is_active"])
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)