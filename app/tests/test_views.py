from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase
from app.models import Post, Like
from app.views import registration, post_collection, \
    post_element, post_like, analytics, user_activity
from app.serializers import PostSerializer
from django.contrib.auth.models import User
from rest_framework.test import force_authenticate
from rest_framework import status


class TestViews(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user1 = User.objects.create_user(username='Petya',
                                              password='1234567',
                                              email='petya@gmail.com')
        self.post1 = Post.objects.create(author=self.user1,
                                         title="Very first title",
                                         post="A lot of text")
        self.like1 = Like.objects.create(user=self.user1, post=self.post1)

    def test_registration_get_method_not_allowed(self):
        request = self.factory.get("account/register")
        response = registration(request)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_registration_get_bad_request(self):
        request = self.factory.post("account/register")
        response = registration(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_email_validation_error(self):
        user2 = {"username": 'Petya2',
                 "password": '12345678',
                 "password2": '12345678',
                 "email": "petya@gmail.com"}
        request = self.factory.post('/account/register', user2)
        response = registration(request)
        self.assertRaises(ValidationError)

    def test_registration_password_validation_error(self):
        user3 = {"username": 'Petya3',
                 "password": '12345678',
                 "password2": '1',
                 "email": "petya3@gmail.com"}
        request = self.factory.post('/account/register', user3)
        response = registration(request)
        self.assertRaises(ValidationError)

    def test_registration_post_created(self):
        user4 = {"username": 'Petya4',
                 "password": '12345678',
                 "password2": '12345678',
                 "email": "petya4@gmail.com"}
        request = self.factory.post('/account/register', user4)
        response = registration(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.get(username=user4["username"]))

    def test_registration_jwt_token_created(self):
        user1 = {"username": 'Petya2',
                 "password": '12345678',
                 "password2": '12345678',
                 "email": "petya2@gmail.com"}
        request = self.factory.post('/account/register', user1)
        response = registration(request)
        self.assertTrue(response.data['access'])

    def test_post_collection_get_all(self):
        request = self.factory.get("/post")
        force_authenticate(request, user=self.user1)
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        response = post_collection(request)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_collection_get_auth_error(self):
        request = self.factory.get("/post")
        response = post_collection(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_collection_post(self):
        data = {
            "author": "Danny Ocean",
            "title": "the Bellagio, the Mirage",
            "post": "So here is the plan...",
        }
        request = self.factory.post("/post", data)
        force_authenticate(request, user=self.user1)
        response = post_collection(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_collection_post_error(self):
        data = {
            "author": "Danny Ocean",
            "title": "the Bellagio, the Mirage",
        }
        request = self.factory.post("/post", data)
        force_authenticate(request, user=self.user1)
        response = post_collection(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_element_get_does_not_exist(self):
        post_id = 100500
        request = self.factory.get('/post/{post_id}/')
        force_authenticate(request, user=self.user1)
        response = post_element(request, post_id)
        self.assertRaises(Post.DoesNotExist)

    def test_post_element_get(self):
        post_id = self.post1.id
        request = self.factory.get('/post/{post_id}/')
        force_authenticate(request, user=self.user1)
        response = post_element(request, post_id)
        self.assertEqual(response.data['title'], "Very first title")

    def test_post_element_put(self):
        post_id = self.post1.id
        data = {
            "author": 1,
            "title": "the Bellagio, the Mirage",
            "post": "So here is the plan...",
        }
        request = self.factory.put('/post/{post_id}/',
                                   data,
                                   content_type='application/json')
        force_authenticate(request, user=self.user1)
        response = post_element(request, post_id)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['title'], "the Bellagio, the Mirage")


    def test_post_element_put_bad_request(self):
        post_id = self.post1.id
        data = {
            "author": '',
        }
        request = self.factory.put('/post/{post_id}/',
                                   data,
                                   content_type='application/json')
        force_authenticate(request, user=self.user1)
        response = post_element(request, post_id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_element_delete(self):
        post_id = self.post1.id
        request = self.factory.delete('/post/{post_id}/')
        force_authenticate(request, user=self.user1)
        response = post_element(request, post_id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_post_like(self):
        post_id = self.post1.id
        request = self.factory.put('/post/{post_id}/like')
        force_authenticate(request, user=self.user1)
        response = post_like(request, post_id)
        self.assertTrue(response.data['liked'])

    def test_post_like_post_does_not_exist(self):
        post_id = 100500
        request = self.factory.put('/post/{post_id}/like')
        force_authenticate(request, user=self.user1)
        response = post_like(request, post_id)
        self.assertRaises(Post.DoesNotExist)

    def test_post_like_like_does_not_exist_and_create(self):
        post2 = Post.objects.create(author=self.user1,
                                    title="Another title",
                                    post="Another text")
        request = self.factory.put('/post/{post2.id}/like')
        force_authenticate(request, user=self.user1)
        response = post_like(request, post2.id)
        self.assertRaises(Like.DoesNotExist)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_analytics(self):
        data = {
            'date_from': '2021-02-16',
            'date_to': '2021-02-16'
        }
        request = self.factory.get('/analytics', data)
        force_authenticate(request, user=self.user1)
        response = analytics(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_analytics_value_error(self):
        data = {
            'date_from': '123123',
            'date_to': '123123'
        }
        request = self.factory.get('/analytics', data)
        force_authenticate(request, user=self.user1)
        self.assertRaises(ValueError)


    def test_user_activity(self):
        last_post = Post.objects.filter(author=self.user1).last()
        request = self.factory.get('/user-activity')
        force_authenticate(request, user=self.user1)
        response = user_activity(request)
        self.assertEqual(response.data['last_post'], last_post.date_published)
