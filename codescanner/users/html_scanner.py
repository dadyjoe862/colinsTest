import re

def scan_html_code(content):
    # Scanning logic for HTML files
    xss_pattern = re.compile(r'<\s*script\s*>', re.IGNORECASE)
    
    vulnerabilities = []
    for i, line in enumerate(content.split('\n'), start=1):
        if xss_pattern.search(line):
            vulnerabilities.append({
                'line_number': i,
                'code_snippet': line.strip(),
                'result': 'Potential Cross-Site Scripting (XSS)',
                'recommendation': 'Ensure proper input sanitization and output encoding.',
                'severity': 'High',
                'confidence': 'High'  # Add the confidence key with a default value
            })
    return vulnerabilities