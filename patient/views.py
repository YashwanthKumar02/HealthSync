from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin
from .serializers import (
    UserRegisterSerializer, UserLoginSerializer, UserSerializer,
    LogoutSerializer, PatientRecordSerializer, DepartmentSerializer
)
from .models import PatientRecord, Department
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView


# from rest_framework import generics, status
# from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model, authenticate
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserSerializer, LogoutSerializer, DepartmentSerializer, PatientRecordSerializer
from .models import PatientRecord, Department

User = get_user_model()

# User Registration
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        response_data = {
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'department': user.department.id if user.department else None
            }
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

# User Login
class LoginView(TokenObtainPairView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        response_data = {
            'refresh': str(refresh),
            'access': access_token,
            'user': UserSerializer(user).data
        }

        return Response(response_data, status=status.HTTP_200_OK)

# User Logout
class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response_data = {
            'message': 'User logged out successfully'
        }

        return Response(response_data, status=status.HTTP_204_NO_CONTENT)
    
class DepartmentListCreateView(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return super().get_permissions()
    
class DepartmentDoctorsView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        department_id = self.kwargs['pk']
        return User.objects.filter(department_id=department_id, role='doctor')

class DepartmentPatientsView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        department_id = self.kwargs['pk']
        return User.objects.filter(department_id=department_id, role='patient')

# Retrieve all doctors
class DoctorListView(generics.ListCreateAPIView):
    queryset = User.objects.filter(role='doctor')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role != 'doctor':
            self.permission_denied(self.request)
        serializer.save()

# Retrieve a particular doctor
class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.filter(role='doctor')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if obj != self.request.user and self.request.user.role != 'superuser':
            self.permission_denied(self.request)
        return obj

# Retrieve all patients
class PatientListView(generics.ListCreateAPIView):
    queryset = User.objects.filter(role='patient')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role != 'doctor':
            self.permission_denied(self.request)
        serializer.save()

# Retrieve a particular patient
class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.filter(role='patient')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if obj != self.request.user and self.request.user.role != 'superuser' and obj not in self.request.user.get_related_patients():
            self.permission_denied(self.request)
        return obj
from rest_framework_simplejwt.authentication import JWTAuthentication

class PatientRecordListCreateView(generics.ListCreateAPIView):
    serializer_class = PatientRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'doctor':
            return PatientRecord.objects.filter(department=user.department)
        elif user.role == 'patient':
            return PatientRecord.objects.filter(patient=user)
        return PatientRecord.objects.none()

# Retrieve all patient records
class PatientRecordListView(generics.ListCreateAPIView):
    serializer_class = PatientRecordSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'doctor':
            return PatientRecord.objects.filter(department=user.department)
        elif user.role == 'patient':
            return PatientRecord.objects.filter(patient=user)
        return PatientRecord.objects.none()  # No access for other roles

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'doctor':
            serializer.save(doctor=user, department=user.department)
        elif user.role == 'patient':
            serializer.save(patient=user)
from django.core.exceptions import PermissionDenied
# Retrieve a particular patient record
class PatientRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PatientRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'doctor':
            return PatientRecord.objects.filter(department=user.department)
        elif user.role == 'patient':
            return PatientRecord.objects.filter(patient=user)
        return PatientRecord.objects.none()

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        if user.role == 'doctor' and obj.department != user.department:
            raise PermissionDenied("You do not have permission to access this record.")
        if user.role == 'patient' and obj.patient != user:
            raise PermissionDenied("You do not have permission to access this record.")
        return obj

# Retrieve all departments
class DepartmentListView(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


# Retrieve a specific department
class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


# Retrieve doctors in a particular department
class DepartmentDoctorsView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        department_id = self.kwargs.get('pk')
        department = Department.objects.filter(id=department_id).first()
        if not department:
            self.permission_denied(self.request)
        if self.request.user.role != 'doctor' or department != self.request.user.department:
            self.permission_denied(self.request)
        return User.objects.filter(role='doctor', department=department)

# Retrieve patients in a particular department
class DepartmentPatientsView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        department_id = self.kwargs.get('pk')
        department = Department.objects.filter(id=department_id).first()
        if not department:
            self.permission_denied(self.request)
        if self.request.user.role != 'doctor' or department != self.request.user.department:
            self.permission_denied(self.request)
        return User.objects.filter(role='patient', department=department)
