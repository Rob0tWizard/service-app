from django.conf import settings
from django.core.cache import cache
from django.db.models.signals import post_delete
from django.dispatch import receiver



@receiver(post_delete, sender=None)
def delete_cache_total_sum(*args, **kwargs):
    # вызывается каждый раз когда мы удалили подписку, ведь общая сумма изменяется, таску мы вызвать не можем,
    # но можем инвалидировать кэш
    cache.delete(settings.PRICE_CACHE_NAME)
