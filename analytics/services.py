from django.db.models import Count
from django.utils import timezone
from tickets.models import Ticket
from .models import AnalyticsSnapshot

def generate_analytics_snapshot(organization):
    tickets = Ticket.objects.filter(organization=organization)
    total_tickets = tickets.count()
    open_tickets = tickets.filter(status=Ticket.OPEN).count()
    in_progress_tickets = tickets.filter(status=Ticket.IN_PROGRESS).count()
    waiting_customer_tickets = tickets.filter(status=Ticket.WAITING_CUSTOMER).count()
    resolved_tickets = tickets.filter(status=Ticket.RESOLVED).count()
    closed_tickets = tickets.filter(status=Ticket.CLOSED).count()
    urgent_tickets = tickets.filter(priority=Ticket.URGENT).count()
    high_priority_tickets = tickets.filter(priority=Ticket.HIGH).count()
    resolved_queryset = tickets.filter(resolved_at__isnull=False, created_at__isnull=False)
    average_resolution_minutes = None
    if resolved_queryset.exists():
        total_resolution_seconds = sum((ticket.resolved_at - ticket.created_at).total_seconds() for ticket in resolved_queryset)
        average_resolution_minutes = round(total_resolution_seconds / resolved_queryset.count() / 60, 2)
    tickets_by_category = dict(tickets.values("category").annotate(count=Count("id")).values_list("category", "count"))
    tickets_by_priority = dict(tickets.values("priority").annotate(count=Count("id")).values_list("priority", "count"))
    tickets_by_status = dict(tickets.values("status").annotate(count=Count("id")).values_list("status", "count"))
    tickets_by_team = {str(item["team_id"]): item["count"] for item in tickets.filter(team__isnull=False).values("team_id").annotate(count=Count("id"))}
    unassigned_count = tickets.filter(team__isnull=True).count()
    if unassigned_count:
        tickets_by_team["unassigned"] = unassigned_count
    snapshot, created = AnalyticsSnapshot.objects.update_or_create(organization=organization, date=timezone.localdate(), defaults={"total_tickets": total_tickets, "open_tickets": open_tickets, "in_progress_tickets": in_progress_tickets, "waiting_customer_tickets": waiting_customer_tickets, "resolved_tickets": resolved_tickets, "closed_tickets": closed_tickets, "urgent_tickets": urgent_tickets, "high_priority_tickets": high_priority_tickets, "average_resolution_minutes": average_resolution_minutes, "tickets_by_category": tickets_by_category, "tickets_by_priority": tickets_by_priority, "tickets_by_status": tickets_by_status, "tickets_by_team": tickets_by_team})
    return snapshot