from rest_framework import serializers
from .models import GroupMessage, ChatGroup
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

# ✅ Fix: Define UserSerializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    conpassword = serializers.CharField(write_only=True)  # ✅ Add this since it's used in `create()`

    def validate(self, data):
        if data['password'] != data['conpassword']:
            raise serializers.ValidationError("Passwords do not match")
        
        if User.objects.filter(username=data['username'].lower()).exists():
            raise serializers.ValidationError("Username is already taken")

        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email is already registered")

        return data

    def create(self, validated_data):
        validated_data.pop('conpassword')

        user = User.objects.create(
            username=validated_data['username'].lower(),
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        if not User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError('User not found')
        return data

    def get_jwt_token(self, validated_data):
        user = authenticate(username=validated_data['username'], password=validated_data['password'])

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        refresh = RefreshToken.for_user(user)

        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'username': user.username,
                'email': user.email
            },
        }

class GroupMessageSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    group = serializers.SlugRelatedField(slug_field='group_name', queryset=ChatGroup.objects.all())

    class Meta:
        model = GroupMessage
        fields = ['id', 'body', 'author', 'created_at', 'group']

class ChatGroupSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)
    users_online = UserSerializer(many=True, read_only=True)

    class Meta:
        model = ChatGroup
        fields = ['id', 'group_name', 'is_private', 'members', 'users_online']
