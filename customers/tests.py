from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from organizations.models import Membership, Organization
from .models import Customer

User = get_user_model()

class CustomerTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", email="owner@example.com", password="Password123")
        self.admin = User.objects.create_user(username="admin", email="admin@example.com", password="Password123")
        self.agent = User.objects.create_user(username="agent", email="agent@example.com", password="Password123")
        self.customer = User.objects.create_user(username="customer", email="customer@example.com", password="Password123")
        self.other_customer = User.objects.create_user(username="othercustomer", email="othercustomer@example.com", password="Password123")
        self.outsider = User.objects.create_user(username="outsider", email="outsider@example.com", password="Password123")
        self.organization = Organization.objects.create(name="SupportFlow", slug="supportflow", owner=self.owner)
        Membership.objects.create(organization=self.organization, user=self.owner, role=Membership.OWNER)
        Membership.objects.create(organization=self.organization, user=self.admin, role=Membership.ADMIN)
        Membership.objects.create(organization=self.organization, user=self.agent, role=Membership.AGENT)
        Membership.objects.create(organization=self.organization, user=self.customer, role=Membership.CUSTOMER)
        self.other_organization = Organization.objects.create(name="Other Org", slug="other-org", owner=self.other_customer)
        Membership.objects.create(organization=self.other_organization, user=self.other_customer, role=Membership.OWNER)
        self.list_url = reverse("customer-list-create", kwargs={"organization_id": self.organization.id})

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def create_customer(self, user=None, organization=None):
        return Customer.objects.create(user=user or self.customer, organization=organization or self.organization)

    def test_unauthenticated_user_cannot_list_customers(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_can_create_customer(self):
        self.authenticate(self.owner)
        response = self.client.post(self.list_url, {"user": self.customer.id, "company_name": "ABC Ltd", "phone": "01700000000", "address": "Barishal", "notes": "Important customer"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Customer.objects.filter(organization=self.organization, user=self.customer).exists())

    def test_admin_can_create_customer(self):
        self.authenticate(self.admin)
        response = self.client.post(self.list_url, {"user": self.customer.id, "company_name": "ABC Ltd"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_agent_cannot_create_customer(self):
        self.authenticate(self.agent)
        response = self.client.post(self.list_url, {"user": self.customer.id, "company_name": "ABC Ltd"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_create_customer(self):
        self.authenticate(self.customer)
        response = self.client.post(self.list_url, {"user": self.customer.id, "company_name": "ABC Ltd"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_list_customers(self):
        self.create_customer()
        self.authenticate(self.owner)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_admin_can_list_customers(self):
        self.create_customer()
        self.authenticate(self.admin)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_agent_can_list_customers(self):
        self.create_customer()
        self.authenticate(self.agent)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_can_list_customers(self):
        self.create_customer()
        self.authenticate(self.customer)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_detail_can_be_retrieved(self):
        customer = self.create_customer()
        self.authenticate(self.agent)
        url = reverse("customer-detail", kwargs={"organization_id": self.organization.id, "pk": customer.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], customer.id)

    def test_owner_can_update_customer(self):
        customer = self.create_customer()
        self.authenticate(self.owner)
        url = reverse("customer-detail", kwargs={"organization_id": self.organization.id, "pk": customer.id})
        response = self.client.patch(url, {"company_name": "Updated Company"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        customer.refresh_from_db()
        self.assertEqual(customer.company_name, "Updated Company")

    def test_admin_can_update_customer(self):
        customer = self.create_customer()
        self.authenticate(self.admin)
        url = reverse("customer-detail", kwargs={"organization_id": self.organization.id, "pk": customer.id})
        response = self.client.patch(url, {"phone": "01800000000"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_agent_cannot_update_customer(self):
        customer = self.create_customer()
        self.authenticate(self.agent)
        url = reverse("customer-detail", kwargs={"organization_id": self.organization.id, "pk": customer.id})
        response = self.client.patch(url, {"company_name": "Updated Company"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_update_customer(self):
        customer = self.create_customer()
        self.authenticate(self.customer)
        url = reverse("customer-detail", kwargs={"organization_id": self.organization.id, "pk": customer.id})
        response = self.client.patch(url, {"company_name": "Updated Company"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete_customer(self):
        customer = self.create_customer()
        self.authenticate(self.owner)
        url = reverse("customer-detail", kwargs={"organization_id": self.organization.id, "pk": customer.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Customer.objects.filter(id=customer.id).exists())

    def test_admin_can_delete_customer(self):
        customer = self.create_customer()
        self.authenticate(self.admin)
        url = reverse("customer-detail", kwargs={"organization_id": self.organization.id, "pk": customer.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_agent_cannot_delete_customer(self):
        customer = self.create_customer()
        self.authenticate(self.agent)
        url = reverse("customer-detail", kwargs={"organization_id": self.organization.id, "pk": customer.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cross_organization_customer_access_is_blocked(self):
        customer = self.create_customer(user=self.other_customer, organization=self.other_organization)
        self.authenticate(self.owner)
        url = reverse("customer-detail", kwargs={"organization_id": self.other_organization.id, "pk": customer.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_inactive_organization_blocks_customer_access(self):
        self.create_customer()
        self.organization.is_active = False
        self.organization.save()
        self.authenticate(self.owner)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_inactive_membership_blocks_customer_access(self):
        self.create_customer()
        membership = Membership.objects.get(organization=self.organization, user=self.agent)
        membership.is_active = False
        membership.save()
        self.authenticate(self.agent)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_duplicate_customer_is_blocked(self):
        self.create_customer()
        self.authenticate(self.owner)
        response = self.client.post(self.list_url, {"user": self.customer.id, "company_name": "Duplicate"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_customer_membership_cannot_create_customer_profile(self):
        self.authenticate(self.owner)
        response = self.client.post(self.list_url, {"user": self.agent.id, "company_name": "Invalid Customer"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)