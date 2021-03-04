from django.test import TestCase
from app.models import Post, Like
from django.contrib.auth.models import User


class TestModels(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user('Petya',
                                              '1234567',
                                              'petya@gmail.com')
        self.post1 = Post.objects.create(author=self.user1,
                                         title="Very first title",
                                         post="A lot of text")
        self.like1 = Like.objects.create(user=self.user1, post=self.post1)

    def tearDown(self):
        self.user1.delete()
        self.post1.delete()
        self.like1.delete()

    def test_post_created(self):
        self.assertTrue(Post.objects.get(id=self.post1.id))

    def test_post_string(self):
        post = Post.objects.get(id=self.post1.id)
        self.assertEqual(str(post), self.post1.title)

    def test_post_slugify(self):
        self.assertEqual(self.post1.slug, 'petya-very-first-title')

    def test_like_created(self):
        self.assertTrue(Like.objects.get(id=self.like1.id))

    def test_like_string(self):
        like = Like.objects.get(id=self.like1.id)
        self.assertEqual(str(like), str(self.like1.liked))

    def test_like_unlike(self):
        self.like1.like_unlike()
        self.like1.save()
        self.assertTrue(Like.objects.get(id=self.like1.id).liked)
