from django.db import models
import datetime
from django.contrib.auth.models import User
from enum import Enum


class Session(models.Model):
    date_start = models.DateTimeField()
    date_end = models.DateTimeField(null=True)
    # TEMPORARY! Allow user to be null to support guests. This is TEMPORARY!
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)


# Represents each time a number appears
class Number(models.Model):
    class Color(Enum):
        GREEN = "GREEN"
        RED = "RED"
        BLACK = "BLACK"

    color_mappings = {
        0: Color.GREEN,
        1: Color.RED,
        2: Color.BLACK,
        3: Color.RED,
        4: Color.BLACK,
        5: Color.RED,
        6: Color.BLACK,
        7: Color.RED,
        8: Color.BLACK,
        9: Color.RED,
        10: Color.BLACK,
        11: Color.BLACK,
        12: Color.RED,
        13: Color.BLACK,
        14: Color.RED,
        15: Color.BLACK,
        16: Color.RED,
        17: Color.BLACK,
        18: Color.RED,
        19: Color.RED,
        20: Color.BLACK,
        21: Color.RED,
        22: Color.BLACK,
        23: Color.RED,
        24: Color.BLACK,
        25: Color.RED,
        26: Color.BLACK,
        27: Color.RED,
        28: Color.BLACK,
        29: Color.BLACK,
        30: Color.RED,
        31: Color.BLACK,
        32: Color.RED,
        33: Color.BLACK,
        34: Color.RED,
        35: Color.BLACK,
        36: Color.RED,
    }

    number = models.PositiveSmallIntegerField()
    date = models.DateTimeField(default=datetime.datetime.now())
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

    def count(self, session):
        return Number.objects.filter(session=session, number=self.number).count()

    @staticmethod
    def is_red(number):
        return Number.color_mappings[number] == Number.Color.RED

    @staticmethod
    def is_black(number):
        return Number.color_mappings[number] == Number.Color.BLACK

    @staticmethod
    def is_green(number):
        return Number.color_mappings[number] == Number.Color.GREEN

    @staticmethod
    def is_odd(number):
        return not Number.is_even(number)

    @staticmethod
    def is_even(number):
        return number != 0 and number % 2 == 0

    @staticmethod
    def is_in_1_12(number):
        return 1 <= number <= 12

    @staticmethod
    def is_in_13_24(number):
        return 13 <= number <= 24

    @staticmethod
    def is_in_25_36(number):
        return 25 <= number <= 36

    @staticmethod
    def is_in_1_18(number):
        return 1 <= number <= 18

    @staticmethod
    def is_in_19_36(number):
        return 19 <= number <= 36

    @staticmethod
    def is_in_row_one(number):
        return number % 3 == 1

    @staticmethod
    def is_in_row_two(number):
        return number % 3 == 2

    @staticmethod
    def is_in_row_three(number):
        return number != 0 and number % 3 == 0
