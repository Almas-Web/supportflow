from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from customers.models import Customer
from organizations.models import Membership, Organization
from teams.models import Team, TeamMember
from tickets.models import Ticket

from .models import Rating


User = get_user_model()


class RatingTests(APITestCase):
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

        self.customer = Customer.objects.create(
            user=self.customer_user,
            organization=self.organization,
            company_name="ABC Ltd",
        )

        self.team = Team.objects.create(
            organization=self.organization,
            name="Support Team",
            slug="support-team",
            lead=self.agent,
        )

        TeamMember.objects.create(
            team=self.team,
            user=self.agent,
            is_active=True,
        )

        self.ticket = Ticket.objects.create(
            organization=self.organization,
            customer=self.customer,
            team=self.team,
            agent=self.agent,
            title="Login problem",
            description="Customer cannot login",
            category=Ticket.TECHNICAL,
            priority=Ticket.HIGH,
            status=Ticket.RESOLVED,
        )

        self.other_organization = Organization.objects.create(
            name="Other Org",
            slug="other-org",
            owner=self.outsider,
        )

        Membership.objects.create(
            organization=self.other_organization,
            user=self.outsider,
            role=Membership.OWNER,
        )

        self.rating_list_url = reverse(
            "rating-list-create",
            kwargs={"organization_id": self.organization.id},
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def create_rating(self):
        return Rating.objects.create(
            organization=self.organization,
            ticket=self.ticket,
            customer=self.customer,
            agent=self.agent,
            score=5,
            comment="Excellent support.",
        )

    def test_unauthenticated_user_cannot_list_ratings(self):
        response = self.client.get(self.rating_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_can_create_rating(self):
        self.authenticate(self.customer_user)

        response = self.client.post(
            self.rating_list_url,
            {
                "ticket": self.ticket.id,
                "score": 5,
                "comment": "Excellent support.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["score"], 5)

    def test_customer_cannot_rate_another_customers_ticket(self):
        other_user = User.objects.create_user(
            username="othercustomer",
            email="othercustomer@example.com",
            password="Password123",
        )

        other_customer = Customer.objects.create(
            user=other_user,
            organization=self.organization,
            company_name="Other Customer",
        )

        Membership.objects.create(
            organization=self.organization,
            user=other_user,
            role=Membership.CUSTOMER,
        )

        other_ticket = Ticket.objects.create(
            organization=self.organization,
            customer=other_customer,
            agent=self.agent,
            title="Other issue",
            description="Other customer issue",
            category=Ticket.GENERAL,
            priority=Ticket.MEDIUM,
            status=Ticket.RESOLVED,
        )

        self.authenticate(self.customer_user)

        response = self.client.post(
            self.rating_list_url,
            {
                "ticket": other_ticket.id,
                "score": 5,
                "comment": "Invalid rating.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_rate_ticket_from_another_organization(self):
        other_ticket = Ticket.objects.create(
            organization=self.other_organization,
            customer=Customer.objects.create(
                user=self.outsider,
                organization=self.other_organization,
                company_name="Other Customer",
            ),
            agent=self.outsider,
            title="Other organization issue",
            description="Other organization issue",
            category=Ticket.GENERAL,
            priority=Ticket.MEDIUM,
            status=Ticket.RESOLVED,
        )

        self.authenticate(self.customer_user)

        response = self.client.post(
            self.rating_list_url,
            {
                "ticket": other_ticket.id,
                "score": 5,
                "comment": "Invalid rating.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_agent_cannot_create_rating(self):
        self.authenticate(self.agent)

        response = self.client.post(
            self.rating_list_url,
            {
                "ticket": self.ticket.id,
                "score": 5,
                "comment": "Agent cannot rate.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_cannot_create_rating(self):
        self.authenticate(self.admin)

        response = self.client.post(
            self.rating_list_url,
            {
                "ticket": self.ticket.id,
                "score": 5,
                "comment": "Admin cannot rate.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_cannot_create_rating(self):
        self.authenticate(self.owner)

        response = self.client.post(
            self.rating_list_url,
            {
                "ticket": self.ticket.id,
                "score": 5,
                "comment": "Owner cannot rate.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_rating_score_cannot_be_less_than_one(self):
        self.authenticate(self.customer_user)

        response = self.client.post(
            self.rating_list_url,
            {
                "ticket": self.ticket.id,
                "score": 0,
                "comment": "Invalid score.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rating_score_cannot_be_greater_than_five(self):
        self.authenticate(self.customer_user)

        response = self.client.post(
            self.rating_list_url,
            {
                "ticket": self.ticket.id,
                "score": 6,
                "comment": "Invalid score.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unresolved_ticket_cannot_be_rated(self):
        self.ticket.status = Ticket.OPEN
        self.ticket.save()

        self.authenticate(self.customer_user)

        response = self.client.post(
            self.rating_list_url,
            {
                "ticket": self.ticket.id,
                "score": 5,
                "comment": "Ticket is not resolved.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_closed_ticket_can_be_rated(self):
        self.ticket.status = Ticket.CLOSED
        self.ticket.save()

        self.authenticate(self.customer_user)

        response = self.client.post(
            self.rating_list_url,
            {
                "ticket": self.ticket.id,
                "score": 4,
                "comment": "Good support.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_ticket_without_agent_cannot_be_rated(self):
        ticket = Ticket.objects.create(
            organization=self.organization,
            customer=self.customer,
            title="Unassigned issue",
            description="No agent assigned.",
            category=Ticket.GENERAL,
            priority=Ticket.MEDIUM,
            status=Ticket.RESOLVED,
        )

        self.authenticate(self.customer_user)

        response = self.client.post(
            self.rating_list_url,
            {
                "ticket": ticket.id,
                "score": 5,
                "comment": "No agent.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ticket_cannot_be_rated_twice(self):
        self.create_rating()
        self.authenticate(self.customer_user)

        response = self.client.post(
            self.rating_list_url,
            {
                "ticket": self.ticket.id,
                "score": 4,
                "comment": "Second rating.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_customer_can_list_ratings(self):
        self.create_rating()
        self.authenticate(self.customer_user)

        response = self.client.get(self.rating_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_agent_can_list_ratings(self):
        self.create_rating()
        self.authenticate(self.agent)

        response = self.client.get(self.rating_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_list_ratings(self):
        self.create_rating()
        self.authenticate(self.admin)

        response = self.client.get(self.rating_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_can_list_ratings(self):
        self.create_rating()
        self.authenticate(self.owner)

        response = self.client.get(self.rating_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cross_organization_rating_list_is_blocked(self):
        self.authenticate(self.owner)

        url = reverse(
            "rating-list-create",
            kwargs={"organization_id": self.other_organization.id},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_can_update_own_rating(self):
        rating = self.create_rating()
        self.authenticate(self.customer_user)

        url = reverse(
            "rating-detail",
            kwargs={
                "organization_id": self.organization.id,
                "pk": rating.id,
            },
        )

        response = self.client.patch(
            url,
            {
                "score": 4,
                "comment": "Updated feedback.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["score"], 4)

    def test_customer_can_delete_own_rating(self):
        rating = self.create_rating()
        self.authenticate(self.customer_user)

        url = reverse(
            "rating-detail",
            kwargs={
                "organization_id": self.organization.id,
                "pk": rating.id,
            },
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_agent_cannot_update_rating(self):
        rating = self.create_rating()
        self.authenticate(self.agent)

        url = reverse(
            "rating-detail",
            kwargs={
                "organization_id": self.organization.id,
                "pk": rating.id,
            },
        )

        response = self.client.patch(
            url,
            {
                "score": 3,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_agent_cannot_delete_rating(self):
        rating = self.create_rating()
        self.authenticate(self.agent)

        url = reverse(
            "rating-detail",
            kwargs={
                "organization_id": self.organization.id,
                "pk": rating.id,
            },
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)