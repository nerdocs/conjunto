from django.db import models

from conjunto.models import SingletonModel


class SingletonTestModel(SingletonModel):
    app_label = "test_app"


class Person(models.Model):
    name = models.CharField(max_length=40)
