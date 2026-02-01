from django.core.management.base import BaseCommand, CommandError
from core.models import Prompt
import os

class Command(BaseCommand):
    help = 'Reads a text file line by line and creates Prompt objects for each non-blank line.'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='The path to the text file containing prompts, one per line.')

    def handle(self, *args, **options):
        file_path = options['file_path']

        if not os.path.exists(file_path):
            raise CommandError(f'File "{file_path}" does not exist.')
        
        self.stdout.write(self.style.SUCCESS(f'Attempting to import prompts from "{file_path}"...'))

        prompts_created_count = 0
        prompts_skipped_count = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                prompt_text = line.strip()
                
                if not prompt_text:
                    prompts_skipped_count += 1
                    continue
                
                # Check if prompt already exists
                obj, created = Prompt.objects.get_or_create(text=prompt_text)
                
                if created:
                    self.stdout.write(f'  Created prompt: "{prompt_text}"')
                    prompts_created_count += 1
                else:
                    self.stdout.write(f'  Skipped existing prompt: "{prompt_text}"')
                    prompts_skipped_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'\nImport complete: {prompts_created_count} prompts created, '
            f'{prompts_skipped_count} prompts skipped (already existed or blank lines).'
        ))
