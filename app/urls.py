from django.urls import path
from . import views


urlpatterns = [
    path('account/register', views.registration, name="sign-up"),
    path('account/login', views.login, name="login"),
    path('post/', views.post_collection, name="post-collection"),
    path('post/<int:id>', views.post_element, name="post-element"),
    path('post/<int:post_id>/comment', views.comment_collection, name='comment-collection'),
    path('comment/<int:comment_id>', views.comment_element, name='comment-collection'),

]