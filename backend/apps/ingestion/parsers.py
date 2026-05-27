import csv
import io


class CSVParser:
    """Parse CSV files for different source types"""
    
    @staticmethod
    def parse_sap_fuel(file_content):
        """Parse SAP fuel/procurement CSV"""
        reader = csv.DictReader(io.StringIO(file_content))
        rows = []
        errors = []
        
        required_fields = ['Date', 'Quantity', 'Unit', 'Facility']
        
        for index, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
            row_errors = []
            
            # Validate required fields
            for field in required_fields:
                if not row.get(field):
                    row_errors.append(f"Missing required field: {field}")
            
            rows.append({
                'row_number': index,
                'raw_content': row,
                'validation_errors': row_errors,
            })
        
        return rows
    
    @staticmethod
    def parse_utility_electricity(file_content):
        """Parse utility electricity CSV"""
        reader = csv.DictReader(io.StringIO(file_content))
        rows = []
        
        for index, row in enumerate(reader, start=2):
            rows.append({
                'row_number': index,
                'raw_content': row,
                'validation_errors': [],
            })
        
        return rows
    
    @staticmethod
    def parse_corporate_travel(file_content):
        """Parse corporate travel CSV"""
        reader = csv.DictReader(io.StringIO(file_content))
        rows = []
        
        for index, row in enumerate(reader, start=2):
            rows.append({
                'row_number': index,
                'raw_content': row,
                'validation_errors': [],
            })
        
        return rows


def parse_file_by_source_type(file_content, source_type):
    """Route to appropriate parser"""
    if source_type == 'SAP_FUEL':
        return CSVParser.parse_sap_fuel(file_content)
    elif source_type == 'UTILITY_ELECTRICITY':
        return CSVParser.parse_utility_electricity(file_content)
    elif source_type == 'TRAVEL':
        return CSVParser.parse_corporate_travel(file_content)
    else:
        raise ValueError(f"Unknown source type: {source_type}")
