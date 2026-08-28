from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from customers.models import Customer
from organizations.models import Membership, Organization
from tickets.models import Ticket
from .models import Notification

User = get_user_model()

class NotificationTests(APITestCase):
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
        self.ticket = Ticket.objects.create(organization=self.organization, customer=self.customer, title="Login problem", description="Customer cannot login", category=Ticket.TECHNICAL, priority=Ticket.HIGH)
        self.other_organization = Organization.objects.create(name="Other Org", slug="other-org", owner=self.outsider)
        Membership.objects.create(organization=self.other_organization, user=self.outsider, role=Membership.OWNER)
        self.notification = Notification.objects.create(user=self.agent, organization=self.organization, ticket=self.ticket, notification_type=Notification.TICKET_ASSIGNED, title="Ticket Assigned", message="A ticket has been assigned to you.")
        self.list_url = reverse("notification-list", kwargs={"organization_id": self.organization.id})

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_unauthenticated_user_cannot_list_notifications(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_list_notifications(self):
        Notification.objects.create(user=self.owner, organization=self.organization, title="Owner Notification", message="Test notification.")
        self.authenticate(self.owner)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_list_notifications(self):
        Notification.objects.create(user=self.admin, organization=self.organization, title="Admin Notification", message="Test notification.")
        self.authenticate(self.admin)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_agent_can_list_notifications(self):
        self.authenticate(self.agent)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_customer_can_list_notifications(self):
        Notification.objects.create(user=self.customer_user, organization=self.organization, title="Customer Notification", message="Test notification.")
        self.authenticate(self.customer_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_only_sees_own_notifications(self):
        Notification.objects.create(user=self.owner, organization=self.organization, title="Owner Notification", message="Private notification.")
        self.authenticate(self.agent)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["user"], self.agent.id)

    def test_notification_detail_can_be_retrieved(self):
        self.authenticate(self.agent)
        url = reverse("notification-detail", kwargs={"organization_id": self.organization.id, "pk": self.notification.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.notification.id)

    def test_user_cannot_retrieve_another_users_notification(self):
        owner_notification = Notification.objects.create(user=self.owner, organization=self.organization, title="Private", message="Owner only.")
        self.authenticate(self.agent)
        url = reverse("notification-detail", kwargs={"organization_id": self.organization.id, "pk": owner_notification.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_mark_notification_as_read(self):
        self.authenticate(self.agent)
        url = reverse("notification-mark-read", kwargs={"organization_id": self.organization.id, "pk": self.notification.id})
        response = self.client.patch(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)

    def test_mark_read_response_contains_read_status(self):
        self.authenticate(self.agent)
        url = reverse("notification-mark-read", kwargs={"organization_id": self.organization.id, "pk": self.notification.id})
        response = self.client.patch(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_read"])

    def test_user_cannot_mark_another_users_notification_as_read(self):
        owner_notification = Notification.objects.create(user=self.owner, organization=self.organization, title="Private", message="Owner only.")
        self.authenticate(self.agent)
        url = reverse("notification-mark-read", kwargs={"organization_id": self.organization.id, "pk": owner_notification.id})
        response = self.client.patch(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_mark_all_notifications_as_read(self):
        Notification.objects.create(user=self.agent, organization=self.organization, title="Second", message="Second notification.")
        self.authenticate(self.agent)
        url = reverse("notification-mark-all-read", kwargs={"organization_id": self.organization.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Notification.objects.filter(user=self.agent, organization=self.organization, is_read=False).count(), 0)

    def test_mark_all_read_does_not_affect_other_users(self):
        owner_notification = Notification.objects.create(user=self.owner, organization=self.organization, title="Owner", message="Owner notification.")
        self.authenticate(self.agent)
        url = reverse("notification-mark-all-read", kwargs={"organization_id": self.organization.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        owner_notification.refresh_from_db()
        self.assertFalse(owner_notification.is_read)

    def test_cross_organization_notification_list_is_blocked(self):
        self.authenticate(self.agent)
        url = reverse("notification-list", kwargs={"organization_id": self.other_organization.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cross_organization_notification_detail_is_blocked(self):
        other_notification = Notification.objects.create(user=self.outsider, organization=self.other_organization, title="Other", message="Other organization.")
        self.authenticate(self.agent)
        url = reverse("notification-detail", kwargs={"organization_id": self.other_organization.id, "pk": other_notification.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cross_organization_mark_read_is_blocked(self):
        other_notification = Notification.objects.create(user=self.outsider, organization=self.other_organization, title="Other", message="Other organization.")
        self.authenticate(self.agent)
        url = reverse("notification-mark-read", kwargs={"organization_id": self.other_organization.id, "pk": other_notification.id})
        response = self.client.patch(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cross_organization_mark_all_read_is_blocked(self):
        self.authenticate(self.agent)
        url = reverse("notification-mark-all-read", kwargs={"organization_id": self.other_organization.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_notification_belongs_to_correct_user(self):
        self.assertEqual(self.notification.user, self.agent)

    def test_notification_belongs_to_correct_organization(self):
        self.assertEqual(self.notification.organization, self.organization)

    def test_notification_can_be_created(self):
        notification = Notification.objects.create(user=self.owner, organization=self.organization, title="New Notification", message="New notification message.")
        self.assertEqual(notification.user, self.owner)
        self.assertFalse(notification.is_read)

    def test_notification_default_is_unread(self):
        self.assertFalse(self.notification.is_read)

    def test_notification_can_be_created_without_ticket(self):
        notification = Notification.objects.create(user=self.owner, organization=self.organization, notification_type=Notification.GENERAL, title="General", message="General notification.")
        self.assertIsNone(notification.ticket)

    def test_notification_ticket_relationship(self):
        self.assertEqual(self.notification.ticket, self.ticket)

    def test_notification_type_is_stored(self):
        self.assertEqual(self.notification.notification_type, Notification.TICKET_ASSIGNED)

    def test_notification_string_representation(self):
        self.assertEqual(str(self.notification), f"{self.agent.email} - Ticket Assigned")

    def test_read_notification_remains_read(self):
        self.notification.is_read = True
        self.notification.save()
        self.authenticate(self.agent)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)