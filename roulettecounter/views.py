from django.shortcuts import render
from .models import Session, Number
import datetime
from operator import itemgetter

# Create your views here.
def homepage(request):
    context = {}
    currentSession = getCurrentSession()

    if request.method == "POST":
        if request.POST.get('start_session', False):
            if not isInASession():
                currentSession = startSession()
                context['infoMessage'] = "Session started at " + str(currentSession.dateStart)
            else:
                context['infoMessage'] = "Already in a session started on " + str(currentSession.dateStart)
        elif request.POST.get('finish_session', False):
            if isInASession():
                finishedSession = finishSession()
                context['infoMessage'] = "Session ended on " + str(finishedSession.dateEnd)
            else:
                context['infoMessage'] = "No session to finish"
        elif request.POST.get('number', False):
            if isInASession() and request.POST.get('number', False):
                number = createNumber(currentSession, request.POST.get('number', False))
                context['infoMessage'] = "'" + str(number) + "' was added."
            else:
                context['infoMessage'] = "Must be in a session to use numbers."
        elif request.POST.get('delete', False):
            if isInASession():
                deletedNumber = deleteLastNumber(currentSession)
                if deletedNumber is not None:
                    context['infoMessage'] = "Number '" + str(deletedNumber) + "' has been deleted."
                else:
                    context['infoMessage'] = "No numbers were deleted."
            else:
                context['infoMessage'] = "Must be in a session to delete numbers."
    elif request.method == "GET":
        if isInASession():
            context['infoMessage'] = "Currently in a session started on " + str(currentSession.dateStart)

    # Populate context
    context['currentSession'] = currentSession

    # Build our numbers | count
    numbers = {}
    for number in Number.objects.filter(session=currentSession):
        if not numbers.get(number.number, False):
            numbers[number.number] = number.count(currentSession)

        # Show top 5 for now. Currently not working...
        #if len(numbers) == 5:
        #    break

    context['numbers'] = numbers
    context['history'] = Number.objects.filter(session=currentSession).order_by('-date')

    return render(request=request, template_name="roulettecounter/home.html", context=context)

def visualizePage(request):
    context = {}
    currentSession = getCurrentSession()
    if currentSession is not None:

        hotNumbers = []
        for i in range(0, 37):
            count = Number.objects.filter(session=currentSession, number=i).count()
            if count != 0:
                hotNumbers.append((i, count))

        hotNumbers.sort(key=itemgetter(1), reverse=True)

        context['labels'] = [e[0] for e in hotNumbers]
        context['data'] = [e[1] for e in hotNumbers]
        print(context['labels'])
        print(context['data'])
    else:
        context['infoMessage'] = "No numbers to visualize."

    return render(request=request, template_name="roulettecounter/visualize.html", context=context)

def getCurrentSession():
    try:
        session = Session.objects.latest('dateStart')
        if session.dateEnd == None:
            return session
    except Session.DoesNotExist:
        pass

    return None

def isInASession():
    session = getCurrentSession()
    if session:
        return True
    else:
        return False

def startSession():
    print("startSession()")
    session = Session()
    session.dateStart = datetime.datetime.now()
    session.dateEnd = None
    session.save()
    return session

def finishSession():
    print("finishSession()")
    session = getCurrentSession()
    if session:
        session.dateEnd = datetime.datetime.now()
        session.save()

    return session

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
