from django.db import models

# Create your models here.

class uploadtrainfile(models.Model):
    f_name = models.CharField(max_length=255)
    myfiles = models.FileField(upload_to="training_files")

    def __str__(self):
        return self.f_name

class uploadpredictfile(models.Model):
    f_name = models.CharField(max_length=255)
    myfiles = models.FileField(upload_to="prediction_files")

    def __str__(self):
        return self.f_name
