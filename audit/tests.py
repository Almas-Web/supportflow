from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from organizations.models import Membership, Organization
from .models import AuditLog

User = get_user_model()

class AuditLogTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", email="owner@example.com", password="Password123")
        self.admin = User.objects.create_user(username="admin", email="admin@example.com", password="Password123")
        self.agent = User.objects.create_user(username="agent", email="agent@example.com", password="Password123")
        self.customer = User.objects.create_user(username="customer", email="customer@example.com", password="Password123")
        self.outsider = User.objects.create_user(username="outsider", email="outsider@example.com", password="Password123")
        self.organization = Organization.objects.create(name="SupportFlow", slug="supportflow", owner=self.owner)
        Membership.objects.create(organization=self.organization, user=self.owner, role=Membership.OWNER)
        Membership.objects.create(organization=self.organization, user=self.admin, role=Membership.ADMIN)
        Membership.objects.create(organization=self.organization, user=self.agent, role=Membership.AGENT)
        Membership.objects.create(organization=self.organization, user=self.customer, role=Membership.CUSTOMER)
        self.other_organization = Organization.objects.create(name="Other Org", slug="other-org", owner=self.outsider)
        Membership.objects.create(organization=self.other_organization, user=self.outsider, role=Membership.OWNER)
        self.audit_log = AuditLog.objects.create(organization=self.organization, user=self.owner, action=AuditLog.CREATE, model_name="Ticket", object_id=1, description="Created ticket", changes={"title": "Login issue"})
        self.list_url = reverse("audit-log-list", kwargs={"organization_id": self.organization.id})

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_unauthenticated_user_cannot_list_audit_logs(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_can_list_audit_logs(self):
        self.authenticate(self.owner)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_admin_can_list_audit_logs(self):
        self.authenticate(self.admin)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_agent_can_list_audit_logs(self):
        self.authenticate(self.agent)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_can_list_audit_logs(self):
        self.authenticate(self.customer)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_outsider_cannot_list_audit_logs(self):
        self.authenticate(self.outsider)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_retrieve_audit_log(self):
        self.authenticate(self.owner)
        url = reverse("audit-log-detail", kwargs={"organization_id": self.organization.id, "pk": self.audit_log.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["action"], AuditLog.CREATE)

    def test_admin_can_retrieve_audit_log(self):
        self.authenticate(self.admin)
        url = reverse("audit-log-detail", kwargs={"organization_id": self.organization.id, "pk": self.audit_log.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_agent_can_retrieve_audit_log(self):
        self.authenticate(self.agent)
        url = reverse("audit-log-detail", kwargs={"organization_id": self.organization.id, "pk": self.audit_log.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_can_retrieve_audit_log(self):
        self.authenticate(self.customer)
        url = reverse("audit-log-detail", kwargs={"organization_id": self.organization.id, "pk": self.audit_log.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_outsider_cannot_retrieve_audit_log(self):
        self.authenticate(self.outsider)
        url = reverse("audit-log-detail", kwargs={"organization_id": self.organization.id, "pk": self.audit_log.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_audit_log_cannot_be_created_through_api(self):
        self.authenticate(self.owner)
        response = self.client.post(self.list_url, {"organization": self.organization.id, "user": self.owner.id, "action": AuditLog.CREATE, "model_name": "Ticket", "object_id": 2, "description": "Created ticket", "changes": {}}, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_audit_log_cannot_be_updated_through_api(self):
        self.authenticate(self.owner)
        url = reverse("audit-log-detail", kwargs={"organization_id": self.organization.id, "pk": self.audit_log.id})
        response = self.client.patch(url, {"description": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_audit_log_cannot_be_deleted_through_api(self):
        self.authenticate(self.owner)
        url = reverse("audit-log-detail", kwargs={"organization_id": self.organization.id, "pk": self.audit_log.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        