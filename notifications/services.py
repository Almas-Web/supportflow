from .models import Notification

def create_ticket_notification(ticket, user, notification_type, title, message):
    if not user or not user.is_active:
        return
    Notification.objects.create(user=user, organization=ticket.organization, ticket=ticket, notification_type=notification_type, title=title, message=message)

def notify_ticket_created(ticket):
    if ticket.agent:
        create_ticket_notification(ticket, ticket.agent, Notification.TICKET_CREATED, "New Ticket Created", f"Ticket {ticket.ticket_number} has been created and assigned to you.")

def notify_ticket_assigned(ticket):
    if ticket.agent:
        create_ticket_notification(ticket, ticket.agent, Notification.TICKET_ASSIGNED, "Ticket Assigned", f"Ticket {ticket.ticket_number} has been assigned to you.")

def notify_ticket_updated(ticket):
    if ticket.agent:
        create_ticket_notification(ticket, ticket.agent, Notification.TICKET_UPDATED, "Ticket Updated", f"Ticket {ticket.ticket_number} has been updated.")

def notify_ticket_status_changed(ticket):
    recipients = []
    if ticket.agent:
        recipients.append(ticket.agent)
    if ticket.customer and ticket.customer.user:
        recipients.append(ticket.customer.user)
    for user in recipients:
        create_ticket_notification(ticket, user, Notification.TICKET_STATUS_CHANGED, "Ticket Status Changed", f"Ticket {ticket.ticket_number} status changed to {ticket.get_status_display()}.")

def notify_ticket_resolved(ticket):
    recipients = []
    if ticket.agent:
        recipients.append(ticket.agent)
    if ticket.customer and ticket.customer.user:
        recipients.append(ticket.customer.user)
    for user in recipients:
        create_ticket_notification(ticket, user, Notification.TICKET_RESOLVED, "Ticket Resolved", f"Ticket {ticket.ticket_number} has been resolved.")
        