from django.shortcuts import render
from .models import Session, Number
import datetime

# Create your views here.
def homepage(request):
    context = {}

    currentSession = None
    if request.method == "POST":
        if request.POST.get('start_session', False):
            if not isInASession():
                currentSession = startSession()
        elif request.POST.get('finish_session', False):
            if isInASession():
                finishSession()
    else:
        # should i programmatically... generate the html? i suppose i do need to pass the "count" to that website to actually show the count... otherwise it's kind of useless...
        # so i'll need to pass all 37 numbers into the field into context.
        print("method: " + request.method)
        # hold a variable... whether i'm in a session or not...
        # pass that variable onwards?
        # go to db... get the last session and see if the date has ended...
        try:
            currentSession = Session.objects.latest('dateStart')
        except Session.DoesNotExist:
            pass
            # inSession = currentSession.dateEnd != None
            # if inSession:
            #     context['inSession'] = inSession

    context['currentSession'] = currentSession

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
    session = getCurrentSession()
    if session:
        session.dateEnd = datetime.datetime.now()
        session.save()
