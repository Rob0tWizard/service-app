from rest_framework import serializers

from services.models import Subscriptions, Plan


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.company_name")
    email = serializers.CharField(source="client.user.email")
    plan = PlanSerializer()
    price = serializers.SerializerMethodField()     #методфиелд это соглащение об использовании имен если поле price он ищет GET_price
    def get_price(self, instance):
        return instance.price
            # вычисляем price во views на уровне базы
            # (instance.service.full_price -
            #     instance.service.full_price *
            #     (instance.plan.discount_percent / 100))
    # instance - это конкретное воплощение (представление) класса, созданное на основе его определения. Когда вы
    # создаете экземпляр класса, вы создаете объект, который наследует свойства и методы, определенные в этом классе.
    # Этот объект считается экземпляром данного класса.

    class Meta:
        model = Subscriptions
        fields = ('id', 'plan_id', 'client_name', 'email', 'plan', 'price')




