from django.utils import timezone
from .models import ApprovalRecord, AuditLog


VALID_TRANSITIONS = {
    'pending': ['approved', 'rejected', 'locked'],
    'approved': ['locked'],
    'rejected': [],
    'locked': [],
}


def can_transition(from_status, to_status):
    """Check if transition is allowed"""
    return to_status in VALID_TRANSITIONS.get(from_status, [])


def approve_record(approval_record, reviewer_email, comment=''):
    """Approve a record"""
    if not can_transition(approval_record.status, 'approved'):
        raise ValueError(f"Cannot approve from status: {approval_record.status}")
    
    old_status = approval_record.status
    approval_record.status = 'approved'
    approval_record.reviewer = reviewer_email
    approval_record.reviewed_at = timezone.now()
    approval_record.reviewed_comment = comment
    approval_record.save()
    
    # Audit log
    AuditLog.objects.create(
        organization_id=approval_record.normalized_record.organization_id,
        record_type='ApprovalRecord',
        record_id=approval_record.id,
        action='approved',
        old_values={'status': old_status},
        new_values={'status': 'approved'},
        user=reviewer_email
    )
    
    return approval_record


def reject_record(approval_record, reviewer_email, reason=''):
    """Reject a record"""
    if not can_transition(approval_record.status, 'rejected'):
        raise ValueError(f"Cannot reject from status: {approval_record.status}")
    
    old_status = approval_record.status
    approval_record.status = 'rejected'
    approval_record.reviewer = reviewer_email
    approval_record.reviewed_at = timezone.now()
    approval_record.rejection_reason = reason
    approval_record.save()
    
    # Mark raw row as needing re-work
    if approval_record.normalized_record.raw_data_row:
        approval_record.normalized_record.raw_data_row.processing_status = 'pending'
        approval_record.normalized_record.raw_data_row.save()
    
    AuditLog.objects.create(
        organization_id=approval_record.normalized_record.organization_id,
        record_type='ApprovalRecord',
        record_id=approval_record.id,
        action='rejected',
        old_values={'status': old_status},
        new_values={'status': 'rejected', 'reason': reason},
        user=reviewer_email
    )
    
    return approval_record


def lock_record(approval_record, admin_email, reason=''):
    """Lock a record (immutable)"""
    if not can_transition(approval_record.status, 'locked'):
        raise ValueError(f"Cannot lock from status: {approval_record.status}")
    
    old_status = approval_record.status
    approval_record.status = 'locked'
    approval_record.lock_reason = reason
    approval_record.save()
    
    AuditLog.objects.create(
        organization_id=approval_record.normalized_record.organization_id,
        record_type='ApprovalRecord',
        record_id=approval_record.id,
        action='locked',
        old_values={'status': old_status},
        new_values={'status': 'locked', 'reason': reason},
        user=admin_email
    )
    
    return approval_record
