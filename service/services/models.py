from django.core.validators import MaxValueValidator
from django.db import models

from clients.models import Client


#создаем воображаемую бизнес логику
class Service(models.Model):
    name=models.CharField(max_length=50)
    full_price=models.PositiveIntegerField()

#тарифные план
class Plan(models.Model):
    #ниже идет кортеж с кортежами
    PLAN_TYPES=(
        ('full', 'Full'),
        ('students', 'Students'),
        ('discount', 'Discount'),
    )

    plan_type = models.CharField(choices=PLAN_TYPES, max_length=10)
    #первая часть хранится в базе, вторая отображается юзеру
    discount_percent=models.PositiveIntegerField(default=0,
                                                 validators=[
                                                     MaxValueValidator(100)
                                                 ])


class Subscriptions(models.Model):
    client = models.ForeignKey(Client, related_name='subscriptions', on_delete=models.PROTECT)
    #related_name - это то с каким именем модель будет доступна внутри модели с которой образууем связь,
    #тоесть чтоб показать подписки клиента client.subscriptions.all , или через фильтры
    service = models.ForeignKey(Service, related_name='subscriptions', on_delete=models.PROTECT)
    plan = models.ForeignKey(Plan, related_name='subscriptions', on_delete=models.PROTECT)
