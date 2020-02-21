import datetime
from operator import itemgetter

from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, get_user
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import render, redirect
from rest_framework import viewsets

from roulettecounter.serializers import UserSerializer
from . import helper
from .models import Session, NumberShown, NumberStat, BoardStat


# Create your views here.
def mobile_request(request):
    context = {}
    current_session = Session.get_current_session(request)

    if not Session.is_in_session(request):
        return render(request=request, template_name="roulettecounter/mobile.html", context=context)

    messages.info(request,
                  f"In session started on {current_session.date_start.strftime('%a %I:%M%p (%d/%m)')}")

    # Populate context
    context['currentSession'] = current_session

    # Required for visualization
    context['labels'], context['data'] = get_hot_numbers(request, current_session, limit=10)

    context['history'] = NumberShown.objects.filter(session=current_session).order_by('-date')

    return render(request=request, template_name="roulettecounter/mobile.html", context=context)


def home_request(request):
    # We start a session automatically
    if not Session.is_in_session(request):
        start_session_request(request)

    session = Session.get_current_session(request)

    context = {"numbers": NumberStat.objects.filter(session=session),
               "board_stat": BoardStat.objects.get(id=session.board_stat.pk),
               'history': NumberShown.objects.filter(session=session).order_by('-date')}

    return render(request, "roulettecounter/home.html", context=context)


def history_request(request):
    if not request.user.is_authenticated:
        messages.error(request, "Must be logged in to show history.")
        return redirect("roulettecounter:home")

    context = {}
    context["sessions"] = []
    sessions = Session.objects.filter(user=get_user(request)).order_by('-date_end')
    for session in sessions:
        labels, data = get_hot_numbers(request, session)
        context["sessions"].append([session, labels, data])
        print(labels)
        print(data)

    return render(request=request, template_name="roulettecounter/history.html", context=context)


def number_request(request, number):
    if request.method == "POST":
        if 0 <= number <= 36:
            if Session.is_in_session(request):
                session = Session.get_current_session(request)
                number_stat = NumberStat.objects.get(session=session, number=number)
                NumberShown.create(number_stat, session)
            else:
                messages.error(request, "Must be in a session to add numbers.")

    return redirect("roulettecounter:home")


def delete_most_recent_request(request):
    if request.method == "POST":
        if Session.is_in_session(request):
            deleted_number = delete_last_number(Session.get_current_session(request))
            if deleted_number is not None:
                messages.info(request, f"Number '{deleted_number}' has been deleted.")
            else:
                messages.info(request, "No numbers were deleted.")
        else:
            messages.error(request, "Must be in a session to delete numbers.")

    return redirect("roulettecounter:home")


def signup(request):
    context = {}
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"New Account Created: {username}")
            login(request, user)
            messages.info(request, f"You are now logged in as ''{username}''")
            return redirect("roulettecounter:home")
        else:
            messages.error(request, ",".join(form.error_messages))

    form = UserCreationForm()
    context["form"] = form
    return render(request, "roulettecounter/register.html", context=context)


# def visualize(request):
#     context = {}
#     currentSession = get_current_session(request)
#     if currentSession is not None:
#
#         hotNumbers = []
#         for i in range(0, 37):
#             count = Number.objects.filter(session=currentSession, number=i).count()
#             if count != 0:
#                 hotNumbers.append((i, count))
#
#         hotNumbers.sort(key=itemgetter(1), reverse=True)
#
#         context['labels'] = [e[0] for e in hotNumbers]
#         context['data'] = [e[1] for e in hotNumbers]
#         print(context['labels'])
#         print(context['data'])
#     else:
#         context['infoMessage'] = "No numbers to visualize."
#
#     return render(request=request, template_name="roulettecounter/visualize.html", context=context)

def get_hot_numbers(request, session, limit=37):
    hotNumbers = []
    for i in range(0, 37):
        count = NumberShown.objects.filter(session=session, number=i).count()
        if count != 0:
            hotNumbers.append((i, count))

    hotNumbers.sort(key=itemgetter(1), reverse=True)

    labels = [e[0] for e in hotNumbers][:limit]
    data = [e[1] for e in hotNumbers][:limit]

    return labels, data


def logout_request(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("roulettecounter:home")


def login_request(request):
    context = {}
    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as ''{username}''")
                return redirect("roulettecounter:home")
            else:
                messages.error = "Invalid username or password"
        else:
            messages.error = ",".join(form.error_messages)

    form = AuthenticationForm()
    context["form"] = form
    return render(request, "roulettecounter/login.html", context=context)


def delete_most_recent_number(request):
    context = {}
    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as ''{username}''")
                return redirect("roulettecounter:home")
            else:
                messages.error = "Invalid username or password"
        else:
            messages.error = ",".join(form.error_messages)

    form = AuthenticationForm()
    context["form"] = form
    return render(request, "roulettecounter/login.html", context=context)


def start_session_request(request):
    # Because we can start a new session, before the old one has finished, end the old one before starting the new one
    if Session.is_in_session(request):
        Session.get_current_session(request).end()

    user = get_user(request)
    if user.is_anonymous:
        user = None

    session = Session.create(user)
    session.save()

    return redirect("roulettecounter:home")


def end_session_request(request):
    if not Session.is_in_session(request):
        return JsonResponse({"error_message": "Session cannot be ended, you are currently not in a session."})

    Session.get_current_session(request).end()

    return redirect("roulettecounter:home")


def delete_last_number(current_session):
    try:
        numberObj = NumberShown.objects.filter(session=current_session).latest('date')
        number = numberObj.number
        numberObj.delete()
        return number
    except NumberShown.DoesNotExist:
        return None


def analytics_request(request):
    current_session = Session.get_current_session(request)
    if current_session is None:
        messages.error(request, "Must be in session to use analytics.")
        return redirect("roulettecounter:home")

    # { number -> percentage times occurred }
    # out of a sample size of...
    context = {}

    # Populate our numbers
    numbers_numbers = {}
    numbers_count = {}
    other_count = {
        "red": 0,
        "black": 0,
        "odd": 0,
        "even": 0,
        "1_12": 0,
        "13_24": 0,
        "25_36": 0,
        "row_one": 0,
        "row_two": 0,
        "row_three": 0,
        "1_18": 0,
        "19_36": 0
    }
    for i in range(0, 37):
        # numbers_numbers[i] = Number.objects.filter(session=get_current_session(request), number=i)
        count = NumberShown.objects.filter(session=current_session, number=i).count()

        numbers_count[i] = count

        if NumberShown.is_red(i):
            other_count["red"] += count
        elif NumberShown.is_black(i):
            other_count["black"] += count

        if NumberShown.is_even(i):
            other_count["even"] += count
        elif NumberShown.is_odd(i):
            other_count["odd"] += count

        if NumberShown.is_in_1_12(i):
            other_count["1_12"] += count
        elif NumberShown.is_in_13_24(i):
            other_count["13_24"] += count
        elif NumberShown.is_in_25_36(i):
            other_count["25_36"] += count

        if NumberShown.is_in_1_18(i):
            other_count["1_18"] += count
        elif NumberShown.is_in_19_36(i):
            other_count["19_36"] += count

        if NumberShown.is_in_row_one(i):
            other_count["row_one"] += count
        elif NumberShown.is_in_row_two(i):
            other_count["row_two"] += count
        elif NumberShown.is_in_row_three(i):
            other_count["row_three"] += count

    total = sum(numbers_count.values())
    numbers_percentages = {}
    other_percentages = {
        "red": helper.to_percent(other_count["red"] / total),
        "black": helper.to_percent(other_count["black"] / total),
        "odd": helper.to_percent(other_count["odd"] / total),
        "even": helper.to_percent(other_count["even"] / total),
        "1_12": helper.to_percent(other_count["1_12"] / total),
        "13_24": helper.to_percent(other_count["13_24"] / total),
        "25_36": helper.to_percent(other_count["25_36"] / total),
        "row_one": helper.to_percent(other_count["row_one"] / total),
        "row_two": helper.to_percent(other_count["row_two"] / total),
        "row_three": helper.to_percent(other_count["row_three"] / total),
        "1_18": helper.to_percent(other_count["1_18"] / total),
        "19_36": helper.to_percent(other_count["19_36"] / total)
    }

    for k, v in numbers_count.items():
        numbers_percentages[k] = helper.to_percent(v / total)

    context["numbers"] = numbers_percentages
    context["other_percentages"] = other_percentages

    return render(request, "roulettecounter/analytics.html", context=context)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

