from django.db.models import Q


def apply_dashboard_filters(queryset, params):
    """Apply dashboard filters to the normalized record queryset."""
    source_type = params.get('source_type')
    if source_type:
        queryset = queryset.filter(source_type=source_type)

    review_status = params.get('review_status')
    if review_status:
        queryset = queryset.filter(approval__status=review_status)

    approval_state = params.get('approval_state')
    if approval_state:
        queryset = queryset.filter(approval__status=approval_state)

    flagged = params.get('flagged')
    if flagged is not None:
        if flagged.lower() in ('true', '1', 'yes'):
            queryset = queryset.filter(is_suspicious=True)
        elif flagged.lower() in ('false', '0', 'no'):
            queryset = queryset.filter(is_suspicious=False)

    scope = params.get('scope')
    if scope:
        queryset = queryset.filter(metric_type=scope)

    start_date = params.get('start_date')
    end_date = params.get('end_date')
    if start_date:
        queryset = queryset.filter(time_period__gte=start_date)
    if end_date:
        queryset = queryset.filter(time_period__lte=end_date)

    search = params.get('search')
    if search:
        queryset = queryset.filter(
            Q(facility_id__icontains=search) |
            Q(notes__icontains=search) |
            Q(source_type__icontains=search) |
            Q(raw_data_row__raw_payload__icontains=search)
        )

    return queryset
