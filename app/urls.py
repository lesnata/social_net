from django.urls import path
from . import views


urlpatterns = [
    path("account/register", views.registration, name="sign-up"),
    path("post/", views.post_collection, name="post-collection"),
    path("post/<int:id>", views.post_element, name="post-element"),
    path("post/<int:id>/like", views.post_like, name="post-like"),
    path("analytics/", views.analytics, name="analytics"),
    path("user-activity/", views.user_activity, name="user_activity"),
]
