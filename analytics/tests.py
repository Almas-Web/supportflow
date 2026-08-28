from datetime import date
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from customers.models import Customer
from organizations.models import Membership, Organization
from teams.models import Team, TeamMember
from tickets.models import Ticket
from .models import AnalyticsSnapshot

User = get_user_model()

class AnalyticsTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", email="owner@example.com", password="Password123")
        self.admin = User.objects.create_user(username="admin", email="admin@example.com", password="Password123")
        self.agent = User.objects.create_user(username="agent", email="agent@example.com", password="Password123")
        self.customer_user = User.objects.create_user(username="customer", email="customer@example.com", password="Password123")
        self.outsider = User.objects.create_user(username="outsider", email="outsider@example.com", password="Password123")
        self.organization = Organization.objects.create(name="SupportFlow", slug="supportflow", owner=self.owner)
        Membership.objects.create(organization=self.organization, user=self.owner, role=Membership.OWNER)
        Membership.objects.create(organization=self.organization, user=self.admin, role=Membership.ADMIN)
        Membership.objects.create(organization=self.organization, user=self.agent, role=Membership.AGENT)
        Membership.objects.create(organization=self.organization, user=self.customer_user, role=Membership.CUSTOMER)
        self.customer = Customer.objects.create(user=self.customer_user, organization=self.organization, company_name="ABC Ltd")
        self.team = Team.objects.create(organization=self.organization, name="Support Team", slug="support-team", lead=self.agent)
        TeamMember.objects.create(team=self.team, user=self.agent, is_active=True)
        self.other_organization = Organization.objects.create(name="Other Org", slug="other-org", owner=self.outsider)
        Membership.objects.create(organization=self.other_organization, user=self.outsider, role=Membership.OWNER)
        self.analytics_list_url = reverse("analytics-list-create", kwargs={"organization_id": self.organization.id})
        self.analytics_summary_url = reverse("analytics-summary", kwargs={"organization_id": self.organization.id})

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def create_ticket(self, **kwargs):
        data = {"organization": self.organization, "customer": self.customer, "team": self.team, "agent": self.agent, "title": "Login problem", "description": "Customer cannot login", "category": Ticket.TECHNICAL, "priority": Ticket.HIGH}
        data.update(kwargs)
        return Ticket.objects.create(**data)

    def create_snapshot(self, **kwargs):
        data = {"organization": self.organization, "date": date.today(), "total_tickets": 10, "open_tickets": 3, "in_progress_tickets": 2, "waiting_customer_tickets": 1, "resolved_tickets": 2, "closed_tickets": 2, "urgent_tickets": 1, "high_priority_tickets": 3, "average_resolution_minutes": 120.5, "tickets_by_category": {"GENERAL": 2, "TECHNICAL": 4, "BILLING": 2, "ACCOUNT": 1, "OTHER": 1}, "tickets_by_priority": {"LOW": 2, "MEDIUM": 4, "HIGH": 3, "URGENT": 1}, "tickets_by_status": {"OPEN": 3, "IN_PROGRESS": 2, "WAITING_CUSTOMER": 1, "RESOLVED": 2, "CLOSED": 2}, "tickets_by_team": {str(self.team.id): 10}}
        data.update(kwargs)
        return AnalyticsSnapshot.objects.create(**data)

    def test_unauthenticated_user_cannot_list_analytics(self):
        response = self.client.get(self.analytics_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_can_list_analytics(self):
        self.create_snapshot()
        self.authenticate(self.owner)
        response = self.client.get(self.analytics_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_list_analytics(self):
        self.create_snapshot()
        self.authenticate(self.admin)
        response = self.client.get(self.analytics_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_agent_can_list_analytics(self):
        self.create_snapshot()
        self.authenticate(self.agent)
        response = self.client.get(self.analytics_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_can_list_analytics(self):
        self.create_snapshot()
        self.authenticate(self.customer_user)
        response = self.client.get(self.analytics_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_can_create_analytics_snapshot(self):
        self.authenticate(self.owner)
        response = self.client.post(self.analytics_list_url, {"organization": self.organization.id, "date": str(date.today()), "total_tickets": 10, "open_tickets": 3, "in_progress_tickets": 2, "waiting_customer_tickets": 1, "resolved_tickets": 2, "closed_tickets": 2, "urgent_tickets": 1, "high_priority_tickets": 3, "average_resolution_minutes": 120.5, "tickets_by_category": {"TECHNICAL": 4}, "tickets_by_priority": {"HIGH": 3}, "tickets_by_status": {"OPEN": 3}, "tickets_by_team": {str(self.team.id): 10}}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_can_create_analytics_snapshot(self):
        self.authenticate(self.admin)
        response = self.client.post(self.analytics_list_url, {"organization": self.organization.id, "date": str(date.today()), "total_tickets": 5}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_agent_cannot_create_analytics_snapshot(self):
        self.authenticate(self.agent)
        response = self.client.post(self.analytics_list_url, {"organization": self.organization.id, "date": str(date.today()), "total_tickets": 5}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_create_analytics_snapshot(self):
        self.authenticate(self.customer_user)
        response = self.client.post(self.analytics_list_url, {"organization": self.organization.id, "date": str(date.today()), "total_tickets": 5}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_retrieve_analytics_snapshot(self):
        snapshot = self.create_snapshot()
        self.authenticate(self.owner)
        url = reverse("analytics-detail", kwargs={"organization_id": self.organization.id, "pk": snapshot.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_tickets"], 10)

    def test_owner_can_update_analytics_snapshot(self):
        snapshot = self.create_snapshot()
        self.authenticate(self.owner)
        url = reverse("analytics-detail", kwargs={"organization_id": self.organization.id, "pk": snapshot.id})
        response = self.client.patch(url, {"total_tickets": 20}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_tickets"], 20)

    def test_agent_cannot_update_analytics_snapshot(self):
        snapshot = self.create_snapshot()
        self.authenticate(self.agent)
        url = reverse("analytics-detail", kwargs={"organization_id": self.organization.id, "pk": snapshot.id})
        response = self.client.patch(url, {"total_tickets": 20}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete_analytics_snapshot(self):
        snapshot = self.create_snapshot()
        self.authenticate(self.owner)
        url = reverse("analytics-detail", kwargs={"organization_id": self.organization.id, "pk": snapshot.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_agent_cannot_delete_analytics_snapshot(self):
        snapshot = self.create_snapshot()
        self.authenticate(self.agent)
        url = reverse("analytics-detail", kwargs={"organization_id": self.organization.id, "pk": snapshot.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cross_organization_analytics_access_is_blocked(self):
        self.authenticate(self.owner)
        url = reverse("analytics-list-create", kwargs={"organization_id": self.other_organization.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_view_latest_analytics_summary(self):
        self.create_ticket()
        self.authenticate(self.owner)
        response = self.client.get(self.analytics_summary_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_tickets"], 1)
        self.assertEqual(response.data["high_priority_tickets"], 1)
        self.assertEqual(response.data["tickets_by_category"]["TECHNICAL"], 1)
        self.assertEqual(response.data["tickets_by_priority"]["HIGH"], 1)
        self.assertEqual(response.data["tickets_by_status"]["OPEN"], 1)

    def test_unauthenticated_user_cannot_view_analytics_summary(self):
        response = self.client.get(self.analytics_summary_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)