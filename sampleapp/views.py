from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth import authenticate

import os
import shutil
from prediction_Validation_Insertion import pred_validation
from trainingModel import trainModel
from training_Validation_Insertion import train_validation
from predictFromModel import prediction
import json

from .models import uploadtrainfile,uploadpredictfile

# from . models import myuploadfile
# Create your views here.

import mimetypes

def download_file(request):
    # fill these variables with real values
    fl_path = 'Prediction_Output_File/Predictions.csv'
    filename = 'predictions.csv'
    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    print(os.path.exists('Prediction_Output_File/Predictions.csv'))
    fl = open(fl_path, 'r')
    mime_type, _ = mimetypes.guess_type(fl_path)
    response = HttpResponse(fl, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response

def send_train_files(request):
    if request.method == "POST":
        name = request.POST.get("filename")
        myfile = request.FILES.getlist("uploadfiles")
        path = 'media/'
        if os.path.isdir(path + 'training_files/'):
            shutil.rmtree(path + 'training_files/')
        for f in myfile:
            uploadtrainfile(f_name=name,myfiles=f).save()
        return render(request,"train.html")

def send_predict_files(request):
    if request.method == "POST":
        name = request.POST.get("filename")
        myfile = request.FILES.getlist("uploadfiles")
        path = 'media/'
        if os.path.isdir(path + 'prediction_files/'):
            shutil.rmtree(path + 'prediction_files/')
        for f in myfile:
            uploadpredictfile(f_name=name,myfiles=f).save()
        return render(request,"predict.html")

def home(request):
    return render(request,'home.html') 

def train_or_predict(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        print(password)
        print("username : {}".format(username))
        try:
            user = User.objects.get(username=username)
        except:
            return render(request,'login_error.html')
        print("user : {}".format(user))
        print(user.is_superuser)
        if user.is_superuser:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                return render(request,'upload_train.html')
            else:
                return render(request,'login_error.html')
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                return render(request,'upload_predict.html')
            else:
                return render(request,'login_error.html')
            

def train(request):
        path = "media/training_files/"
        try:
            train_valObj = train_validation(path) #object initialization

            train_valObj.train_validation()#calling the training_validation function


            trainModelObj = trainModel() #object initialization
            trainModelObj.trainingModel() #training the model for the files in the table
            return render(request,'train_success.html')

        except ValueError:

                return HttpResponse("Error Occurred! %s" % ValueError)

        except KeyError:

                return HttpResponse("Error Occurred! %s" % KeyError)

        except Exception as e:

                return HttpResponse("Error Occurred! %s" % e)

def predict(request):
        path = "media/prediction_files/"
        try:
            
            pred_val = pred_validation(path) #object initialization

            pred_val.prediction_validation() #calling the prediction_validation function

            pred = prediction(path) #object initialization

            # predicting for dataset present in database
            path=pred.predictionFromModel()
            # return HttpResponse("Prediction File created at !!!"  +str(path) +'and few of the predictions are '+str(json.loads(json_predictions) ))
            return render(request,'download_predictions.html')
        except ValueError:
            return HttpResponse("Error Occurred! %s" %ValueError)
        except KeyError:
            return HttpResponse("Error Occurred! %s" %KeyError)
        except Exception as e:
            return HttpResponse("Error Occurred! %s" %e)
    






# from django.shortcuts import render
# from django.http import HttpResponse
# from django.contrib import messages

# import os
# from prediction_Validation_Insertion import pred_validation
# from trainingModel import trainModel
# from training_Validation_Insertion import train_validation
# from predictFromModel import prediction
# import json

# Create your views here.

# def home(request):
#     return render(request,'home.html')
# def train(request):
#     if request.method=="POST":
#         path = request.POST.get('path')
#         try:
#             train_valObj = train_validation(path) #object initialization

#             train_valObj.train_validation()#calling the training_validation function


#             trainModelObj = trainModel() #object initialization
#             trainModelObj.trainingModel() #training the model for the files in the table
#             messages.success(request,"%s Training Successful..!"%(path))

#         except ValueError:

#                 return HttpResponse("Error Occurred! %s" % ValueError)

#         except KeyError:

#                 return HttpResponse("Error Occurred! %s" % KeyError)

#         except Exception as e:

#                 return HttpResponse("Error Occurred! %s" % e)
#     return render(request,'train.html')

# def predict(request):
#     if request.method=="POST":
#         try:
#             path = request.POST.get('path')

#             pred_val = pred_validation(path) #object initialization

#             pred_val.prediction_validation() #calling the prediction_validation function

#             pred = prediction(path) #object initialization

#             # predicting for dataset present in database
#             path,json_predictions = pred.predictionFromModel()
#             return HttpResponse("Prediction File created at !!!"  +str(path) +'and few of the predictions are '+str(json.loads(json_predictions) ))
#         except ValueError:
#             return HttpResponse("Error Occurred! %s" %ValueError)
#         except KeyError:
#             return HttpResponse("Error Occurred! %s" %KeyError)
#         except Exception as e:
#             return HttpResponse("Error Occurred! %s" %e)
#     return render(request,'predict.html')
    
    