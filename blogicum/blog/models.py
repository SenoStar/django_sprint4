from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

USER = get_user_model()

# Длина текста.
TEXT_LEN = 256


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Добавлено')

    class Meta:
        abstract = True
        # Перестала работать сортировка в view функции для постов
        # после аннотации(подсчёт комментариев)
        ordering = (['-pub_date'])


class Post(BaseModel):
    title = models.CharField(max_length=TEXT_LEN,
                             verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в будущем — '
                  'можно делать отложенные публикации.'
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    author = models.ForeignKey(USER, on_delete=models.CASCADE,
                               verbose_name='Автор публикации')
    category = models.ForeignKey('Category', on_delete=models.SET_NULL,
                                 null=True, verbose_name='Категория',
                                 related_name='posts')
    location = models.ForeignKey('Location', on_delete=models.SET_NULL,
                                 blank=False, null=True,
                                 verbose_name='Местоположение')
    image = models.ImageField('Фото', upload_to='posts_images', blank=True)

    class Meta(BaseModel.Meta):
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'


class Category(BaseModel):
    title = models.CharField(max_length=TEXT_LEN,
                             verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True, verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; '
                  'разрешены символы латиницы, цифры, дефис и подчёркивание.'
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(BaseModel):
    name = models.CharField(max_length=TEXT_LEN, verbose_name='Название места')
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Comment(BaseModel):
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
