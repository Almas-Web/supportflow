from datetime import timedelta
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from organizations.models import Membership, Organization
from tickets.models import Ticket
from customers.models import Customer
from teams.models import Team, TeamMember
from .models import SLAPolicy, TicketSLA
User = get_user_model()
class SLATests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="sla_owner", email="sla_owner@example.com", password="Password123")
        self.admin = User.objects.create_user(username="sla_admin", email="sla_admin@example.com", password="Password123")
        self.agent = User.objects.create_user(username="sla_agent", email="sla_agent@example.com", password="Password123")
        self.customer_user = User.objects.create_user(username="sla_customer", email="sla_customer@example.com", password="Password123")
        self.outsider = User.objects.create_user(username="sla_outsider", email="sla_outsider@example.com", password="Password123")
        self.organization = Organization.objects.create(name="SLA Org", slug="sla-org", owner=self.owner)
        Membership.objects.create(organization=self.organization, user=self.owner, role=Membership.OWNER)
        Membership.objects.create(organization=self.organization, user=self.admin, role=Membership.ADMIN)
        Membership.objects.create(organization=self.organization, user=self.agent, role=Membership.AGENT)
        Membership.objects.create(organization=self.organization, user=self.customer_user, role=Membership.CUSTOMER)
        self.customer = Customer.objects.create(user=self.customer_user, organization=self.organization, company_name="SLA Customer")
        self.team = Team.objects.create(organization=self.organization, name="SLA Team", slug="sla-team", lead=self.agent)
        TeamMember.objects.create(team=self.team, user=self.agent, is_active=True)
        self.other_organization = Organization.objects.create(name="Other SLA Org", slug="other-sla-org", owner=self.outsider)
        Membership.objects.create(organization=self.other_organization, user=self.outsider, role=Membership.OWNER)
        self.policy = SLAPolicy.objects.create(organization=self.organization, name="High Priority SLA", description="High priority support SLA", priority=Ticket.HIGH, first_response_minutes=30, resolution_minutes=240)
        self.ticket = Ticket.objects.create(organization=self.organization, customer=self.customer, team=self.team, agent=self.agent, title="SLA Ticket", description="SLA test ticket", category=Ticket.TECHNICAL, priority=Ticket.HIGH)
        self.first_response_due_at = timezone.now() + timedelta(minutes=30)
        self.resolution_due_at = timezone.now() + timedelta(minutes=240)
        self.ticket_sla = TicketSLA.objects.create(ticket=self.ticket, policy=self.policy, first_response_due_at=self.first_response_due_at, resolution_due_at=self.resolution_due_at)
        self.policy_list_url = reverse("sla-policy-list-create", kwargs={"organization_id": self.organization.id})
        self.ticket_sla_list_url = reverse("ticket-sla-list-create", kwargs={"organization_id": self.organization.id})
    def authenticate(self, user):
        self.client.force_authenticate(user=user)
    def test_unauthenticated_user_cannot_list_policies(self):
        response = self.client.get(self.policy_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    def test_owner_can_list_policies(self):
        self.authenticate(self.owner)
        response = self.client.get(self.policy_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_agent_can_list_policies(self):
        self.authenticate(self.agent)
        response = self.client.get(self.policy_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_customer_can_list_policies(self):
        self.authenticate(self.customer_user)
        response = self.client.get(self.policy_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_owner_can_create_policy(self):
        self.authenticate(self.owner)
        response = self.client.post(self.policy_list_url, {"organization": self.organization.id, "name": "Urgent SLA", "description": "Urgent support", "priority": Ticket.URGENT, "first_response_minutes": 15, "resolution_minutes": 120}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    def test_admin_can_create_policy(self):
        self.authenticate(self.admin)
        response = self.client.post(self.policy_list_url, {"organization": self.organization.id, "name": "Medium SLA", "description": "Medium support", "priority": Ticket.MEDIUM, "first_response_minutes": 60, "resolution_minutes": 480}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    def test_agent_cannot_create_policy(self):
        self.authenticate(self.agent)
        response = self.client.post(self.policy_list_url, {"organization": self.organization.id, "name": "Agent SLA", "priority": Ticket.LOW, "first_response_minutes": 60, "resolution_minutes": 480}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    def test_customer_cannot_create_policy(self):
        self.authenticate(self.customer_user)
        response = self.client.post(self.policy_list_url, {"organization": self.organization.id, "name": "Customer SLA", "priority": Ticket.LOW, "first_response_minutes": 60, "resolution_minutes": 480}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    def test_owner_can_update_policy(self):
        self.authenticate(self.owner)
        url = reverse("sla-policy-detail", kwargs={"organization_id": self.organization.id, "pk": self.policy.id})
        response = self.client.patch(url, {"first_response_minutes": 20}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_admin_can_update_policy(self):
        self.authenticate(self.admin)
        url = reverse("sla-policy-detail", kwargs={"organization_id": self.organization.id, "pk": self.policy.id})
        response = self.client.patch(url, {"resolution_minutes": 300}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_agent_cannot_update_policy(self):
        self.authenticate(self.agent)
        url = reverse("sla-policy-detail", kwargs={"organization_id": self.organization.id, "pk": self.policy.id})
        response = self.client.patch(url, {"resolution_minutes": 300}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    def test_owner_can_delete_policy(self):
        self.authenticate(self.owner)
        policy = SLAPolicy.objects.create(organization=self.organization, name="Delete SLA", priority=Ticket.LOW, first_response_minutes=60, resolution_minutes=480)
        url = reverse("sla-policy-detail", kwargs={"organization_id": self.organization.id, "pk": policy.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    def test_agent_cannot_delete_policy(self):
        self.authenticate(self.agent)
        url = reverse("sla-policy-detail", kwargs={"organization_id": self.organization.id, "pk": self.policy.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    def test_cross_organization_policy_access_is_blocked(self):
        self.authenticate(self.outsider)
        url = reverse("sla-policy-list-create", kwargs={"organization_id": self.organization.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    def test_owner_can_list_ticket_slas(self):
        self.authenticate(self.owner)
        response = self.client.get(self.ticket_sla_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_agent_can_list_ticket_slas(self):
        self.authenticate(self.agent)
        response = self.client.get(self.ticket_sla_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_owner_can_create_ticket_sla(self):
        ticket = Ticket.objects.create(organization=self.organization, customer=self.customer, team=self.team, agent=self.agent, title="Second SLA Ticket", description="Second ticket", category=Ticket.TECHNICAL, priority=Ticket.HIGH)
        self.authenticate(self.owner)
        response = self.client.post(self.ticket_sla_list_url, {"ticket": ticket.id, "policy": self.policy.id, "first_response_due_at": timezone.now().isoformat(), "resolution_due_at": (timezone.now() + timedelta(hours=4)).isoformat(), "status": TicketSLA.ON_TRACK}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    def test_agent_cannot_create_ticket_sla(self):
        ticket = Ticket.objects.create(organization=self.organization, customer=self.customer, team=self.team, agent=self.agent, title="Agent SLA Ticket", description="Agent ticket", category=Ticket.TECHNICAL, priority=Ticket.HIGH)
        self.authenticate(self.agent)
        response = self.client.post(self.ticket_sla_list_url, {"ticket": ticket.id, "policy": self.policy.id, "first_response_due_at": timezone.now().isoformat(), "resolution_due_at": (timezone.now() + timedelta(hours=4)).isoformat()}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    def test_customer_cannot_create_ticket_sla(self):
        ticket = Ticket.objects.create(organization=self.organization, customer=self.customer, title="Customer SLA Ticket", description="Customer ticket", category=Ticket.GENERAL, priority=Ticket.HIGH)
        self.authenticate(self.customer_user)
        response = self.client.post(self.ticket_sla_list_url, {"ticket": ticket.id, "policy": self.policy.id, "first_response_due_at": timezone.now().isoformat(), "resolution_due_at": (timezone.now() + timedelta(hours=4)).isoformat()}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    def test_ticket_sla_priority_must_match_policy(self):
        low_policy = SLAPolicy.objects.create(organization=self.organization, name="Low SLA", priority=Ticket.LOW, first_response_minutes=60, resolution_minutes=480)
        ticket = Ticket.objects.create(organization=self.organization, customer=self.customer, title="High Ticket", description="Priority mismatch", category=Ticket.TECHNICAL, priority=Ticket.HIGH)
        self.authenticate(self.owner)
        response = self.client.post(self.ticket_sla_list_url, {"ticket": ticket.id, "policy": low_policy.id, "first_response_due_at": timezone.now().isoformat(), "resolution_due_at": (timezone.now() + timedelta(hours=4)).isoformat()}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    def test_ticket_sla_cross_organization_access_is_blocked(self):
        self.authenticate(self.outsider)
        url = reverse("ticket-sla-list-create", kwargs={"organization_id": self.organization.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    def test_ticket_sla_detail_can_be_retrieved(self):
        self.authenticate(self.agent)
        url = reverse("ticket-sla-detail", kwargs={"organization_id": self.organization.id, "pk": self.ticket_sla.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["ticket"], self.ticket.id)
    def test_owner_can_update_ticket_sla(self):
        self.authenticate(self.owner)
        url = reverse("ticket-sla-detail", kwargs={"organization_id": self.organization.id, "pk": self.ticket_sla.id})
        response = self.client.patch(url, {"status": TicketSLA.PAUSED}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_agent_cannot_update_ticket_sla(self):
        self.authenticate(self.agent)
        url = reverse("ticket-sla-detail", kwargs={"organization_id": self.organization.id, "pk": self.ticket_sla.id})
        response = self.client.patch(url, {"status": TicketSLA.PAUSED}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    def test_owner_can_delete_ticket_sla(self):
        self.authenticate(self.owner)
        url = reverse("ticket-sla-detail", kwargs={"organization_id": self.organization.id, "pk": self.ticket_sla.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)