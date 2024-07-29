import re

def scan_javascript_code(content):
    # Scanning logic for JavaScript files
    xss_pattern = re.compile(r'\b(?:eval|document\.write|innerHTML)\b', re.IGNORECASE)
    
    vulnerabilities = []
    for i, line in enumerate(content.split('\n'), start=1):
        if xss_pattern.search(line):
            vulnerabilities.append({
                'line_number': i,
                'code_snippet': line.strip(),
                'result': 'Potential Cross-Site Scripting (XSS)',
                'recommendation': 'Avoid using unsafe methods for dynamic content.',
                'severity': 'High',
                'confidence': 'High'  # Add the confidence key with a default value
            })
    return vulnerabilities
