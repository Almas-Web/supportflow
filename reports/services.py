from django.db.models import Count
from tickets.models import Ticket

def generate_ticket_summary(organization, start_date, end_date):
    tickets = Ticket.objects.filter(organization=organization, created_at__date__range=[start_date, end_date])
    return {"total_tickets": tickets.count(), "open_tickets": tickets.filter(status=Ticket.OPEN).count(), "in_progress_tickets": tickets.filter(status=Ticket.IN_PROGRESS).count(), "waiting_customer_tickets": tickets.filter(status=Ticket.WAITING_CUSTOMER).count(), "resolved_tickets": tickets.filter(status=Ticket.RESOLVED).count(), "closed_tickets": tickets.filter(status=Ticket.CLOSED).count(), "tickets_by_priority": dict(tickets.values("priority").annotate(count=Count("id")).values_list("priority", "count")), "tickets_by_category": dict(tickets.values("category").annotate(count=Count("id")).values_list("category", "count"))}

def generate_sla_performance(organization, start_date, end_date):
    from sla.models import TicketSLA
    sla_records = TicketSLA.objects.filter(ticket__organization=organization, created_at__date__range=[start_date, end_date])
    total = sla_records.count()
    breached = sla_records.filter(status=TicketSLA.BREACHED).count() if hasattr(TicketSLA, "BREACHED") else 0
    return {"total_sla_records": total, "breached_sla_records": breached, "compliant_sla_records": total - breached}

def generate_team_performance(organization, start_date, end_date):
    tickets = Ticket.objects.filter(organization=organization, created_at__date__range=[start_date, end_date], team__isnull=False)
    return {"teams": [{"team_id": item["team_id"], "ticket_count": item["count"]} for item in tickets.values("team_id").annotate(count=Count("id")).order_by("-count")]}

def generate_customer_activity(organization, start_date, end_date):
    tickets = Ticket.objects.filter(organization=organization, created_at__date__range=[start_date, end_date])
    return {"customers": [{"customer_id": item["customer_id"], "ticket_count": item["count"]} for item in tickets.values("customer_id").annotate(count=Count("id")).order_by("-count")]}

def generate_report_data(organization, report_type, start_date, end_date):
    generators = {"TICKET_SUMMARY": generate_ticket_summary, "SLA_PERFORMANCE": generate_sla_performance, "TEAM_PERFORMANCE": generate_team_performance, "CUSTOMER_ACTIVITY": generate_customer_activity}
    generator = generators.get(report_type)
    if not generator:
        raise ValueError("Unsupported report type.")
    return generator(organization, start_date, end_date)