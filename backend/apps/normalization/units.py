from decimal import Decimal

EMISSION_FACTORS = {
    'SAP_FUEL': {
        'liters_diesel': Decimal('2.64'),
        'liters_gasoline': Decimal('2.31'),
        'gallons_diesel': Decimal('10.0'),
        'gallons_gasoline': Decimal('8.75'),
    },
    'UTILITY_ELECTRICITY': {
        'kWh': Decimal('0.42'),
        'mWh': Decimal('420.0'),
        'MWh': Decimal('420.0'),
    },
    'TRAVEL': {
        'km_car': Decimal('0.192'),
        'miles_car': Decimal('0.309'),
        'km_flight': Decimal('0.255'),
        'miles_flight': Decimal('0.41'),
    }
}


def get_conversion_factor(from_unit, source_type, org_factors=None):
    """Get conversion factor for unit to CO2e"""
    factors = org_factors or EMISSION_FACTORS.get(source_type, {})
    
    if from_unit not in factors:
        raise ValueError(f"Unknown unit: {from_unit} for source: {source_type}")
    
    return factors[from_unit]


def convert_to_co2e(quantity, from_unit, source_type, org_factors=None):
    """Convert any unit to kg or metric tons CO2e"""
    quantity = Decimal(str(quantity))
    conversion_factor = get_conversion_factor(from_unit, source_type, org_factors)
    
    emission_qty = quantity * conversion_factor
    
    # Auto-convert to metric tons if large
    target_unit = 'kg_CO2e'
    if emission_qty > 1000:
        emission_qty = emission_qty / Decimal('1000')
        target_unit = 'metric_tons_CO2e'
        emission_qty = emission_qty.quantize(Decimal('0.01'))
    else:
        emission_qty = emission_qty.quantize(Decimal('0.01'))
    
    return emission_qty, target_unit, conversion_factor
