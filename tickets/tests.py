from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from customers.models import Customer
from organizations.models import Membership, Organization
from teams.models import Team, TeamMember
from .models import Ticket

User = get_user_model()

class TicketTests(APITestCase):
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
        self.list_url = reverse("ticket-list-create", kwargs={"organization_id": self.organization.id})

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def create_ticket(self, **kwargs):
        data = {"organization": self.organization, "customer": self.customer, "team": self.team, "agent": self.agent, "title": "Login problem", "description": "Customer cannot login", "category": Ticket.TECHNICAL, "priority": Ticket.HIGH}
        data.update(kwargs)
        return Ticket.objects.create(**data)

    def test_unauthenticated_user_cannot_list_tickets(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_can_create_ticket(self):
        self.authenticate(self.owner)
        response = self.client.post(self.list_url, {"organization": self.organization.id, "customer": self.customer.id, "team": self.team.id, "agent": self.agent.id, "title": "Login issue", "description": "Customer cannot login", "category": "TECHNICAL", "priority": "HIGH"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_can_create_ticket(self):
        self.authenticate(self.admin)
        response = self.client.post(self.list_url, {"organization": self.organization.id, "customer": self.customer.id, "team": self.team.id, "agent": self.agent.id, "title": "Billing issue", "description": "Billing problem", "category": "BILLING", "priority": "MEDIUM"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_agent_can_create_ticket(self):
        self.authenticate(self.agent)
        response = self.client.post(self.list_url, {"organization": self.organization.id, "customer": self.customer.id, "team": self.team.id, "agent": self.agent.id, "title": "Technical issue", "description": "Technical problem", "category": "TECHNICAL", "priority": "HIGH"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_customer_can_create_ticket(self):
        self.authenticate(self.customer_user)
        response = self.client.post(self.list_url, {"organization": self.organization.id, "customer": self.customer.id, "title": "My issue", "description": "I need help", "category": "GENERAL", "priority": "MEDIUM"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_owner_can_list_tickets(self):
        self.create_ticket()
        self.authenticate(self.owner)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_list_tickets(self):
        self.create_ticket()
        self.authenticate(self.admin)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_agent_can_list_tickets(self):
        self.create_ticket()
        self.authenticate(self.agent)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_can_list_tickets(self):
        self.create_ticket()
        self.authenticate(self.customer_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_ticket_detail_can_be_retrieved(self):
        ticket = self.create_ticket()
        self.authenticate(self.agent)
        url = reverse("ticket-detail", kwargs={"organization_id": self.organization.id, "pk": ticket.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["ticket_number"], ticket.ticket_number)

    def test_owner_can_update_ticket(self):
        ticket = self.create_ticket()
        self.authenticate(self.owner)
        url = reverse("ticket-detail", kwargs={"organization_id": self.organization.id, "pk": ticket.id})
        response = self.client.patch(url, {"priority": "URGENT"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_update_ticket(self):
        ticket = self.create_ticket()
        self.authenticate(self.admin)
        url = reverse("ticket-detail", kwargs={"organization_id": self.organization.id, "pk": ticket.id})
        response = self.client.patch(url, {"status": "IN_PROGRESS"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_agent_can_update_ticket(self):
        ticket = self.create_ticket()
        self.authenticate(self.agent)
        url = reverse("ticket-detail", kwargs={"organization_id": self.organization.id, "pk": ticket.id})
        response = self.client.patch(url, {"status": "IN_PROGRESS"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_can_update_ticket_without_agent_assignment(self):
        ticket = self.create_ticket()
        self.authenticate(self.customer_user)
        url = reverse("ticket-detail", kwargs={"organization_id": self.organization.id, "pk": ticket.id})
        response = self.client.patch(url, {"title": "Updated issue"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_cannot_assign_agent(self):
        ticket = self.create_ticket()
        self.authenticate(self.customer_user)
        url = reverse("ticket-detail", kwargs={"organization_id": self.organization.id, "pk": ticket.id})
        response = self.client.patch(url, {"agent": self.agent.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete_ticket(self):
        ticket = self.create_ticket()
        self.authenticate(self.owner)
        url = reverse("ticket-detail", kwargs={"organization_id": self.organization.id, "pk": ticket.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_can_delete_ticket(self):
        ticket = self.create_ticket()
        self.authenticate(self.admin)
        url = reverse("ticket-detail", kwargs={"organization_id": self.organization.id, "pk": ticket.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_agent_cannot_delete_ticket(self):
        ticket = self.create_ticket()
        self.authenticate(self.agent)
        url = reverse("ticket-detail", kwargs={"organization_id": self.organization.id, "pk": ticket.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cross_organization_ticket_access_is_blocked(self):
        self.authenticate(self.owner)
        url = reverse("ticket-list-create", kwargs={"organization_id": self.other_organization.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_customer_organization_is_blocked(self):
        other_customer = Customer.objects.create(user=self.outsider, organization=self.other_organization, company_name="Other Customer")
        self.authenticate(self.owner)
        response = self.client.post(self.list_url, {"organization": self.organization.id, "customer": other_customer.id, "title": "Invalid", "description": "Invalid customer", "category": "GENERAL", "priority": "LOW"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_agent_team_assignment_is_blocked(self):
        other_agent = User.objects.create_user(username="otheragent", email="otheragent@example.com", password="Password123")
        Membership.objects.create(organization=self.organization, user=other_agent, role=Membership.AGENT)
        self.authenticate(self.owner)
        response = self.client.post(self.list_url, {"organization": self.organization.id, "customer": self.customer.id, "team": self.team.id, "agent": other_agent.id, "title": "Invalid assignment", "description": "Agent is not team member", "category": "TECHNICAL", "priority": "HIGH"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ticket_number_is_generated(self):
        ticket = self.create_ticket()
        self.assertTrue(ticket.ticket_number.startswith("TKT-"))