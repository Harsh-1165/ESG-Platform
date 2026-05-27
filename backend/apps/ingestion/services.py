import hashlib
import json

from django.db import IntegrityError, transaction
from django.utils import timezone
from apps.core.models import DataSource, RawRecord
from apps.ingestion.models import RawData, RawDataRow
from .parsers import parse_file_by_source_type


class FileUploadService:
    """Handles CSV uploads for ingestion batches."""

    CHUNK_SIZE = 8192

    @staticmethod
    def compute_file_hash(file_bytes):
        digest = hashlib.sha256()
        digest.update(file_bytes)
        return digest.hexdigest()

    @staticmethod
    def build_external_id(row_data, file_hash):
        if row_data.get('external_id'):
            return row_data['external_id']
        return f"{file_hash}:{row_data['row_number']}"

    @classmethod
    def upload_csv(cls, organization_id, user_email, file_obj, source_type,
                   data_source_name=None, data_source_external_id=None,
                   payload_schema_name='', payload_schema_version=''):
        file_bytes = file_obj.read()
        file_hash = cls.compute_file_hash(file_bytes)

        existing = RawData.objects.filter(
            organization_id=organization_id,
            source_type=source_type,
            file_hash=file_hash
        ).first()

        if existing:
            return {
                'duplicate': True,
                'upload_id': str(existing.id),
                'file_name': existing.file_name,
                'source_type': existing.source_type,
                'row_count': existing.row_count,
                'uploaded_at': existing.uploaded_at,
                'status': existing.status,
                'message': 'This file was already uploaded and processed.',
                'existing_upload_id': str(existing.id),
            }

        file_content = file_bytes.decode('utf-8', errors='replace')
        rows_data = parse_file_by_source_type(file_content, source_type)

        if not data_source_name:
            data_source_name = file_obj.name or f"{source_type} upload"

        data_source_defaults = {
            'organization_id': organization_id,
            'source_type': source_type,
            'name': data_source_name,
            'external_id': data_source_external_id or file_obj.name,
            'created_by': user_email,
        }

        data_source, _ = DataSource.objects.get_or_create(
            organization_id=organization_id,
            source_type=source_type,
            name=data_source_name,
            defaults=data_source_defaults
        )

        batch = RawData.objects.create(
            organization_id=organization_id,
            source_type=source_type,
            file_name=file_obj.name,
            file_hash=file_hash,
            uploaded_by=user_email,
            row_count=len(rows_data),
            status='processing',
            metadata={
                'payload_schema_name': payload_schema_name,
                'payload_schema_version': payload_schema_version,
                'data_source_id': str(data_source.id),
                'created_at': timezone.now().isoformat(),
            }
        )

        successful_rows = 0
        failed_rows = 0
        row_results = []

        with transaction.atomic():
            for row_data in rows_data:
                validation_errors = list(row_data.get('validation_errors', []))
                external_id = cls.build_external_id(row_data, file_hash)
                raw_record_status = 'failed' if validation_errors else 'received'
                raw_record = None

                try:
                    raw_record = RawRecord.objects.create(
                        organization_id=organization_id,
                        data_source=data_source,
                        raw_payload=row_data['raw_content'],
                        external_id=external_id,
                        status=raw_record_status,
                        import_batch_id=str(batch.id),
                        import_errors=validation_errors,
                        processing_notes='; '.join(validation_errors) if validation_errors else '',
                        created_by=user_email,
                    )
                except IntegrityError as exc:
                    validation_errors.append('Duplicate RawRecord key or integrity issue.')
                    raw_record_status = 'failed'
                    failed_rows += 1
                except Exception as exc:
                    validation_errors.append(str(exc))
                    raw_record_status = 'failed'
                    failed_rows += 1
                else:
                    if raw_record_status == 'failed':
                        failed_rows += 1
                    else:
                        successful_rows += 1

                RawDataRow.objects.create(
                    raw_data=batch,
                    row_number=row_data['row_number'],
                    raw_content=row_data['raw_content'],
                    validation_errors=validation_errors,
                    processing_status='failed' if validation_errors else 'pending',
                )

                row_results.append({
                    'row_number': row_data['row_number'],
                    'status': raw_record_status,
                    'errors': validation_errors,
                    'raw_record_external_id': external_id,
                })

        batch.status = 'completed'
        batch.metadata.update({
            'success_count': successful_rows,
            'failed_count': failed_rows,
            'file_hash': file_hash,
        })
        batch.save(update_fields=['status', 'metadata'])

        return {
            'duplicate': False,
            'upload_id': str(batch.id),
            'file_name': batch.file_name,
            'source_type': batch.source_type,
            'data_source_id': str(data_source.id),
            'data_source_name': data_source.name,
            'row_count': batch.row_count,
            'success_count': successful_rows,
            'failed_count': failed_rows,
            'status': batch.status,
            'file_hash': file_hash,
            'rows': row_results[:50],
            'message': 'Upload processed. Some rows may have validation errors.',
        }
