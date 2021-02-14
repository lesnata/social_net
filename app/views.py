from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Post, Comment
from .serializers import PostSerializer, LikeSerializer, RegistrationSerializer

# Create your views here.


