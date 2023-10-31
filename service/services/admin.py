from django.contrib import admin

from services.models import Service, Plan, Subscriptions

admin.site.register(Service)
admin.site.register(Plan)               # регистрируем это для вывода в админке
admin.site.register(Subscriptions)

