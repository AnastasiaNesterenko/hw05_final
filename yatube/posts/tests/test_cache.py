from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.test import Client, TestCase
from django.urls import reverse


from posts.models import Post, Group


User = get_user_model()


class CacheIndexTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertTrue(response.content)
        len_resp = len(response.content)
        self.post.delete()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertTrue(response.content)
        len_resp_2 = len(response.content)
        self.assertEqual(len_resp, len_resp_2)
        key = make_template_fragment_key('index_page')
        cache.delete(key)
        response = self.authorized_client.get(reverse('posts:index'))
        len_resp_3 = len(response.content)
        self.assertNotEqual(len_resp, len_resp_3)
