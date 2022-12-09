from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import validate_year
import datetime

CSV_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"  # формат datetime в csv


class User(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    ROLES = (
        (ADMIN, 'Administrator'),
        (MODERATOR, 'Moderator'),
        (USER, 'User'),
    )
    email = models.EmailField(
        unique=True,
    )
    username = models.CharField(
        max_length=150,
        null=True,
        unique=True,
    )
    role = models.CharField(
        max_length=50,
        choices=ROLES,
        default=USER
    )
    bio = models.TextField(
        null=True,
        blank=True
    )

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'


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
        validators=[validate_year]
    )
    description = models.TextField(
        null=True,
        blank=True)
    genre = models.ManyToManyField(
        Genre,)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Произведение'
        ordering = ('name',)


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE)
    genre = models.ForeignKey(
        Genre,
        verbose_name='Жанр',
        on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.title}, жанр - {self.genre}'

    class Meta:
        verbose_name = 'Произведение и жанр'
        verbose_name_plural = 'Произведения и жанры'


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


@property
def csv_pub_date(self):
    return self.pub_date


@csv_pub_date.setter
def csv_pub_date(self, value):
    if value:
        self.pub_date = datetime.datetime.strptime(value, CSV_DATETIME_FORMAT)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author',),
                name='unique review'
            )]


class Comment(models.Model):
    """Коментарии."""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )


@property
def csv_pub_date(self):
    return self.pub_date


@csv_pub_date.setter
def csv_pub_date(self, value):
    if value:
        self.pub_date = datetime.datetime.strptime(value, CSV_DATETIME_FORMAT)

    class Meta:
        verbose_name = 'Комментарий'
        ordering = ('pub_date',)
