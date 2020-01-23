from django.shortcuts import render
from .models import Session, Number
import datetime

# Create your views here.
def homepage(request):
    context = {}

    currentSession = None
    if request.method == "POST":
        if request.POST.get('start_session', False):
            currentSession = Session()
            currentSession.dateStart = datetime.datetime.now()
            # print("Am i in hte right place?")
            # TODO if we're currently in a session... do not start another one...
            # the moment we have created a session... we got to save it...
            # create a bunch of Number fields...
            # inc them...
            # should i programmatically... generate the html? i suppose i do need to pass the "count" to that website to actually show the count... otherwise it's kind of useless...
            # so i'll need to pass all 37 numbers into the field into context. 
        elif request.POST.get('finish_session', False):
            # only be able to finish a session if... we are in a session...
            try:
                currentSession = Session.objects.latest('dateStart')
                currentSession.dateEnd = datetime.datetime.now()
            except Session.DoesNotExist:
                pass
    else:
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
