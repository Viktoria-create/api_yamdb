import datetime

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import username_validate, validate_year

CSV_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


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
        unique=True
    )
    username = models.CharField(
        max_length=150,
        null=True,
        unique=True,
        validators=(username_validate,)
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
    def is_admin(self):
        return (
            self.role == self.ADMIN
            or self.is_superuser)
        #    or self.is_staff
        # )

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_user(self):
        return self.role == self.USER

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'


class CategoryGenre(models.Model):
    """Категория и жанр произведения."""
    name = models.CharField(
        max_length=200
    )
    slug = models.SlugField(
        max_length=50,
        unique=True
    )

    class Meta:
        abstract = True


class Category(CategoryGenre):
    """Категория произведения."""

    class Meta:
        verbose_name = 'Категория'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Genre(CategoryGenre):
    """Жанр произведения."""

    class Meta:
        verbose_name = 'Жанр'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Title(models.Model):
    """Конкретный объект."""
    name = models.CharField(
        max_length=200
    )
    year = models.IntegerField(
        validators=(validate_year,)
    )
    description = models.TextField(
        null=True,
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр',
        through='GenreTitle'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True
    )

    class Meta:
        verbose_name = 'Произведение'
        ordering = ('name',)

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE
    )
    genre = models.ForeignKey(
        Genre,
        verbose_name='Жанр',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Произведение и жанр'

    def __str__(self):
        return f'{self.title}, жанр - {self.genre}'


class DatePubText(models.Model):
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )
    text = models.TextField()

    class Meta:
        abstract = True


class Review(DatePubText):
    """Отзывы пользователей."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.IntegerField(
        validators=(
            MinValueValidator(
                limit_value=1, message='Оценка не может быть меньше 1'
            ),
            MaxValueValidator(
                limit_value=10, message='Оценка не может быть больше 10'
            )
        )
    )

    class Meta:
        unique_together = ('author', 'title')

    @property
    def csv_pub_date(self):
        return self.pub_date

    @csv_pub_date.setter
    def csv_pub_date(self, value):
        if value:
            self.pub_date = datetime.datetime.strptime(
                value, CSV_DATETIME_FORMAT)


class Comment(DatePubText):
    """Комментарии."""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    class Meta:
        verbose_name = 'Комментарий'
        ordering = ('pub_date',)

    @property
    def csv_pub_date(self):
        return self.pub_date

    @csv_pub_date.setter
    def csv_pub_date(self, value):
        if value:
            self.pub_date = datetime.datetime.strptime(value,
                                                       CSV_DATETIME_FORMAT)
