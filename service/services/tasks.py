from celery import shared_task
from celery_singleton import Singleton
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.db.models import F


# используем сингле тон(рекваирментс) для таски ниже, он позволяет создавать класс только в одном экземпляре
@shared_task(base=Singleton)
# тем самым не засоряет изменением одного и того же поля, например если изменяется подряд поле price, таска будет
# одна, а не столько сколько раз мы изменяли это поле
def set_price(subscriptions_id):
    from services.models import Subscriptions
    # subscription_id - потому что пока таска ждет исполнения, сам объект за время в очереди может измениться,
    # а если айди, то получаем в момент запуска таски

    with transaction.atomic():
        # Все действия внутри транзакции происходят вместе, база накапливает изменения внутри транзакции и применяет
        # их ВСЕ вместе или не применит ИХ ВСЕ. То есть объекты ниже лочатся пока не пройдет транзакция,
        # никто не получит к ним доступа
        subscriptions = Subscriptions.objects.filter(id=subscriptions_id).annotate(  # получаем таску
            annotated_price=F('service__full_price') - F('service__full_price') * F(
                'plan__discount_percent') / 100.00).first()
        # new_price = (subscriptions.service.full_price -
        #              subscriptions.service.full_price * subscriptions.plan.discount_percent / 100)
        # # получили сервис и план, на питоне просчитали
        subscriptions.price = subscriptions.annotated_price  # виртуальное поле присваиваем реальному прайс
        subscriptions.save()
# инвалидация кэша который мы включаем во views
    cache.delete(settings.PRICE_CACHE_NAME)
