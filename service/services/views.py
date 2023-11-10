from django.conf import settings
from django.core.cache import cache
from django.db.models import Prefetch, Sum
from rest_framework.viewsets import ReadOnlyModelViewSet

from clients.models import Client
from services.models import Subscriptions
from services.serializers import SubscriptionSerializer


class SubscriptionView(ReadOnlyModelViewSet):
    queryset = Subscriptions.objects.all().prefetch_related(
        'plan',  # позволяет доставать все планы в одном запросе избегая n+1
        Prefetch('client', queryset=Client.objects.all().select_related('user').only('company_name',
                                                                                     'user__email')))
    # .annotate(price=F('service__full_price') - F('service__full_price') * F('plan__discount_percent') / 100.00)
    # annotate переносим к таскам для оптимизации работы

    # queryset = Subscriptions.objects.all().prefetch_related('client').prefetch_related('client__user')
    # prefetch_releated(client) - длявсех подписок вытащить всех клиентов одним разом и склеить, для всех сразу
    # client__user - убираем n+1 на запросы к юзеру
    # annotate(price) -создает виртуальное поле прайс(на уровне базы)  у каждого поля сабскрипшн
    # F - обращаемся к полю
    serializer_class = SubscriptionSerializer

    # !!! Кодом ниже мы переопределяем выведения данных и его уровни, для того чтобы можно было выводить доп информацию,
    # !!! Но фронт за это может дать пизды, нужно согласовывать такие моменты. Переопределяем ListModelMixin

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        response = super().list(request, *args, *kwargs)

        # делаем кэш на тотал прайс

        price_cache = cache.get(settings.PRICE_CACHE_NAME)

        if price_cache:
            total_price = price_cache
        else:
            total_price = queryset.aggregate(total=Sum('price')).get('total')
            cache.set(settings.PRICE_CACHE_NAME, total_price, 60 * 60)  # кэш ОБЯЗАН стухнуть, нельзя делать его вечным

        response_data = {'data': response.data}
        response_data['total_amount'] = total_price  # показывает сумму всех подписок
        # queryset.aggregate(total=Sum('price')) - выдает словарь в котром подключен тотал c нужными значениями,
        # а с get вернет сумму всех подписок
        response.data = response_data

        return response
