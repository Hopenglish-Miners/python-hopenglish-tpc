from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
# from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import JsonResponse
import json
# from django.forms.util import ErrorList


# from .models import Greeting
from .forms import DocumentForm

# Create your views here.
def index(request):
    # return HttpResponse('Hello from Python!')
    form = DocumentForm()

    # return render(request, 'index.html')
    if request.method == 'GET':
        return render_to_response(
            'index.html',
            {'form': form},
            context_instance=RequestContext(request)
        )
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        errorMessages = ""

        if form.is_valid():
            uploadedFile = request.FILES['docfile']
            try:
                jsonFile = json.load(uploadedFile)
            except ValueError, e:
                form.errors["Selected file is not JSON"] = ""

            """
                Desired fields:
                chosenVideo: at least one video
                listenScore: at least one listen score per video
                    postId: at least one postId for the chosen video
                    score: at least one score
            """
            # videosSent = []
            videosSent = {}
            if "chosenVideo" not in jsonFile.keys():
                form.errors["chosenVideo key is not in JSON"] = ""
            else:
                if len(jsonFile["chosenVideo"]) == 0:
                    form.errors["Please send at least one video in the \"chosenVideo\" key "] = ""
                else:
                    for video in jsonFile["chosenVideo"]:
                        # videosSent.append(int(video))
                        videosSent[video] = 0
            if "listenScore" not in jsonFile.keys():
                form.errors["listenScore key is not in JSON"] = ""
            else:
                if len(jsonFile["listenScore"]) == 0:
                    form.errors["Please don't send an empty \"listenScore\" key "] = ""
                else:
                    postScores = {}
                    for listSc in jsonFile["listenScore"]:
                        if "postId" in listSc.keys():
                            if "score" in listSc.keys():
                                if listSc["postId"] in videosSent.keys():
                                    videosSent[listSc["postId"]] = 1
                                else:
                                    form.errors["There is an object with postId %d that is not in the chosenVideos key" % (listSc["postId"])] = ""
                            else:
                                form.errors["There is an object with postId %d that has no score" % (listSc["postId"])] = ""
                        else:
                            form.errors["There is a listenScore item without \"postId\" key in your file"] = ""

            for key, value in videosSent.iteritems():
                if value == 0:
                    form.errors["The video %d has no listenScore" % key] = ""

        else:
            form.errors["Form is not valid"] = ""

        return render_to_response(
            'index.html',
            {'form': form},
            context_instance=RequestContext(request)
        )
