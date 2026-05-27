Audit Trail Usage
==================

Summary
-------
This `apps.audit` helper provides an immutable `AuditLog` model and convenience helpers to persist audit entries for key actions: create, update, approve, reject, lock/unlock, comment creation, and normalization events.

1) Model (already in code):
- `apps.audit.models.AuditLog` stores: `organization`, `record_type`, `record_id`, `action`, `actor`, `timestamp`, `old_values`, `new_values`, `reason`, `ip_address`.
- Immutable: saving an existing `AuditLog` (updates) will raise an exception.

2) Helpers: `apps.audit.utils`
- `log_action(...)` generic writer
- `log_create(...)`, `log_update(...)` convenience wrappers
- `attach_audit_signals(Model)` attaches a pre_save/post_save pair to automatically log create/update events for a model

3) Example log entries (Python snippets)

- Manual create log:

```py
from apps.audit.utils import log_create

log_create(
    organization=org,
    actor=request.user.email,
    record=normalized_record,
    new_values={'emission_quantity': str(normalized_record.emission_quantity)},
    reason='Imported from CSV',
    ip_address=get_client_ip(request),
)
```

- Manual update log:

```py
from apps.audit.utils import log_update

log_update(
    organization=org,
    actor=request.user.email,
    record=normalized_record,
    old_values={'emission_quantity': '100.00'},
    new_values={'emission_quantity': '95.00'},
    reason='Analyst corrected rounding error',
)
```

- Comment creation:

```py
# after saving a ReviewComment instance
from apps.audit.utils import log_action
log_action(organization=org, actor=reviewer_email, action='comment_created', record=normalized_record, new_values={'comment_id': str(comment.id), 'text': comment.comment_text})
```

4) Showing history in the UI
- Query `AuditLog.objects.filter(record_type='NormalizedRecord', record_id=str(record.id)).order_by('-timestamp')`.
- Use a small serializer returning `actor`, `timestamp`, `action`, `old_values`, `new_values`, `reason` and display as a timeline in the record detail view.
- For large results, paginate and show diffs collapsed by change group (e.g., group multiple field updates in one row by timestamp).

5) Keeping the audit trail immutable
- The `AuditLog.save()` implementation prevents updates to existing entries by raising an error if attempting to save a non-new instance.
- Enforcement suggestions:
  - Do not expose admin edit/delete for `AuditLog` (remove from admin or make read-only).
  - At DB level consider: use a separate audit DB/user with only INSERT privileges for the service account writing logs; or use DB triggers to insert into an append-only audit table.
  - Monitor and alert on any attempts to modify `audit_logs` (log inspector job).

Integration tips
----------------
- Prefer explicit calls to `log_create` and `log_update` from application code paths where business logic occurs (views/services) rather than relying solely on generic model signals; signals are convenient but may capture changes from background jobs unexpectedly.
- For approval transitions, call `log_action(... action='approved'/ 'rejected' ...)` in the approval workflow functions so the exact actor and reason are recorded.
- For imports/normalization, include source metadata in `new_values` (e.g., `{'source': 'sap', 'file_hash': '...'} `) so the audit trail explains where data came from.

Database migrations
-------------------
- After adding the files run:

```powershell
cd "d:\Breathe ESG\backend"
python manage.py makemigrations audit
python manage.py migrate
```

Security
--------
- Restrict who can view audit logs via permissions; logs often contain PII and must be protected.
- Avoid storing full user credentials or secrets in `old_values`/`new_values`.

Questions / next steps
---------------------
- I can add signal attachment for `RawDataRow`, `NormalizedRecord`, and `ApprovalRecord`, or I can add explicit log calls into the approval workflow and normalization pipeline. Which do you prefer?