from typing import Optional, Dict, Any
from django.utils import timezone
from .models import AuditLog


def _stringify_id(pk) -> Optional[str]:
    if pk is None:
        return None
    return str(pk)


def log_action(
    *,
    organization=None,
    actor: str = 'system',
    action: str,
    record=None,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    reason: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> AuditLog:
    """Create an AuditLog entry (best-effort helper).

    Example:
        log_action(
            organization=org,
            actor=request.user.email,
            action='approved',
            record=normalized_record,
            old_values={'status': 'pending'},
            new_values={'status': 'approved'},
            reason='Reviewed by Alice',
            ip_address=get_client_ip(request),
        )
    """

    record_type = None
    record_id = None
    if record is not None:
        try:
            record_type = record.__class__.__name__
        except Exception:
            record_type = None
        try:
            record_id = _stringify_id(getattr(record, 'id', getattr(record, 'pk', None)))
        except Exception:
            record_id = None

    entry = AuditLog(
        organization=getattr(organization, 'id', None) and organization or None,
        record_type=record_type,
        record_id=record_id,
        action=action,
        actor=actor or 'system',
        old_values=old_values or {},
        new_values=new_values or {},
        reason=reason or '',
        ip_address=ip_address,
        user_agent=user_agent or '',
    )
    # write entry to DB; save() enforces immutability
    entry.save()
    return entry


def log_create(*, organization=None, actor: str = 'system', record=None, new_values: Optional[Dict[str, Any]] = None, reason: Optional[str] = None, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> AuditLog:
    return log_action(
        organization=organization,
        actor=actor,
        action='created',
        record=record,
        old_values={},
        new_values=new_values or {},
        reason=reason,
        ip_address=ip_address,
        user_agent=user_agent,
    )


def log_update(*, organization=None, actor: str = 'system', record=None, old_values: Optional[Dict[str, Any]] = None, new_values: Optional[Dict[str, Any]] = None, reason: Optional[str] = None, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> AuditLog:
    return log_action(
        organization=organization,
        actor=actor,
        action='updated',
        record=record,
        old_values=old_values or {},
        new_values=new_values or {},
        reason=reason,
        ip_address=ip_address,
        user_agent=user_agent,
    )


# Convenience: signal helpers (example usage provided below in docs)
from django.db.models.signals import pre_save, post_save


def attach_audit_signals(model, *, organization_attr: str = 'organization'):
    """Attach simple pre/post-save signal handlers to capture created/updated events.

    WARNING: This is a convenience that stores shallow snapshots; for large models
    or sensitive fields prefer explicit calls to `log_create`/`log_update` from
    the code path that performs the change.

    Usage:
        from apps.audit.utils import attach_audit_signals
        attach_audit_signals(MyModel)
    """

    def _pre_save(sender, instance, **kwargs):
        if getattr(instance, 'pk', None):
            try:
                previous = sender.objects.get(pk=instance.pk)
                # store a minimal old-values snapshot on the instance for post-save
                instance._audit_old_values = {f.name: getattr(previous, f.name) for f in sender._meta.fields}
            except sender.DoesNotExist:
                instance._audit_old_values = {}
        else:
            instance._audit_old_values = {}

    def _post_save(sender, instance, created, **kwargs):
        org = getattr(instance, organization_attr, None)
        actor = getattr(instance, '_audit_actor', 'system')
        ip = getattr(instance, '_audit_ip', None)
        ua = getattr(instance, '_audit_user_agent', None)

        if created:
            log_create(organization=org, actor=actor, record=instance, new_values={f.name: getattr(instance, f.name) for f in sender._meta.fields}, ip_address=ip, user_agent=ua)
        else:
            old = getattr(instance, '_audit_old_values', {})
            new = {f.name: getattr(instance, f.name) for f in sender._meta.fields}
            # compute minimal diff here if desired
            diffs_old = {}
            diffs_new = {}
            for k in new.keys():
                if old.get(k) != new.get(k):
                    diffs_old[k] = old.get(k)
                    diffs_new[k] = new.get(k)
            if diffs_old or diffs_new:
                log_update(organization=org, actor=actor, record=instance, old_values=diffs_old, new_values=diffs_new, ip_address=ip, user_agent=ua)

    pre_save.connect(_pre_save, sender=model, weak=False)
    post_save.connect(_post_save, sender=model, weak=False)


# Example of request-aware usage (attach request data before saving):
# instance._audit_actor = request.user.email
# instance._audit_ip = get_client_ip(request)
# instance._audit_user_agent = request.META.get('HTTP_USER_AGENT')
# instance.save()
