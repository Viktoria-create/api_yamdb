from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


# from .validators import validate_year


# class User(AbstractUser):
#     ADMIN = 'admin'
#     MODERATOR = 'moderator'
#     USER = 'user'
#     ROLES = (
#         (ADMIN, 'Administrator'),
#         (MODERATOR, 'Moderator'),
#         (USER, 'User'),
#     )
#     role = models.CharField(
#         max_length=50,
#         choices=ROLES,
#         default=USER
#     )
#     bio = models.TextField(
#         null=True,
#         blank=True
#     )

#     @property
#     def is_moderator(self):
#         return self.role == self.MODERATOR

#     @property
#     def is_admin(self):
#         return self.role == self.ADMIN

#     # USERNAME_FIELD = 'email'
#     # REQUIRED_FIELDS = ['username']

#     class Meta:
#         ordering = ('id',)
#         verbose_name = 'Пользователь'

#         # constraints = [
#         #   models.CheckConstraint(
#         #       check=~models.Q(username__iexact="me"),
#         #       name="username_is_not_me")]

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **kwargs):
        user = self.model(email=email, is_staff=True, is_superuser=True, **kwargs)
        user.set_password(password)
        user.save()
        return user


class User(AbstractUser):
    email = models.EmailField(('email address'), unique=True)
    bio = models.TextField(max_length=300, blank=True)
    confirmation_code = models.CharField(max_length=6, default='000000')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    USER_ROLE = (
        ('user', 'user'),
        ('moderator', 'moderator'),
        ('admin', 'admin'),
    )

    role = models.CharField(max_length=9, choices=USER_ROLE, default='user')

    objects = CustomUserManager()


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
        # validators=[validate_year]
    )
    description = models.TextField(
        null=True,
        blank=True)
    genre = models.ManyToManyField(
        Genre, )
    # through='GenreTitle')
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
