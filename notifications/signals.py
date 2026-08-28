from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from tickets.models import Ticket
from .services import notify_ticket_created, notify_ticket_assigned, notify_ticket_status_changed, notify_ticket_resolved

@receiver(pre_save, sender=Ticket)
def ticket_pre_save(sender, instance, **kwargs):
    if not instance.pk:
        instance._old_agent_id = None
        instance._old_status = None
        return
    old_ticket = Ticket.objects.filter(pk=instance.pk).first()
    instance._old_agent_id = old_ticket.agent_id if old_ticket else None
    instance._old_status = old_ticket.status if old_ticket else None

@receiver(post_save, sender=Ticket)
def ticket_post_save(sender, instance, created, **kwargs):
    if created:
        notify_ticket_created(instance)
        return
    if getattr(instance, "_old_agent_id", None) != instance.agent_id and instance.agent_id:
        notify_ticket_assigned(instance)
    if getattr(instance, "_old_status", None) != instance.status:
        if instance.status == Ticket.RESOLVED:
            notify_ticket_resolved(instance)
        else:
            notify_ticket_status_changed(instance)