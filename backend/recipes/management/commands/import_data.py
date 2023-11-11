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
        list_ingredients = []
        for row in reader:
            name, meashurement_unit = row
            list_ingredients.append(Ingredient(
                name=name,
                meashurement_unit=meashurement_unit))
        Ingredient.objects.bulk_create(list_ingredients)
        print('Ингредиенты +')
