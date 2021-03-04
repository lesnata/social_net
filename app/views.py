from django.http import HttpResponse
from datetime import datetime

from rest_framework.decorators import (
    api_view, permission_classes,)
from rest_framework import status
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Post, Like
from .serializers import PostSerializer, LikeSerializer, UserCreateSerializer
from django.db.models import Count
from django.contrib.auth.models import User
from django.db.models.functions import ExtractDay, ExtractMonth, ExtractYear

# Create your views here.


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def registration(request):
    """
    Route for user registration with
    issuance of JWT access & refresh tokens

    Args:
    :param request: request parameter from API.
    Required: username, email, password, password2

    Returns:
    :return: serialized data of Post object or status code
    Example: {
                "user": "Berlin",
                "refresh": "eyJ0eXAiOiJKV1QiLCJhbGci.....",
                "access": "eyJ0eXAiOiJKV1QiLCJhbGciO....."
            }
    """

    # "detail": "No active account found with the given credentials"
    # Ensure your password is being hashed before it is stored in your db

    serializer = UserCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    user = serializer.save()
    refresh = RefreshToken.for_user(user)
    res = {
        "user": user.username,
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }
    return Response(res, status.HTTP_201_CREATED)


@api_view(["GET", "POST"])
def post_collection(request):
    """
    Route for multiple Post objects - GET method
    or POST method for new Post object creation.

    Args:
    :param request: request parameter from API

    Returns:
    :return: serialized data of Post object or status code
    Example: [
                {
                    "id": 2,
                    "title": "Why “Trusting the Science” Is Complicated",
                    "post": "IT IS POSSIBLE that John Pringle’s...",
                    "slug": "admin-lesna-why-trusting-the-science-is-complicated",
                    "date_published": "2021-02-15T10:47:55.652257Z",
                    "author": 1
                }
            ]
    """

    if request.method == "GET":
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        data = {
            "author": request.user.id,
            "title": request.data.get("title"),
            "post": request.data.get("post"),
        }
        serializer = PostSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
def post_element(request, id):
    """
    Route for singular post object with methods GET, PUT, DELETE.

    Args:
    :param request: request parameter from API
    :param id: id of post object. Required

    Raises:
    Post.DoesNotExist: when target object is not found

    Returns:
    :return: serialized data of Post object or status code
    Example: {
                "id": 3,
                "title": "Faster JavaScript Calls",
                "post": "By putting the number of arguments...",
                "slug": "tokio-faster-javascript-calls",
                "date_published": "2021-02-15T20:12:48.573997Z",
                "author": 4
            }
    """
    try:
        post = Post.objects.get(id=id)
    except Post.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == "GET":
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "PUT":
        # TODO make only one field update necessary
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        post.delete()
        # TODO add comment when deleted
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["PUT"])
def post_like(request, id):
    """
    Route for post like and post unlike.
    Triggers like_unlike() method of Like model,
    switching Boolean to opposite value.
    If Like object doesn't exist, creates it.

    Args:
    :param request: request parameter from API
    :param id: id of post object. Required

    Raises:
    Post.DoesNotExist: when target object is not found

    Returns:
    :return: serialized data of Like object.
    Example: {
                "id": 2,
                "date": "2021-02-16T08:38:30.946808Z",
                "liked": false,
                "user": 4,
                "post": 3
            }
    """
    try:
        post = Post.objects.get(id=id)
    except Post.DoesNotExist:
        return HttpResponse(status=404)

    try:
        like = Like.objects.get(post=post)
    except Like.DoesNotExist:
        data = {
            "user": request.user.id,
            "post": id,
        }
        serializer = LikeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    else:
        like.like_unlike()
        data = {
            "user": request.user.id,
            "post": id,
        }
        serializer = LikeSerializer(like, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def analytics(request):
    """
    Analytics route displaying quantity of likes received by day.
    Example url: /api/analytics/?date_from=2020-02-02&date_to=2020-02-15.

    Args:
    :param request: request parameter from API
    :query_params: date_from and date_to. Required

    Raises:
    ValueError: when date_from or date_to query params are not in Date format

    Returns:
    :return: API should return analytics aggregated by day.
    Example: [  {
                    "day": 15,
                    "month": 2,
                    "year": 2021,
                    "total_likes": 1
                },
                {
                    "day": 16,
                    "month": 2,
                    "year": 2021,
                    "total_likes": 1
                }]
    """

    try:
        date_from = request.query_params["date_from"]
        date_to = request.query_params["date_to"]
        date_from_converted = datetime.fromisoformat(date_from)
        date_to_converted = datetime.fromisoformat(date_to)
    except ValueError:
        return f"date_from ({date_from}) or date_to ({date_to}) " \
            f"parameters are not in format Y-m-d"

    else:
        query = (
            Like.objects.filter(liked=True)
            .annotate(day=ExtractDay("date"))
            .annotate(month=ExtractMonth("date"))
            .annotate(year=ExtractYear("date"))
            .values("day", "month", "year")
            .annotate(total_likes=Count("liked"))
        )

        return Response(query, status=status.HTTP_200_OK)


@api_view(["GET"])
def user_activity(request):
    """
    user activity an endpoint, which will show when user was
    logged in last time and when he made a last request to the service.

    Raises:
    Object.DoesNotExist: when target object is not found

    Args:
    :param request parameter from API

    Returns:
    :return: dict with last_login, last_like and last_post
    parameters and datetime values

    Example:
    {
        "last_login": "2021-02-16T08:03:56.779157Z",
        "last_like": "2021-02-16T08:04:40.912497Z",
        "last_post": "2021-02-15T20:12:48.573997Z"
    }

    """

    user = User.objects.get(id=request.user.id)
    last_login = user.last_login
    last_like = Like.objects.filter(user=request.user).last()
    last_post = Post.objects.filter(author=request.user).last()

    data = {
        "last_login": last_login,
        "last_like": last_like.date,
        "last_post": last_post.date_published,
    }
    return Response(data, status=status.HTTP_200_OK)
