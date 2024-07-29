import subprocess
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Run PHPStan analysis'

    def handle(self, *args, **kwargs):
        result = subprocess.run(['./run_phpstan.sh'], capture_output=True, text=True)
        self.stdout.write(self.style.SUCCESS(result.stdout))
        if result.stderr:
            self.stdout.write(self.style.ERROR(result.stderr))
