from django.db import models

# Create your models here.

class Session(models.Model):
    dateStart = models.DateTimeField()
    dateEnd = models.DateTimeField()

class Number(models.Model):
    number = models.PositiveSmallIntegerField()
    count = models.PositiveSmallIntegerField()
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
