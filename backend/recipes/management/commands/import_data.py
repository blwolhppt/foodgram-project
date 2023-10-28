import csv
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        csv_file = open('C:/Users/blwol/PycharmProjects/foodgram-project'
                        '-react/backend/recipes/management/commands'
                        '/ingredients.csv', encoding='utf-8')
        reader = csv.reader(csv_file, delimiter=',')
        next(reader, None)
        for row in reader:
            obj, created = Ingredient.objects.get_or_create(
                name=row[0],
                measurement=row[1]
            )
        print('Ингредиенты +')
