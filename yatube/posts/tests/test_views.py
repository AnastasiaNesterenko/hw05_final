import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

from posts.models import Post, Group, Comment, Follow

from yatube.settings import NUMBER_OF_RECORDS

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_2 = User.objects.create_user(username='Poklonik')
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )
        small_image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_image,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
            image=uploaded
        )
        cls.comment = Comment.objects.create(
            text='Тестовый коммент',
            post=cls.post,
            author=cls.user,
        )
        cls.follow = Follow.objects.create(
            user=cls.user_2,
            author=cls.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)
        self.user_3 = User.objects.create_user(username='NePoklonik')
        self.authorized_client_3 = Client()
        self.authorized_client_3.force_login(self.user_3)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.post.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ): 'posts/create_post.html'
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def for_tests(self, first_object):
        post_text_0 = first_object.text
        post_slug_0 = first_object.group.slug
        post_author_0 = first_object.author
        post_id_0 = first_object.id
        post_image_0 = first_object.image
        return (self.assertEqual(post_text_0, self.post.text),
                self.assertEqual(post_slug_0, self.post.group.slug),
                self.assertEqual(post_author_0, self.user),
                self.assertEqual(post_id_0, self.post.id),
                self.assertEqual(post_image_0, self.post.image)
                )

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        PostViewsTest.for_tests(self, first_object)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.post.group.slug}
            )
        )
        first_object = response.context['page_obj'][0]
        PostViewsTest.for_tests(self, first_object)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user}
            )
        )
        first_object = response.context['page_obj'][0]
        PostViewsTest.for_tests(self, first_object)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        first_object = response.context['post']
        post_count = response.context['post_count']
        user = response.context['user']
        self.assertEqual(post_count, self.post.id)
        self.assertEqual(user, self.user)
        PostViewsTest.for_tests(self, first_object)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильной формой."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильной формой."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_entry(self):
        self.new_user = User.objects.create_user(username='NewKid')
        self.new_group = Group.objects.create(
            title='Тестовая группа 1',
            slug='slug-1',
            description='Тестовое описание 1',
        )
        self.new_post = Post.objects.create(
            author=self.new_user,
            text='Тестовый текст 1',
            group=self.new_group
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.new_user)
        response_index = self.authorized_client.get(reverse('posts:index'))
        self.assertTrue(response_index)
        response_group = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.new_post.group.slug}
            )
        )
        self.assertTrue(response_group)
        response_profile = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.new_user}
            )
        )
        self.assertTrue(response_profile)

    def test_comment_only_authorized(self):
        comment = 'тестовый коммент1'
        form_data = {
            'text': comment,
            'author': self.client,
        }
        self.client.post(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )
        new_comment_id = Comment.objects.filter(
            text=comment
        ).order_by('-id').values('id')[:1]
        self.assertFalse(
            Comment.objects.filter(
                text=comment,
                id=new_comment_id
            ).exists()
        )

    def test_comment_entry(self):
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        first_object = response.context['comments'][0]
        post_comment_0 = first_object.text
        post_comment_author_0 = first_object.author
        self.assertEqual(post_comment_0, self.comment.text)
        self.assertEqual(post_comment_author_0, self.user)

    def test_follow(self):
        form_data = {
            'author': self.user,
            'user': self.user_3
        }
        response_3 = self.authorized_client_3.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response_3, reverse(
                'posts:profile', kwargs={'username': self.user}
            )
        )
        self.assertTrue(
            Follow.objects.filter(
                user=self.user_3,
                author=self.user
            ).exists()
        )

    def test_unfollow(self):
        form_data = {
            'author': self.user,
            'user': self.user_2
        }
        response_2 = self.authorized_client_2.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response_2, reverse(
                'posts:profile', kwargs={'username': self.user}
            )
        )
        self.assertFalse(
            Follow.objects.filter(
                user=self.user_2,
                author=self.user
            ).exists()
        )

    def test_recording_follow(self):
        response_2 = self.authorized_client_2.get(
            reverse('posts:follow_index')
        )
        response_3 = self.authorized_client_3.get(
            reverse('posts:follow_index')
        )
        post_2 = response_2.context['page_obj']
        post_3 = response_3.context['page_obj']
        self.assertTrue(post_2)
        self.assertFalse(post_3)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )
        for cls.post in range(13):
            cls.post = Post.objects.create(
                author=cls.user,
                text='Запись 1',
                group=cls.group,
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), NUMBER_OF_RECORDS)
        response_group = self.client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.post.group.slug}
            )
        )
        self.assertEqual(
            len(
                response_group.context['page_obj']
            ),
            NUMBER_OF_RECORDS
        )
        response_author = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user}
            )
        )
        self.assertEqual(
            len(
                response_author.context['page_obj']
            ),
            NUMBER_OF_RECORDS
        )

    def test_second_page_contains_three_records(self):
        leftover_pages = Post.objects.count() % NUMBER_OF_RECORDS
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), leftover_pages)
        response_group = self.client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.post.group.slug}
            ) + '?page=2'
        )
        self.assertEqual(
            len(
                response_group.context['page_obj']
            ),
            leftover_pages
        )
        response_author = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user}
            ) + '?page=2'
        )
        self.assertEqual(
            len(
                response_author.context['page_obj']
            ),
            leftover_pages
        )
