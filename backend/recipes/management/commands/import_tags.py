import csv

from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    def handle(self, *args, **options):
        csv_file2 = open('/app/recipes/management/commands/tags.csv',
                         encoding='utf-8')
        reader = csv.reader(csv_file2, delimiter=',')
        next(reader, None)
        list_tags = []
        for row in reader:
            name, color, slug = row
            list_tags.append(Tag(
                name=name,
                color=color,
                slug=slug))
        Tag.objects.bulk_create(list_tags)
        print('Теги +')
