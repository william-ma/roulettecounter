from django.db import models
import datetime
from django.contrib.auth.models import User

class Session(models.Model):
    date_start = models.DateTimeField()
    date_end = models.DateTimeField(null=True)
    # TEMPORARY! Allow user to be null to support guests. This is TEMPORARY!
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

# Represents each time a number appears
class Number(models.Model):
    number = models.PositiveSmallIntegerField()
    date = models.DateTimeField(default=datetime.datetime.now())
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

    def count(self, session):
        return Number.objects.filter(session=session, number=self.number).count()
