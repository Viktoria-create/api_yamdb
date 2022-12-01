from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

#from .validators import validate_year
User = get_user_model()


class Category(models.Model):
    """Категория произведения."""
    name = models.CharField(
        max_length=200)
    slug = models.SlugField(
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
        max_length=200)
    slug = models.SlugField(
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
        max_length=200)
    year = models.IntegerField(
        #validators=[validate_year]
        )
    description = models.TextField(
        null=True,
        blank=True)
    genre = models.ManyToManyField(
        Genre,)
    # through='GenreTitle')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True)
    rating = models.IntegerField(
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
        on_delete=models.CASCADE,
        related_name='reviews')
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews')
    score = models.IntegerField(
        validators=[
            MinValueValidator(
                limit_value=1, message='Оценка не может быть меньше 1'
            ),
            MaxValueValidator(
                limit_value=10, message='Оценка не может быть больше 10'
            )]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True)


class Comment(models.Model):
    """Коментарии."""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments')
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True)

    class Meta:
        verbose_name = 'Комментарий'
        ordering = ('pub_date',)
