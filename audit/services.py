from .models import AuditLog

def create_audit_log(user, organization, action, model_name, object_id=None, description="", changes=None):
    return AuditLog.objects.create(user=user, organization=organization, action=action, model_name=model_name, object_id=object_id, description=description, changes=changes or {})

