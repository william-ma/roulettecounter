from django.test import TestCase

# Create your tests here.
from roulettecounter.models import NumberStat, Session, NumberShown


class NumberStatTestCase(TestCase):

    def test(self):
        session = Session.create(None)
        self.assertIsNone(session.date_end)
        self.assertEqual(NumberStat.objects.filter(session=session).count(), 37)

        numbers = NumberStat.objects.filter(session=session).order_by("number")

        number_zero = numbers[0]
        number_one = numbers[1]
        number_six = numbers[6]
        self.assertTrue(numbers[1].is_red)
        self.assertEqual(numbers[1].number, 1)
        self.assertTrue(number_six.is_black)
        self.assertEqual(number_one.appearances, 0)

        self.assertFalse(number_zero.is_even)
        self.assertFalse(number_zero.is_odd)
        self.assertFalse(number_zero.is_in_first_row)
        self.assertFalse(number_zero.is_in_first_col)
        self.assertFalse(number_zero.is_in_first_half)

        self.assertTrue(number_one.is_in_first_half)
        self.assertTrue(number_one.is_in_first_col)
        self.assertTrue(number_one.is_in_first_row)
        self.assertFalse(number_one.is_in_second_half)
        self.assertFalse(number_one.is_in_second_row)
        self.assertFalse(number_one.is_in_third_row)
        self.assertFalse(number_one.is_in_second_col)
        self.assertFalse(number_one.is_in_third_col)

        self.assertTrue(number_six.is_even)
        self.assertFalse(number_six.is_odd)

        NumberShown.create(number_zero)
        NumberShown.create(number_zero)
        NumberShown.create(number_zero)

        self.assertEqual(number_zero.appearances, 3)

        NumberShown.create(number_zero)
        NumberShown.create(number_zero)
        self.assertEqual(number_zero.appearances, 5)

        NumberShown.create(number_one)
        self.assertEqual(number_one.appearances, 1)
