# from django.urls import path

# from.views import train,home,predict

# urlpatterns = [
#     path('',home,name="home"),
#     path('train',train,name="train"),
#     path('predict',predict,name="predict"),
# ]

from django.urls import path

from.views import home,train_or_predict,train,predict,send_predict_files,send_train_files,download_file

from django.contrib.auth import views as auth_views

urlpatterns = [
	path('',home,name="home"),
	path('login/', auth_views.LoginView.as_view(template_name='login.html'),name="login"),
	path('train_or_predict/',train_or_predict,name="train_or_predict"),
	path('logout/',auth_views.LogoutView.as_view(template_name='logout.html'),name="logout"),
	path("upload_train",send_train_files,name="train_uploads"),
	path("upload_predict",send_predict_files,name="predict_uploads"),
	path('train',train,name="train"),
	path('predict',predict,name="predict"),
	path('downloading/', download_file,name="download_file"),
	]


