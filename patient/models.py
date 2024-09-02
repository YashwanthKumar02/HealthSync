from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
        ('superuser', 'Superuser')
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.username
    

class Department(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    diagnostics = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    specialization = models.CharField(max_length=100, blank=True, null=True)


    def __str__(self):
        return self.name

class PatientRecord(models.Model):
    record_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='patient_records')
    created_date = models.DateField(auto_now_add=True)
    diagnostics = models.TextField()
    observations = models.TextField(blank=True, null=True)
    treatments = models.TextField(blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    misc = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Record for {self.patient.username} by {self.doctor.username}'
    
