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


def mobile_request(request):
    # We start a session automatically
    if not Session.is_in_session(request):
        start_session_request(request)

    session = Session.get_current_session(request)
    context = {'currentSession': session,
               # Labels and Data are the lists used by ChartJS for visualization
               'labels': get_hot_numbers(request, session, limit=10)[0],
               'data': get_hot_numbers(request, session, limit=10)[1],
               'history': NumberShown.objects.filter(session=session).order_by('-date')
               }

    return render(request, "roulettecounter/mobile.html", context=context)


def home_request(request):
    # We start a session automatically
    if not Session.is_in_session(request):
        start_session_request(request)

    session = Session.get_current_session(request)

    context = {"numbers": NumberStat.objects.filter(session=session),
               "board_stat": BoardStat.objects.get(id=session.board_stat.pk),
               'history': NumberShown.objects.filter(session=session).order_by('-date')[:20]}

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

    print(request.META["HTTP_REFERER"])
    if "mobile" in request.META["HTTP_REFERER"]:
        return redirect("roulettecounter:mobile")
    else:
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

    hot_numbers = []
    for number_stat in NumberStat.objects.filter(session=session):
        if number_stat.appearances > 0:
            hot_numbers.append((number_stat.number, number_stat.appearances))

    hot_numbers.sort(key=itemgetter(1), reverse=True)

    labels = [e[0] for e in hot_numbers][:limit]
    data = [e[1] for e in hot_numbers][:limit]

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

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

