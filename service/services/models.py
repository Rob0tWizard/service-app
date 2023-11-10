from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models.signals import post_delete

from clients.models import Client
from .receiver import delete_cache_total_sum
from .tasks import set_price


# создаем воображаемую бизнес логику
class Service(models.Model):
    name = models.CharField(max_length=50)
    full_price = models.PositiveIntegerField()

    def __str__(self):
        return f'Service : {self.name}'


    def __init__(self, *args, **kwargs):  # в момент инита происходят фиксации значений
        super().__init__(*args, **kwargs)
        self.__full_price = self.full_price

    def save(self, *args, **kwargs):  # делается если фулпрайс или диск_перцент изменились
        if self.__full_price != self.full_price:
            for subscriptions in self.subscriptions.all():  # from related name
                set_price.delay(subscriptions.id)

        return super().save(*args, **kwargs)


# тарифные план
class Plan(models.Model):
    # ниже идет кортеж с кортежами
    PLAN_TYPES = (
        ('full', 'Full'),
        ('students', 'Students'),
        ('discount', 'Discount'),
    )

    plan_type = models.CharField(choices=PLAN_TYPES, max_length=10)
    # первая часть хранится в базе, вторая отображается юзеру
    discount_percent = models.PositiveIntegerField(default=0,
                                                   validators=[
                                                       MaxValueValidator(100)
                                                   ])

    def __str__(self):
        return f'Plan : {self.plan_type}'

    def __init__(self, *args, **kwargs):  # в момент инита происходят фиксации значений
        super().__init__(*args, **kwargs)
        self.__discount_percent = self.discount_percent

    def save(self, *args, **kwargs):  # делается если фулпрайс или диск_перцент изменились
        if self.__discount_percent != self.discount_percent:
            for subscriptions in self.subscriptions.all():  # from related name
                set_price.delay(subscriptions.id)

        return super().save(*args, **kwargs)


class Subscriptions(models.Model):
    client = models.ForeignKey(Client, related_name='subscriptions', on_delete=models.PROTECT)
    # related_name - это то с каким именем модель будет доступна внутри модели с которой образууем связь,
    # тоесть чтоб показать подписки клиента client.subscriptions.all , или через фильтры
    service = models.ForeignKey(Service, related_name='subscriptions', on_delete=models.PROTECT)
    plan = models.ForeignKey(Plan, related_name='subscriptions', on_delete=models.PROTECT)
    price = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        creating = not bool(self.id) #когда нет селф айди, значит оно создается
        result = super().save(*args, **kwargs)
    # а когда создалась нужно вызвать таску
        if creating:
            set_price.delay(self.id)    #инвалидируем кэш через вызов таска, и делаем это только тогда когда модель создается
        return result

    def __str__(self):
        return f'Subscriptions : {self.service}'


post_delete.connect(delete_cache_total_sum, sender=Subscriptions)
# соединили модель с сигналом из receiver
