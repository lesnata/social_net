from rest_framework import serializers
from .models import Post, Like
from django.contrib.auth import get_user_model


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = "__all__"


#   from django.contrib.auth.models import User
#   class RegistrationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = '__all__'


User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    password2 = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        label="Confirm password"
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password2",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        username = validated_data["username"]
        email = validated_data["email"]
        password = validated_data["password"]
        password2 = validated_data["password2"]
        if (email
            and User.objects.filter(email=email)
                .exclude(username=username)
                .exists()):
            raise serializers.ValidationError(
                {"email": "Email addresses must be unique."})
        if password != password2:
            raise serializers.ValidationError({"password": "The two passwords differ."})
        user = User(username=username, email=email)
        # Ensure your password is being hashed before it is stored in your db
        user.set_password(password)
        user.save()
        return user
