from decimal import Decimal
from django.utils import timezone
from datetime import datetime
from apps.ingestion.models import RawDataRow
from apps.approval.models import ApprovalRecord
from .models import NormalizedRecord, StatusLog
from .sap_normalizer import SAPFuelNormalizer
from .units import convert_to_co2e


def normalize_batch(raw_data_batch_id, normalized_by='system'):
    """Process all rows in a batch"""
    from apps.ingestion.models import RawData
    
    try:
        raw_data = RawData.objects.get(id=raw_data_batch_id)
    except RawData.DoesNotExist:
        return {'status': 'failed', 'error': 'Batch not found'}
    
    results = {'created': 0, 'failed': 0, 'errors': []}
    
    for row in raw_data.rows.all():
        try:
            normalize_row(row, raw_data.source_type, raw_data.organization, normalized_by)
            results['created'] += 1
        except Exception as e:
            results['failed'] += 1
            results['errors'].append(f"Row {row.row_number}: {str(e)}")
            row.processing_status = 'failed'
            row.save()
    
    return results


def normalize_row(raw_row, source_type, organization, normalized_by='system'):
    """Transform single raw row to NormalizedRecord"""
    
    # Parse based on source type
    if source_type == 'SAP_FUEL':
        normalized = _parse_sap_fuel(raw_row, organization, normalized_by)
    elif source_type == 'UTILITY_ELECTRICITY':
        normalized = _parse_utility_electricity(raw_row, organization, normalized_by)
    elif source_type == 'TRAVEL':
        normalized = _parse_corporate_travel(raw_row, organization, normalized_by)
    else:
        raise ValueError(f"Unknown source type: {source_type}")
    
    normalized.save()
    # Run validation and flagging
    try:
        from .validation import ValidationService
        ValidationService.run_and_persist(normalized, user_email=normalized_by)
    except Exception:
        # do not fail normalization on validation errors
        pass
    
    # Mark raw row as normalized
    raw_row.processing_status = 'normalized'
    raw_row.save()
    
    # Create approval record
    ApprovalRecord.objects.create(
        normalized_record=normalized,
        status='pending'
    )
    
    return normalized


def _parse_sap_fuel(raw_row, organization, normalized_by):
    """Parse SAP fuel CSV row using the SAP fuel normalization service."""
    try:
        return SAPFuelNormalizer.normalize_row(raw_row, organization, normalized_by)
    except Exception as e:
        raise ValueError(f"Failed to parse SAP fuel row: {str(e)}")


def _parse_utility_electricity(raw_row, organization, normalized_by):
    """Parse utility electricity CSV row via UtilityNormalizer"""
    try:
        from .utility_normalizer import UtilityNormalizer

        return UtilityNormalizer.normalize_row(raw_row, organization, normalized_by)
    except Exception as e:
        raise ValueError(f"Failed to parse utility data: {str(e)}")


def _parse_corporate_travel(raw_row, organization, normalized_by):
    """Parse corporate travel CSV row via TravelNormalizer"""
    try:
        from .travel_normalizer import TravelNormalizer

        return TravelNormalizer.normalize_row(raw_row, organization, normalized_by)
    except Exception as e:
        raise ValueError(f"Failed to parse travel data: {str(e)}")


def create_status_log(normalized_record, action, old_values=None, new_values=None, user='system'):
    """Track changes to normalized record"""
    StatusLog.objects.create(
        normalized_record=normalized_record,
        action=action,
        old_values=old_values or {},
        new_values=new_values or {},
        user=user
    )
