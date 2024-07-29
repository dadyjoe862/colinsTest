import os
import subprocess

def scan_file_for_vulnerabilities(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()[1:]  # Get the file extension

    if file_extension == 'py':
        return scan_python_file(file_path)
    elif file_extension == 'php':
        return scan_php_file(file_path)
    elif file_extension == 'html':
        return scan_html_file(file_path)
    else:
        return f'Unsupported file type: {file_extension}'

def scan_python_file(file_path):
    try:
        result = subprocess.run(['bandit', '-r', file_path], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f'Exception occurred while scanning Python file: {e}'

def scan_php_file(file_path):
    try:
        result = subprocess.run(['phpstan', 'analyse', file_path], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f'Exception occurred while scanning PHP file: {e}'

def scan_html_file(file_path):
    try:
        result = subprocess.run(['htmlhint', file_path], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f'Exception occurred while scanning HTML file: {e}'
