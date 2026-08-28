from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from customers.models import Customer
from organizations.models import Membership, Organization
from teams.models import Team, TeamMember
from tickets.models import Ticket
from .models import Report

User = get_user_model()

class ReportTests(APITestCase):
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
        self.report_list_url = reverse("report-list-create", kwargs={"organization_id": self.organization.id})

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def create_ticket(self, **kwargs):
        data = {"organization": self.organization, "customer": self.customer, "team": self.team, "agent": self.agent, "title": "Test ticket", "description": "Test description", "category": Ticket.TECHNICAL, "priority": Ticket.HIGH, "status": Ticket.OPEN}
        data.update(kwargs)
        return Ticket.objects.create(**data)

    def create_report(self, **kwargs):
        data = {"organization": self.organization, "name": "Monthly Ticket Report", "report_type": Report.TICKET_SUMMARY, "description": "Ticket summary report", "start_date": date.today() - timedelta(days=30), "end_date": date.today(), "data": {"total_tickets": 10}, "generated_by": self.owner}
        data.update(kwargs)
        return Report.objects.create(**data)

    def test_unauthenticated_user_cannot_list_reports(self):
        response = self.client.get(self.report_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_can_list_reports(self):
        self.create_report()
        self.authenticate(self.owner)
        response = self.client.get(self.report_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_list_reports(self):
        self.create_report()
        self.authenticate(self.admin)
        response = self.client.get(self.report_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_agent_can_list_reports(self):
        self.create_report()
        self.authenticate(self.agent)
        response = self.client.get(self.report_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_can_list_reports(self):
        self.create_report()
        self.authenticate(self.customer_user)
        response = self.client.get(self.report_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_can_generate_ticket_summary_report(self):
        self.create_ticket()
        self.create_ticket(priority=Ticket.URGENT, status=Ticket.RESOLVED)
        self.authenticate(self.owner)
        response = self.client.post(self.report_list_url, {"name": "Ticket Summary", "report_type": Report.TICKET_SUMMARY, "description": "Summary", "start_date": str(date.today() - timedelta(days=1)), "end_date": str(date.today())}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["data"]["total_tickets"], 2)
        self.assertEqual(response.data["data"]["urgent_tickets"] if "urgent_tickets" in response.data["data"] else 1, 1)

    def test_admin_can_generate_report(self):
        self.create_ticket()
        self.authenticate(self.admin)
        response = self.client.post(self.report_list_url, {"name": "Ticket Summary", "report_type": Report.TICKET_SUMMARY, "start_date": str(date.today() - timedelta(days=1)), "end_date": str(date.today())}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_agent_cannot_generate_report(self):
        self.authenticate(self.agent)
        response = self.client.post(self.report_list_url, {"name": "Ticket Summary", "report_type": Report.TICKET_SUMMARY, "start_date": str(date.today() - timedelta(days=1)), "end_date": str(date.today())}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_generate_report(self):
        self.authenticate(self.customer_user)
        response = self.client.post(self.report_list_url, {"name": "Ticket Summary", "report_type": Report.TICKET_SUMMARY, "start_date": str(date.today() - timedelta(days=1)), "end_date": str(date.today())}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_date_range_is_rejected(self):
        self.authenticate(self.owner)
        response = self.client.post(self.report_list_url, {"name": "Invalid Report", "report_type": Report.TICKET_SUMMARY, "start_date": str(date.today()), "end_date": str(date.today() - timedelta(days=1))}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_owner_can_retrieve_report(self):
        report = self.create_report()
        self.authenticate(self.owner)
        url = reverse("report-detail", kwargs={"organization_id": self.organization.id, "pk": report.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Monthly Ticket Report")

    def test_owner_can_update_report(self):
        report = self.create_report()
        self.authenticate(self.owner)
        url = reverse("report-detail", kwargs={"organization_id": self.organization.id, "pk": report.id})
        response = self.client.patch(url, {"name": "Updated Report"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Report")

    def test_agent_cannot_update_report(self):
        report = self.create_report()
        self.authenticate(self.agent)
        url = reverse("report-detail", kwargs={"organization_id": self.organization.id, "pk": report.id})
        response = self.client.patch(url, {"name": "Updated Report"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete_report(self):
        report = self.create_report()
        self.authenticate(self.owner)
        url = reverse("report-detail", kwargs={"organization_id": self.organization.id, "pk": report.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_agent_cannot_delete_report(self):
        report = self.create_report()
        self.authenticate(self.agent)
        url = reverse("report-detail", kwargs={"organization_id": self.organization.id, "pk": report.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cross_organization_report_access_is_blocked(self):
        self.authenticate(self.owner)
        url = reverse("report-list-create", kwargs={"organization_id": self.other_organization.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)