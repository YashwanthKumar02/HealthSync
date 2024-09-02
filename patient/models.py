from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    role = [
        ('Doctor', 'Doctor'),
        ('Patient', 'Patient')
    ]
    role = models.CharField(max_length=10, choices=role)
    
    def __str__(self):
        return self.username

class Patient_Records(models.Model):
    record_id = models.AutoField(primary_key=True)
    patient_id = models.IntegerField()
    created_date = models.DateTimeField(auto_now_add=True)
    diagnostics = models.TextField()
    observations = models.TextField()
    treatments = models.TextField()
    department_id = models.ForeignKey('Departments', on_delete=models.CASCADE)
    misc = models.TextField()

    def __str__(self):
        return self.record_id
    
class Departments(models.Model):
    department_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    diagnostics = models.TextField()
    location = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)

    def __str__(self):
        return self.name