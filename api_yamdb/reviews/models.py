from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

#from .validators import validate_year
User = get_user_model()


class Category(models.Model):
    """Категория произведения."""
    name = models.CharField(
        verbose_name='Название',
        max_length=200)
    slug = models.SlugField(
        name='Идентификатор',
        max_length=50,
        unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        ordering = ('name',)


class Genre(models.Model):
    """Жанр произведения."""
    name = models.CharField(
        verbose_name='Название',
        max_length=200)
    slug = models.SlugField(
        name='Идентификатор',
        max_length=50,
        unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        ordering = ('name',)


class Title(models.Model):
    """Конкретный объкет."""
    name = models.CharField(
        verbose_name='Название',
        max_length=200)
    year = models.IntegerField(
        name='Дата выхода',
        #validators=[validate_year]
        )
    description = models.TextField(

        name='Описание',
        null=True,
        blank=True)
    genre = models.ManyToManyField(
        Genre,
        name='Жанр',)
    # through='GenreTitle')
    category = models.ForeignKey(
        Category,
        name='Категория',
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True)
    rating = models.IntegerField(
        name='Рейтинг',
        null=True,
        default=None)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Произведение'
        ordering = ('name',)


class Review(models.Model):
    """Отзывы пользователей."""
    title = models.ForeignKey(
        Title,
        name='Произведение',
        on_delete=models.CASCADE,
        related_name='reviews')
    text = models.TextField(
        name='Текст',)
    author = models.ForeignKey(
        User,
        name='Автор',
        on_delete=models.CASCADE,
        related_name='reviews')
    score = models.PositiveSmallIntegerField(
        name='Рейтинг',
        validators=[
            MinValueValidator(1, 'Допустимы значения от 1 до 10'),
            MaxValueValidator(10, 'Допустимы значения от 1 до 10')])
    pub_date = models.DateTimeField(
        name='Дата публикации',
        auto_now_add=True,
        db_index=True)


class Comment(models.Model):
    """Коментарии."""
    review = models.ForeignKey(
        Review,
        name='Отзыв',
        on_delete=models.CASCADE,
        related_name='comments')
    text = models.TextField(name='Текст',)
    author = models.ForeignKey(
        User,
        name='Пользователь',
        on_delete=models.CASCADE,
        related_name='comments')
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True)

    class Meta:
        verbose_name = 'Комментарий'
        ordering = ('pub_date',)