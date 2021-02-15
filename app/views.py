import datetime
import json
from django.http import HttpResponse
from rest_framework.decorators import api_view, authentication_classes, \
    permission_classes
from datetime import datetime
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import Post, Like
from .serializers import PostSerializer, LikeSerializer, UserCreateSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.db.models import Count
from django.db.models.functions import ExtractDay, ExtractMonth, ExtractYear

# Create your views here.


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def registration(request):
    serializer = UserCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    user = serializer.save()
    refresh = RefreshToken.for_user(user)
    res = {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }
    return Response(res, status.HTTP_201_CREATED)


# def registration(request):
#     serializer = RegistrationSerializer(data=request.data)
#     data = {}
#     if serializer.is_valid():
#         user = serializer.save()
#         refresh_token = RefreshToken.for_user(user)
#         data = {
#             "refresh": str(refresh_token),
#             "access": str(refresh_token.access_token),
#         }
#         return Response(data)
#
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
def post_collection(request):
    if request.method == "GET":
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        data = {
            'author': request.user.id,
            'title': request.data.get('title'),
            'post': request.data.get('post'),
        }
        serializer = PostSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
def post_element(request, id):
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


@api_view(['PUT'])
def post_like(request, id):
    try:
        post = Post.objects.get(id=id)
    except Post.DoesNotExist:
        return HttpResponse(status=404)

    try:
        like = Like.objects.get(post=post)
    except Like.DoesNotExist:
        data = {
            'user': request.user.id,
            'post': id,
        }
        serializer = LikeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    else:
        like.like_unlike()
        data = {
            'user': request.user.id,
            'post': id,
        }
        serializer = LikeSerializer(like, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def analytics(request):

    '''
    Route with analytics about how many likes was made.
    Example url: /api/analytics/?date_from=2020-02-02&date_to=2020-02-15.
    API should return analytics aggregated by day.

    :param request:
    :return:
    '''

    try:
        date_from = request.query_params['date_from']
        date_to = request.query_params['date_to']
        date_from_converted = datetime.fromisoformat(date_from)
        date_to_converted = datetime.fromisoformat(date_to)
    except ValueError:
        return f"from_time ({date_from}) or to_time ({date_to}) parameters are not in Date format"

    else:
        query = Like.objects.filter(liked=True).annotate(day=ExtractDay('date')) \
            .annotate(month=ExtractMonth('date')) \
            .annotate(year=ExtractYear('date')) \
            .values('day', 'month', 'year') \
            .annotate(total_likes=Count('liked'))

        return Response(query, status=status.HTTP_200_OK)


@api_view(['GET'])
def user_activity(request):
    '''
    user activity an endpoint which will show when user was
    login last time and when he mades a last request to the service.
    :param request:
    :return:
    '''

    try:
        user = User.objects.get(id=request.user.id)
    except User.DoesNotExist:
        return HttpResponse(status=404)

    else:
        last_login = user.last_login
        data = {
            'last_login': last_login,
            'last_request': None
        }
        return Response(data, status=status.HTTP_200_OK)











    # query = Like.objects.annotate(year=ExtractYear('date')).annotate(week=ExtractWeek('date')).values('year', 'week').annotate(total_likes=Count('liked')

        # query = Like.objects.filter(date__gte=date_from, date__lte=date_to)\
        #     .annotate(total_likes=Count('liked'))



            #     for i in Like.objects.filter(date__gte=date_from, date__lte=date_to)
            #
            #     liked_array = Like.objects.all().aggregate(likes_per_day=Sum(F('price')/F('pages'),
            #                                                                  output_field=FloatField()))
            #     liked_array = Like.objects.filter(date__gte=date_from, date__lte=date_to)
            #
            # else:
            #     liked_array = Like.objects.filter(date__gte=date_from)







