import datetime

from django.contrib.auth import get_user
from django.contrib.auth.models import User
from django.db import models

from roulettecounter import helper

class BoardStat(models.Model):
    num_green = models.PositiveSmallIntegerField(default=0)
    num_red = models.PositiveSmallIntegerField(default=0)
    num_black = models.PositiveSmallIntegerField(default=0)
    num_even = models.PositiveSmallIntegerField(default=0)
    num_odd = models.PositiveSmallIntegerField(default=0)
    num_first_col = models.PositiveSmallIntegerField(default=0)
    num_second_col = models.PositiveSmallIntegerField(default=0)
    num_third_col = models.PositiveSmallIntegerField(default=0)
    num_first_half = models.PositiveSmallIntegerField(default=0)
    num_second_half = models.PositiveSmallIntegerField(default=0)
    num_first_row = models.PositiveSmallIntegerField(default=0)
    num_second_row = models.PositiveSmallIntegerField(default=0)
    num_third_row = models.PositiveSmallIntegerField(default=0)

    total_count = models.PositiveSmallIntegerField(default=0)

    # These should've been dictionaries
    percentage_green = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    percentage_red = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    percentage_black = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    percentage_even = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    percentage_odd = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    percentage_first_col = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    percentage_second_col = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    percentage_third_col = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    percentage_first_half = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    percentage_second_half = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    percentage_first_row = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    percentage_second_row = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    percentage_third_row = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    @classmethod
    def create(cls):
        return cls()

    def inc_or_dec(self, number_stat, amount):

        if number_stat.is_red:
            self.num_red += amount
        elif number_stat.is_black:
            self.num_black += amount
        elif number_stat.is_green:
            self.num_green += amount

        if number_stat.is_even:
            self.num_even += amount
        elif number_stat.is_odd:
            self.num_odd += amount

        if number_stat.is_in_first_col:
            self.num_first_col += amount
        elif number_stat.is_in_second_col:
            self.num_second_col += amount
        elif number_stat.is_in_third_col:
            self.num_third_col += amount

        if number_stat.is_in_first_half:
            self.num_first_half += amount
        elif number_stat.is_in_second_half:
            self.num_second_half += amount

        if number_stat.is_in_first_row:
            self.num_first_row += amount
        elif number_stat.is_in_second_row:
            self.num_second_row += amount
        elif number_stat.is_in_third_row:
            self.num_third_row += amount

        self.total_count += amount

        if self.total_count > 0:
            self.percentage_green = helper.to_percent(self.num_green / self.total_count)
            self.percentage_red = helper.to_percent(self.num_red / self.total_count)
            self.percentage_black = helper.to_percent(self.num_black / self.total_count)
            self.percentage_even = helper.to_percent(self.num_even / self.total_count)
            self.percentage_odd = helper.to_percent(self.num_odd / self.total_count)
            self.percentage_first_col = helper.to_percent(self.num_first_col / self.total_count)
            self.percentage_second_col = helper.to_percent(self.num_second_col / self.total_count)
            self.percentage_third_col = helper.to_percent(self.num_third_col / self.total_count)
            self.percentage_first_half = helper.to_percent(self.num_first_half / self.total_count)
            self.percentage_second_half = helper.to_percent(self.num_second_half / self.total_count)
            self.percentage_first_row = helper.to_percent(self.num_first_row / self.total_count)
            self.percentage_second_row = helper.to_percent(self.num_second_row / self.total_count)
            self.percentage_third_row = helper.to_percent(self.num_third_row / self.total_count)

            # Update the % for all the number_stats, since total has changed.
            for number_stat in NumberStat.objects.filter(session=number_stat.session):
                number_stat.percentage_appeared = helper.to_percent(number_stat.appearances / self.total_count)
                number_stat.save()
        else:
            self.percentage_green = 0
            self.percentage_red = 0
            self.percentage_black = 0
            self.percentage_even = 0
            self.percentage_odd = 0
            self.percentage_first_col = 0
            self.percentage_second_col = 0
            self.percentage_third_col = 0
            self.percentage_first_half = 0
            self.percentage_second_half = 0
            self.percentage_first_row = 0
            self.percentage_second_row = 0
            self.percentage_third_row = 0

            # Update the % for all the number_stats, since total has changed.
            for number_stat in NumberStat.objects.filter(session=number_stat.session):
                number_stat.percentage_appeared = 0
                number_stat.save()

        self.save()

    def inc(self, number_stat):
        self.inc_or_dec(number_stat, 1)

    def dec(self, number_stat):
        self.inc_or_dec(number_stat, -1)


"""
Each session has all the numbers attached to it. 
"""


class Session(models.Model):
    date_start = models.DateTimeField()
    date_end = models.DateTimeField(null=True, default=None)
    # TEMPORARY! Allow user to be null to support guests. This is TEMPORARY!
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    board_stat = models.ForeignKey(BoardStat, null=True, on_delete=models.CASCADE)

    @classmethod
    def create(cls, user):

        # We need to save our models beforehand... so we can set them as foreign keys for other models
        board_stat = BoardStat.create()
        board_stat.save()

        session = cls(user=user, date_start=datetime.datetime.now(), board_stat=board_stat)
        session.save()

        for i in range(0, 37):
            NumberStat.create(i, session).save()

        return session

    def is_running(self):
        return self.date_end is None

    def end(self):
        self.date_end = datetime.datetime.now()
        self.save()

    '''
    Returns the current session, otherwise returns None if we're currently not in a session
    '''

    @staticmethod
    def get_current_session(request):
        try:
            user = get_user(request)
            if user.is_anonymous:
                user = None

            # Get the last session that hasn't ended
            session = Session.objects.filter(user=user).latest('date_start')
            if session.is_running():
                return session
        except Session.DoesNotExist:
            pass

        return None

    @staticmethod
    def is_in_session(request):
        return Session.get_current_session(request) is not None


class NumberStat(models.Model):
    number = models.PositiveSmallIntegerField()
    is_green = models.BooleanField()
    is_red = models.BooleanField()
    is_black = models.BooleanField()
    is_even = models.BooleanField()
    is_odd = models.BooleanField()
    is_in_first_col = models.BooleanField()
    is_in_second_col = models.BooleanField()
    is_in_third_col = models.BooleanField()
    is_in_first_half = models.BooleanField()
    is_in_second_half = models.BooleanField()
    is_in_first_row = models.BooleanField()
    is_in_second_row = models.BooleanField()
    is_in_third_row = models.BooleanField()
    appearances = models.PositiveSmallIntegerField(default=0)
    percentage_appeared = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

    green_numbers = [0, 00]
    red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
    black_numbers = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]

    @classmethod
    def create(cls, number, session):
        number_stat = cls(number=number, session=session)

        number_stat.is_green = number in NumberStat.green_numbers
        number_stat.is_red = number in NumberStat.red_numbers
        number_stat.is_black = number in NumberStat.black_numbers

        number_stat.is_even = (number != 0 and number % 2 == 0)
        number_stat.is_odd = (number != 0 and not number_stat.is_even)

        number_stat.is_in_first_col = 1 <= number <= 12
        number_stat.is_in_second_col = 13 <= number <= 24
        number_stat.is_in_third_col = 25 <= number <= 36

        number_stat.is_in_first_half = 1 <= number <= 18
        number_stat.is_in_second_half = 19 <= number <= 36

        number_stat.is_in_first_row = (number % 3 == 1)
        number_stat.is_in_second_row = (number % 3 == 2)
        number_stat.is_in_third_row = (number != 0 and number % 3 == 0)

        return number_stat

    def inc(self):
        self.appearances += 1
        self.save()
        self.session.board_stat.inc(self)

    def dec(self):
        if self.appearances != 0:
            self.appearances -= 1
            self.save()
            self.session.board_stat.dec(self)

    def __str__(self):
        return "Session {} - {}".format(self.session.pk, self.number)


class NumberShown(models.Model):
    date = models.DateTimeField()
    number_stat = models.ForeignKey(NumberStat, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

    @classmethod
    def create(cls, number_stat, session):
        number_shown = cls(number_stat=number_stat, date=datetime.datetime.now(), session=session)
        number_shown.save()

        number_stat.inc()

        return number_shown
