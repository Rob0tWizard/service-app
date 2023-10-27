from django.db import models
from django.contrib.auth.models import User



class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
# OneToOneField() означает к каждому юзеру соответствует моддель client
# Protect означает когда будем удалять юзера, проверит нет ли связей модели client и если есть не позволит удалит
    company_name=models.CharField(max_length=100)
    full_addres=models.CharField(max_length=100)
#просто поле чтоб не было пусто и скучно