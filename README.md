![foodgram-project-react Workflow Status](https://github.com/blwolhppt/foodgram-project-react/actions/workflows/main.yml/badge.svg?branch=master&event=push)
# Foodgram 

## Описание проекта:
— сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд. 

## Ссылка на соцсеть: 
http://foodgramblwol.ddns.net/recipes/

## Технологии:

- Python 3.9
- Django
- Gunicorn
- Nginx
- React
- Django REST Framework
- Docker

## Запуск проекта:
- Клонируем репозиторий:
```angular2html
git clone git@github.com:blwolhppt/foodgram-project-react.git
```
- Запускаем:
```angular2html
sudo docker compose -f docker-compose.production.yml up
```
- Выполняем сбор статики и миграции:
```angular2html
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate

sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic

sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /static/static/
```

## Автор проекта: Белова Ольга
