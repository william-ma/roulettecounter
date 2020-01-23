from django.shortcuts import render
from .models import Session, Number
import datetime

# Create your views here.
def homepage(request):
    context = {}
    context['sessionMessage'] = ""
    currentSession = getCurrentSession()

    if request.method == "POST":
        if request.POST.get('start_session', False):
            if not isInASession():
                currentSession = startSession()
                context['sessionMessage'] = "Session started at " + str(currentSession.dateStart)
            else:
                context['sessionMessage'] = "Already in a session started on " + str(currentSession.dateStart)
        elif request.POST.get('finish_session', False):
            if isInASession():
                finishedSession = finishSession()
                context['sessionMessage'] = "Session ended on " + str(finishedSession.dateEnd)
            else:
                context['sessionMessage'] = "No session to finish"
        elif request.POST.get('number', False):
            if isInASession():
                number = request.POST.get('number', False)
                numberObj = Number.objects.get(number=number, session=currentSession)
                numberObj.count += 1
                numberObj.save()
            else:
                context['sessionMessage'] = "Must be in a session to use numbers"
    elif request.method == "GET":
        if isInASession():
            context['sessionMessage'] = "Currently in a session started on " + str(currentSession.dateStart)

    context['currentSession'] = currentSession
    context['numbers'] = Number.objects.filter(session=currentSession)

    return render(request=request, template_name="roulettecounter/home.html", context=context)

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

    for i in range(0, 37):
        number = Number(session=session, number=i, count=0)
        number.save()

    return session

def finishSession():
    print("finishSession()")
    session = getCurrentSession()
    if session:
        session.dateEnd = datetime.datetime.now()
        session.save()

    return session
