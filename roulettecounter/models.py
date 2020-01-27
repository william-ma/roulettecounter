from django.db import models
import datetime

# Create your models here.

class Session(models.Model):
    dateStart = models.DateTimeField()
    dateEnd = models.DateTimeField(null=True)

# Represents each time a number appears
class Number(models.Model):
    number = models.PositiveSmallIntegerField()
    date = models.DateTimeField(default=datetime.datetime.now())
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

    def count(self):
        return Number.objects.filter(number=self.number).count()
