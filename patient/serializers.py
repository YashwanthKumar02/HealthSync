from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .models import PatientRecord, Department, CustomUser

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'role', 'department')
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), required=False)

    class Meta:
        model = User
        fields = ('username', 'password', 'role', 'department')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            role=validated_data['role'],
            department=validated_data.get('department')
        )
        return user
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)

        if user and user.is_active:
            return user
        raise serializers.ValidationError('Invalid credentials')
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'role', 'department')

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {
        'invalid_token': ('The token is invalid or expired.'),
        'token_not_provided': ('No token provided.')
    }

    def validate(self, attrs):
        self.token = attrs.get('refresh')

        if not self.token:
            self.fail('token_not_provided')

        return attrs

    def save(self, **kwargs):
        try:
            refresh_token = RefreshToken(self.token)
            refresh_token.blacklist()  # This works if blacklisting is enabled
        except TokenError:
            self.fail('invalid_token')

class PatientRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientRecord
        fields = '__all__'
    def validate(self, attrs):
        user = self.context['request'].user
        if user.role == 'doctor':
            if user.department != attrs.get('department'):
                raise serializers.ValidationError("Doctor can only access records from their own department.")
        return attrs

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'
