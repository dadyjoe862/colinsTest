import re

def scan_php_code(content):
    # Scanning logic for PHP files
    sql_pattern = re.compile(r'\b(?:SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE)\b', re.IGNORECASE)
    
    vulnerabilities = []
    for i, line in enumerate(content.split('\n'), start=1):
        if sql_pattern.search(line):
            vulnerabilities.append({
                'line_number': i,
                'code_snippet': line.strip(),
                'result': 'Potential SQL Injection',
                'recommendation': 'Avoid using unsanitized inputs in SQL queries.',
                'severity': 'High',
                'confidence': 'High'  # Add the confidence key with a default value
            })
    return vulnerabilities