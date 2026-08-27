from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from organizations.models import Membership, Organization
from .models import Team, TeamMember

User = get_user_model()

class TeamTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", email="owner@example.com", password="Password123")
        self.admin = User.objects.create_user(username="admin", email="admin@example.com", password="Password123")
        self.agent = User.objects.create_user(username="agent", email="agent@example.com", password="Password123")
        self.customer = User.objects.create_user(username="customer", email="customer@example.com", password="Password123")
        self.other_agent = User.objects.create_user(username="otheragent", email="otheragent@example.com", password="Password123")
        self.organization = Organization.objects.create(name="SupportFlow", slug="supportflow", owner=self.owner)
        Membership.objects.create(organization=self.organization, user=self.owner, role=Membership.OWNER)
        Membership.objects.create(organization=self.organization, user=self.admin, role=Membership.ADMIN)
        Membership.objects.create(organization=self.organization, user=self.agent, role=Membership.AGENT)
        Membership.objects.create(organization=self.organization, user=self.customer, role=Membership.CUSTOMER)
        self.other_organization = Organization.objects.create(name="Other Org", slug="other-org", owner=self.other_agent)
        Membership.objects.create(organization=self.other_organization, user=self.other_agent, role=Membership.OWNER)
        self.list_url = reverse("team-list-create", kwargs={"organization_id": self.organization.id})

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_unauthenticated_user_cannot_list_teams(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_can_create_team(self):
        self.authenticate(self.owner)
        response = self.client.post(self.list_url, {"name": "Support Team", "slug": "support-team", "description": "Customer support team", "lead": self.agent.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Team.objects.filter(organization=self.organization, slug="support-team").exists())

    def test_admin_can_create_team(self):
        self.authenticate(self.admin)
        response = self.client.post(self.list_url, {"name": "Sales Team", "slug": "sales-team", "lead": self.agent.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_agent_cannot_create_team(self):
        self.authenticate(self.agent)
        response = self.client.post(self.list_url, {"name": "Agent Team", "slug": "agent-team"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_create_team(self):
        self.authenticate(self.customer)
        response = self.client.post(self.list_url, {"name": "Customer Team", "slug": "customer-team"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_member_can_list_teams(self):
        Team.objects.create(organization=self.organization, name="Support Team", slug="support-team")
        self.authenticate(self.agent)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_customer_can_list_teams(self):
        Team.objects.create(organization=self.organization, name="Support Team", slug="support-team")
        self.authenticate(self.customer)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cross_organization_access_is_blocked(self):
        team = Team.objects.create(organization=self.other_organization, name="Other Team", slug="other-team")
        self.authenticate(self.owner)
        response = self.client.get(reverse("team-detail", kwargs={"organization_id": self.other_organization.id, "pk": team.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_inactive_organization_blocks_team_access(self):
        self.organization.is_active = False
        self.organization.save()
        self.authenticate(self.owner)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_lead_must_be_active_agent(self):
        self.authenticate(self.owner)
        response = self.client.post(self.list_url, {"name": "Invalid Team", "slug": "invalid-team", "lead": self.customer.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_team_slug_must_be_unique_inside_organization(self):
        Team.objects.create(organization=self.organization, name="Support Team", slug="support-team")
        self.authenticate(self.owner)
        response = self.client.post(self.list_url, {"name": "Another Support", "slug": "support-team"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_owner_can_update_team(self):
        team = Team.objects.create(organization=self.organization, name="Support Team", slug="support-team")
        self.authenticate(self.owner)
        response = self.client.patch(reverse("team-detail", kwargs={"organization_id": self.organization.id, "pk": team.id}), {"name": "Updated Team"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        team.refresh_from_db()
        self.assertEqual(team.name, "Updated Team")

    def test_agent_cannot_update_team(self):
        team = Team.objects.create(organization=self.organization, name="Support Team", slug="support-team")
        self.authenticate(self.agent)
        response = self.client.patch(reverse("team-detail", kwargs={"organization_id": self.organization.id, "pk": team.id}), {"name": "Updated Team"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete_team(self):
        team = Team.objects.create(organization=self.organization, name="Support Team", slug="support-team")
        self.authenticate(self.owner)
        response = self.client.delete(reverse("team-detail", kwargs={"organization_id": self.organization.id, "pk": team.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Team.objects.filter(id=team.id).exists())

    def test_agent_can_be_added_to_team(self):
        team = Team.objects.create(organization=self.organization, name="Support Team", slug="support-team")
        self.authenticate(self.admin)
        url = reverse("team-member-list-create", kwargs={"organization_id": self.organization.id, "team_id": team.id})
        response = self.client.post(url, {"user": self.agent.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(TeamMember.objects.filter(team=team, user=self.agent).exists())

    def test_customer_cannot_be_added_to_team(self):
        team = Team.objects.create(organization=self.organization, name="Support Team", slug="support-team")
        self.authenticate(self.admin)
        url = reverse("team-member-list-create", kwargs={"organization_id": self.organization.id, "team_id": team.id})
        response = self.client.post(url, {"user": self.customer.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_other_organization_agent_cannot_be_added(self):
        team = Team.objects.create(organization=self.organization, name="Support Team", slug="support-team")
        self.authenticate(self.owner)
        url = reverse("team-member-list-create", kwargs={"organization_id": self.organization.id, "team_id": team.id})
        response = self.client.post(url, {"user": self.other_agent.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_agent_cannot_manage_team_members(self):
        team = Team.objects.create(organization=self.organization, name="Support Team", slug="support-team")
        self.authenticate(self.agent)
        url = reverse("team-member-list-create", kwargs={"organization_id": self.organization.id, "team_id": team.id})
        response = self.client.post(url, {"user": self.agent.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_duplicate_team_member_is_blocked(self):
        team = Team.objects.create(organization=self.organization, name="Support Team", slug="support-team")
        TeamMember.objects.create(team=team, user=self.agent)
        self.authenticate(self.admin)
        url = reverse("team-member-list-create", kwargs={"organization_id": self.organization.id, "team_id": team.id})
        response = self.client.post(url, {"user": self.agent.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_team_member_list_requires_organization_membership(self):
        team = Team.objects.create(organization=self.organization, name="Support Team", slug="support-team")
        TeamMember.objects.create(team=team, user=self.agent)
        self.authenticate(self.other_agent)
        url = reverse("team-member-list-create", kwargs={"organization_id": self.organization.id, "team_id": team.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)