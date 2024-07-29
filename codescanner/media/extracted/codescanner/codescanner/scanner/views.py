import ast
import re
from django.shortcuts import get_object_or_404, render
from users.models import ScanResult, UploadedFile, UploadedFolder

# Function to scan the folder recursively.
def scan_folder(request, folder_id):
    folder = get_object_or_404(UploadedFolder, pk=folder_id)
    files = folder.files.all()
    
    for file in files:
        file_path = file.file.path
        try:
            with open(file_path, 'r') as f:
                code = f.read()
                if file.name.endswith('.py'):
                    issues = analyze_python_code(code)
                    issues += analyze_sql_injection(code)
                    issues += analyze_xss(code)
                    save_scan_results(issues, file_path, request.user)
        except Exception as e:
            # Log the exception or handle it as needed
            print(f"Error reading file {file_path}: {e}")

    return render(request, 'scanner/scan_result.html', {'results': ScanResult.objects.filter(user=request.user)})

# Function to parse the python code 
def parse_python_code(code):
    return ast.parse(code)

class PythonAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.issues = []
        self.code = ""

    def set_code(self, code):
        self.code = code

    def visit_FunctionDef(self, node):
        defined_vars = set()
        used_vars = set()

        for n in ast.walk(node):
            if isinstance(n, ast.Name):
                if isinstance(n.ctx, ast.Store):
                    defined_vars.add(n.id)
                elif isinstance(n.ctx, ast.Load):
                    used_vars.add(n.id)

        unused_vars = defined_vars - used_vars
        for var in unused_vars:
            self.issues.append({
                'line_number': node.lineno,
                'code_snippet': ast.get_source_segment(self.code, node),
                'result': f"Unused variable '{var}' in function '{node.name}'",
                'recommendation': f"Consider removing or using the variable '{var}'"
            })

        self.generic_visit(node)

    def get_issues(self):
        return self.issues

# Function to analyze the python code 
def analyze_python_code(code):
    tree = parse_python_code(code)
    analyzer = PythonAnalyzer()
    analyzer.set_code(code)
    analyzer.visit(tree)
    return analyzer.get_issues()

def analyze_sql_injection(code):
    issues = []
    lines = code.split('\n')
    pattern = re.compile(r"(['\"].*\+.*['\"])|(\bexec\b|\bexecute\b|\bquery\b|\bfetch\b|\bselect\b|\binsert\b|\bupdate\b|\bdelete\b).*['\"]\s*\+|\+\s*['\"]", re.IGNORECASE)
    
    for line_number, line in enumerate(lines, start=1):
        if pattern.search(line):
            issues.append({
                'line_number': line_number,
                'code_snippet': line.strip(),
                'result': "Potential SQL injection vulnerability",
                'recommendation': "Use parameterized queries to prevent SQL injection"
            })
    return issues

def analyze_xss(code):
    issues = []
    lines = code.split('\n')
    pattern = re.compile(r"(<[^>]+>.*['\"].*\+.*['\"].*</[^>]+>)|(<[^>]+\s*=\s*['\"].*\+.*['\"].*>)", re.IGNORECASE)
    
    for line_number, line in enumerate(lines, start=1):
        if pattern.search(line):
            issues.append({
                'line_number': line_number,
                'code_snippet': line.strip(),
                'result': "Potential Cross-Site Scripting (XSS) vulnerability",
                'recommendation': "Sanitize user input before rendering in HTML"
            })
    return issues

def save_scan_results(issues, file_path, user):
    for issue in issues:
        ScanResult.objects.create(
            file_path=file_path,
            line_number=issue['line_number'],
            code_snippet=issue['code_snippet'],
            result=issue['result'],
            recommendation=issue['recommendation'],
            user=user
        )

def scan_result(request):
    return render(request, 'scanner/scan_result.html', {'results': ScanResult.objects.filter(user=request.user)})
