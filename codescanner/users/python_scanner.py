import re

def scan_python_code(content):
    # Define patterns and associated details for each vulnerability
    patterns = [
        # SQL Injection patterns
        (
            re.compile(r'\b(?:SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE)\b', re.IGNORECASE),
            'SQL Injection', 
            'SQL Command Pattern',
            'Potential SQL Injection from SQL command',
            'Avoid using unsanitized inputs in SQL queries.',
            'High',  # Severity
            'High'   # Confidence
        ),
        (
            re.compile(r'\b(?:EXECUTE|EXEC)\b', re.IGNORECASE),
            'SQL Injection', 
            'EXEC Command Pattern',
            'Potential SQL Injection from EXEC command',
            'Avoid using unsanitized inputs in SQL queries.',
            'High',  # Severity
            'High'   # Confidence
        ),
        (
            re.compile(r'\b(?:UNION(?: ALL)? SELECT)\b', re.IGNORECASE),
            'SQL Injection', 
            'UNION SELECT Pattern',
            'Potential SQL Injection from UNION SELECT',
            'Avoid using unsanitized inputs in SQL queries.',
            'High',  # Severity
            'High'   # Confidence
        ),
        (
            re.compile(r'\b(?:OR|AND) \d+=\d+', re.IGNORECASE),
            'SQL Injection', 
            'Tautology Pattern',
            'Potential SQL Injection from tautology',
            'Avoid using unsanitized inputs in SQL queries.',
            'High',  # Severity
            'High'   # Confidence
        ),
        (
            re.compile(r"'.*'--", re.IGNORECASE),
            'SQL Injection', 
            'SQL Comment Pattern',
            'Potential SQL Injection from SQL comment',
            'Avoid using unsanitized inputs in SQL queries.',
            'High',  # Severity
            'High'   # Confidence
        ),
        # XSS patterns
        (
            re.compile(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', re.IGNORECASE),
            'XSS', 
            'Script Tag Pattern',
            'Potential XSS from script tags',
            'Sanitize inputs and escape outputs. Avoid directly including user input in HTML.',
            'Medium',  # Severity
            'Medium'   # Confidence
        ),
        (
            re.compile(r'on\w+="[^"]+"', re.IGNORECASE),
            'XSS', 
            'Event Handler Pattern',
            'Potential XSS from event handlers',
            'Sanitize inputs and escape outputs. Avoid directly including user input in HTML.',
            'Medium',  # Severity
            'Medium'   # Confidence
        ),
        (
            re.compile(r'<[^>]+>', re.IGNORECASE),
            'XSS', 
            'HTML Tag Pattern',
            'Potential XSS from HTML tags',
            'Sanitize inputs and escape outputs. Avoid directly including user input in HTML.',
            'Medium',  # Severity
            'Medium'   # Confidence
        )
    ]
    
    vulnerabilities = []
    for i, line in enumerate(content.split('\n'), start=1):
        for pattern, vulnerability_type, vulnerability_name, result, recommendation, severity, confidence in patterns:
            if pattern.search(line):
                vulnerabilities.append({
                    'line_number': i,
                    'code_snippet': line.strip(),
                    'vulnerability_type': vulnerability_type,
                    'vulnerability_name': vulnerability_name,
                    'result': result,
                    'recommendation': recommendation,
                    'severity': severity,
                    'confidence': confidence
                })
                break  # Stop checking other patterns if one is found
    return vulnerabilities
