from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.core.models import Organization, OrganizationUser
from apps.ingestion.models import RawData, RawDataRow
from apps.normalization.models import NormalizedRecord
from apps.approval.models import ApprovalRecord
from decimal import Decimal
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Seed database with demo data'

    def handle(self, *args, **options):
        # Create organization
        org, created = Organization.objects.get_or_create(
            name='Demo Corp ESG',
            defaults={
                'active': True,
                'settings': {
                    'emission_factors': {
                        'liters_diesel': 2.64,
                        'kWh': 0.42,
                        'km_car': 0.192,
                    }
                }
            }
        )
        self.stdout.write(f"Organization: {org.name} (created={created})")

        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@democorp.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
        self.stdout.write(f"Admin User: {admin_user.email} (created={created})")

        # Assign admin to org
        org_user, created = OrganizationUser.objects.get_or_create(
            user=admin_user,
            organization=org,
            defaults={'role': 'admin', 'is_active': True}
        )
        self.stdout.write(f"Org Membership: created={created}")

        # Create sample raw data batch
        raw_data, created = RawData.objects.get_or_create(
            organization=org,
            file_name='sample_fuel_data.csv',
            defaults={
                'source_type': 'SAP_FUEL',
                'uploaded_by': 'admin@democorp.com',
                'row_count': 3,
                'status': 'completed',
            }
        )
        self.stdout.write(f"Raw Data Batch: {raw_data.file_name} (created={created})")

        # Create sample rows
        sample_rows = [
            {'Date': '2026-01-15', 'Quantity': '100', 'Unit': 'liters_diesel', 'Facility': 'Building A'},
            {'Date': '2026-01-16', 'Quantity': '150', 'Unit': 'liters_diesel', 'Facility': 'Building B'},
            {'Date': '2026-01-17', 'Quantity': '200', 'Unit': 'liters_gasoline', 'Facility': 'Fleet'},
        ]

        for idx, row_data in enumerate(sample_rows, start=1):
            raw_row, created = RawDataRow.objects.get_or_create(
                raw_data=raw_data,
                row_number=idx,
                defaults={
                    'raw_content': row_data,
                    'validation_errors': [],
                    'is_flagged': False,
                    'processing_status': 'normalized',
                }
            )

            if created:
                # Create normalized record
                quantity = Decimal(row_data['Quantity'])
                from_unit = row_data['Unit']
                
                if from_unit == 'liters_diesel':
                    emission_qty = quantity * Decimal('2.64')
                elif from_unit == 'liters_gasoline':
                    emission_qty = quantity * Decimal('2.31')
                else:
                    emission_qty = quantity
                
                if emission_qty > 1000:
                    emission_qty = emission_qty / Decimal('1000')
                    emission_unit = 'metric_tons_CO2e'
                else:
                    emission_unit = 'kg_CO2e'
                
                normalized, _ = NormalizedRecord.objects.get_or_create(
                    raw_data_row=raw_row,
                    defaults={
                        'organization': org,
                        'source_type': 'SAP_FUEL',
                        'emission_quantity': emission_qty.quantize(Decimal('0.01')),
                        'emission_unit': emission_unit,
                        'metric_type': 'scope_1',
                        'facility_id': row_data['Facility'],
                        'time_period': datetime.strptime(row_data['Date'], '%Y-%m-%d').date(),
                        'normalized_by': 'admin@democorp.com',
                        'unit_converted_from': from_unit,
                        'conversion_factor': Decimal('2.64') if 'diesel' in from_unit else Decimal('2.31'),
                        'is_suspicious': False,
                        'confidence_score': 100,
                    }
                )
                
                # Create approval record
                ApprovalRecord.objects.get_or_create(
                    normalized_record=normalized,
                    defaults={'status': 'pending'}
                )

        self.stdout.write(self.style.SUCCESS('✓ Seed data created successfully'))
