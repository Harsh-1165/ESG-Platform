"""
Lightweight runner to exercise ValidationService.evaluate without DB writes.
Run inside Django shell or as a module where Django settings are configured.
"""
from decimal import Decimal
from .validation import ValidationService


def run_examples():
    examples = []

    examples.append({
        'id': 'ex1',
        'emission_quantity': Decimal('1000'),
        'emission_unit': 'kg_CO2e',
        'metric_type': 'scope_2',
        'time_period': '2024-04-30',
        'unit_converted_from': 'kWh',
        'conversion_factor': Decimal('0.42'),
        'raw_data_row': {'row_id': 'r1'},
        'source_type': 'UTILITY_ELECTRICITY',
    })

    examples.append({
        'id': 'ex2',
        'emission_quantity': Decimal('-10'),
        'emission_unit': 'kg_CO2e',
        'metric_type': 'scope_3',
        'time_period': None,
        'unit_converted_from': None,
        'conversion_factor': None,
        'raw_data_row': None,
        'source_type': 'TRAVEL',
    })

    for ex in examples:
        flags = ValidationService.evaluate(ex)
        print(f"Example {ex['id']} -> {len(flags)} flags")
        for f in flags:
            print(' -', f['rule_code'], f['reason'], f['severity'], f.get('penalty'))


if __name__ == '__main__':
    run_examples()
