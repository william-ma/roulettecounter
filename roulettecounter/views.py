import datetime
from operator import itemgetter

from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, get_user
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect

from .models import Session, Number


# Create your views here.
def home(request):
    context = {}
    currentSession = get_current_session(request)

    if is_in_session(request):
        messages.info(request, f"Currently in a session started on {currentSession.date_start}")

    # Populate context
    context['currentSession'] = currentSession

    # Build our numbers | count
    numbers = {}
    for number in Number.objects.filter(session=currentSession):
        if not numbers.get(number.number, False):
            numbers[number.number] = number.count(currentSession)

        # Show top 5 for now. Currently not working...
        # if len(numbers) == 5:
        #    break
    context = getHotNumbers(request, context)

    context['numbers'] = numbers
    context['history'] = Number.objects.filter(session=currentSession).order_by('-date')

    return render(request=request, template_name="roulettecounter/home.html", context=context)


def number_request(request, number):
    if request.method == "POST":
        if number < 0 or number > 36:
            messages.error(request, "Number must be between 0 and 36.")

        if is_in_session(request):
            number = createNumber(get_current_session(request), number)
            messages.info(request, f"'{number}' was added.")
        else:
            messages.error(request, "Must be in a session to add numbers.")

    return redirect("roulettecounter:home")


def delete_most_recent_request(request):
    if request.method == "POST":
        if is_in_session(request):
            deletedNumber = deleteLastNumber(get_current_session(request))
            if deletedNumber is not None:
                messages.info(request, f"Number '{deletedNumber}' has been deleted.")
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
            return redirect("roulettecounter:home")
            messages.info(request, f"You are now logged in as ''{username}''")
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

def getHotNumbers(request, context):
    currentSession = get_current_session(request)
    if currentSession is not None:

        hotNumbers = []
        for i in range(0, 37):
            count = Number.objects.filter(session=currentSession, number=i).count()
            if count != 0:
                hotNumbers.append((i, count))

        hotNumbers.sort(key=itemgetter(1), reverse=True)

        context['labels'] = [e[0] for e in hotNumbers][:10]
        context['data'] = [e[1] for e in hotNumbers][:10]
        print(context['labels'])
        print(context['data'])
    else:
        context['infoMessage'] = "No numbers to visualize."

    return context


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


def deleteMostRecentNumber(request):
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


def get_current_session(request):
    try:
        user = get_user(request)
        if user.is_anonymous:
            user = None

        session = Session.objects.filter(user=user).latest('date_start')
        if session.date_end == None:
            return session
    except Session.DoesNotExist:
        pass

    return None


def is_in_session(request):
    session = get_current_session(request)
    if session:
        return True
    else:
        return False


def start_session_request(request):
    if not is_in_session(request):
        user = get_user(request)
        if user.is_anonymous:
            user = None
        Session(
            date_start=datetime.datetime.now(),
            date_end=None,
            user=user
        ).save()
    else:
        messages.error(request, "Already in a session.")
    return redirect("roulettecounter:home")


def end_session_request(request):
    session = get_current_session(request)
    if session:
        session.date_end = datetime.datetime.now()
        session.save()
    return redirect("roulettecounter:home")


def createNumber(currentSession, number):
    numberObj = Number(number=number, date=datetime.datetime.now(), session=currentSession)
    numberObj.save()
    return numberObj.number


def deleteLastNumber(currentSession):
    try:
        numberObj = Number.objects.filter(session=currentSession).latest('date')
        number = numberObj.number
        numberObj.delete()
        return number
    except Number.DoesNotExist:
        return None
