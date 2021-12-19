import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Post, Group, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_authorized(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        new_text = 'Новая запись'
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        new_uploaded = SimpleUploadedFile(
            name='new_small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': new_text,
            'image': new_uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:profile', kwargs={'username': self.user}
            )
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        new_post_id = Post.objects.filter(
            text=new_text
        ).order_by('-id').values('id')[:1]
        self.assertTrue(
            Post.objects.order_by('-id').filter(
                text=new_text,
                id=new_post_id,
                image=f'posts/{new_uploaded.name}'
            ).exists()
        )

    def test_post_edit_authorized(self):
        """Валидная форма редактирует запись в Post."""
        post_count = Post.objects.count()
        text_repl = 'Редактирование записи'
        small_gif_repl = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded_repl = SimpleUploadedFile(
            name='small_repl.gif',
            content=small_gif_repl,
            content_type='image/gif'
        )
        form_data = {
            'text': text_repl,
            'image': uploaded_repl
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            )
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(
            Post.objects.order_by('-id').filter(
                text=text_repl,
                id=self.post.id,
                image=f'posts/{uploaded_repl.name}'
            ).exists()
        )

    def test_create_post_group(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        new_text = 'Новая запись'
        small_gif_2 = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        new_uploaded = SimpleUploadedFile(
            name='new_small_2.gif',
            content=small_gif_2,
            content_type='image/gif'
        )
        form_data = {
            'text': new_text,
            'group': self.post.group.id,
            'image': new_uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:profile', kwargs={'username': self.user}
            )
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        new_post_id = Post.objects.filter(
            text=new_text
        ).order_by('-id').values('id')[:1]
        self.assertTrue(
            Post.objects.order_by('-id').filter(
                text=new_text,
                group=self.post.group.id,
                id=new_post_id,
                image=f'posts/{new_uploaded.name}'
            ).exists()
        )

    def test_post_edit_group(self):
        """Валидная форма редактирует запись в Post."""
        post_count = Post.objects.count()
        text_repl = 'Редактирование записи'
        small_gif_repl_2 = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded_repl = SimpleUploadedFile(
            name='small_repl_2.gif',
            content=small_gif_repl_2,
            content_type='image/gif'
        )
        form_data = {
            'text': text_repl,
            'group': self.post.group.id,
            'image': uploaded_repl
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            )
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(
            Post.objects.order_by('-id').filter(
                text=text_repl,
                group=self.post.group.id,
                id=self.post.id,
                image=f'posts/{uploaded_repl.name}'
            ).exists()
        )

    def test_create_post_anon(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        new_text = 'Новая запись'
        small_gif_3 = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        new_uploaded = SimpleUploadedFile(
            name='new_small.gif',
            content=small_gif_3,
            content_type='image/gif'
        )
        form_data = {
            'text': new_text,
            'group': self.post.group.id,
            'image': new_uploaded
        }
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            f'{reverse("users:login")}'
            f'?next={reverse("posts:post_create")}'
        )
        self.assertEqual(Post.objects.count(), post_count)
        new_post_id = Post.objects.filter(
            text=new_text
        ).order_by('-id').values('id')[:1]
        self.assertFalse(
            Post.objects.filter(
                text=new_text,
                group=self.post.group.id,
                id=new_post_id,
                image=f'posts/{new_uploaded.name}'
            ).exists()
        )

    def test_post_edit_anon(self):
        """Валидная форма редактирует запись в Post."""
        post_count = Post.objects.count()
        text_repl = 'Редактирование записи'
        small_gif_repl_3 = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded_repl = SimpleUploadedFile(
            name='small_repl.gif',
            content=small_gif_repl_3,
            content_type='image/gif'
        )
        form_data = {
            'text': text_repl,
            'group': self.post.group.id,
            'image': uploaded_repl
        }
        response = self.client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            f'{reverse("users:login")}'
            f'?next='
            f'{reverse("posts:post_edit", kwargs={"post_id": self.post.id})}'
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertFalse(
            Post.objects.filter(
                text=text_repl,
                group=self.post.group.id,
                id=self.post.id,
                image=f'posts/{uploaded_repl.name}'
            ).exists()
        )
