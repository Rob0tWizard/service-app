from django.db.models import Prefetch
from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet

from clients.models import Client
from services.models import Subscriptions
from services.serializers import SubscriptionSerializer


class SubscriptionView(ReadOnlyModelViewSet):
    queryset = Subscriptions.objects.all().prefetch_related(
        Prefetch('client',
                 queryset=Client.objects.all().select_related('user').only('company_name',
                                                                           'user__email'))
    )
    # queryset = Subscriptions.objects.all().prefetch_related('client').prefetch_related('client__user')
    # prefetch_releated(client) - длявсех подписок вытащить всех клиентов одним разом и склеить, для всех сразу
    # client__user - убираем n+1 на запросы к юзеру
    serializer_class = SubscriptionSerializer
