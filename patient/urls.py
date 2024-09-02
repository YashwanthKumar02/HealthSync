from django.urls import path
from .views import RegisterView, LoginView, LogoutView
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView, LoginView, LogoutView,
    DoctorListView, DoctorDetailView,
    PatientListView, PatientDetailView,
    PatientRecordListView, PatientRecordDetailView,
    DepartmentListView, DepartmentDoctorsView, DepartmentPatientsView
)

urlpatterns = [
    path('user/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/register/', RegisterView.as_view(), name='register'),
    path('user/login/', LoginView.as_view(), name='login'),
    path('user/logout/', LogoutView.as_view(), name='logout'),

    path('doctors/', DoctorListView.as_view(), name='doctor-list'),
    path('doctors/<int:pk>/', DoctorDetailView.as_view(), name='doctor-detail'),

    path('patients/', PatientListView.as_view(), name='patient-list'),
    path('patients/<int:pk>/', PatientDetailView.as_view(), name='patient-detail'),

    path('patient_records/', PatientRecordListView.as_view(), name='patient-record-list'),
    path('patient_records/<int:pk>/', PatientRecordDetailView.as_view(), name='patient-record-detail'),

    path('departments/', DepartmentListView.as_view(), name='department-list'),
    path('departments/<int:pk>/doctors/', DepartmentDoctorsView.as_view(), name='department-doctors'),
    path('departments/<int:pk>/patients/', DepartmentPatientsView.as_view(), name='department-patients'),

]
