from django.db import models

# Create your models here.

class Session(models.Model):
    dateStart = models.DateTimeField()
    dateEnd = models.DateTimeField(null=True)

class Number(models.Model):
    number = models.PositiveSmallIntegerField()
    count = models.PositiveSmallIntegerField()
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

    # def __init__(self, session, number, count=0):
    #     self.session = session
    #     self.number = number
    #     self.count = count
