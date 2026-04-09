from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Profile

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['user_id'] = str(user.id)
        token['role'] = user.role
        token['status'] = user.status

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        if self.user.status != 'active':
            raise serializers.ValidationError("User is suspended or banned.")

        data["user_id"] = str(self.user.id)
        data["role"] = self.user.role
        data["status"] = self.user.status

        return data


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['nickname', 'realName', 'age', 'gender', 'description', 'avatar', 'frame', 'background', 'countrie', 'level']