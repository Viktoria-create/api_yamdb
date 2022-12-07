from django.contrib import admin
from django.contrib.auth.models import Group
from .models import User
from django.db import models
from reviews.models import (Category, Comment, Genre, Review, Title,
                            User, GenreTitle)
from django.contrib.auth.admin import UserAdmin, User

from import_export import resources
from import_export.admin import ImportExportModelAdmin


class UserResource(resources.ModelResource):

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'role',
            'bio',
            'first_name',
            'last_name',
        )


class UserAdmin(ImportExportModelAdmin,):
    resource_classes = [UserResource]
    list_display = (
        'id',
        'username',
        'email',
        'role',
        'bio',
        'first_name',
        'last_name',
    )
    search_fields = (
        'id',
        'role',
        'first_name',
        'last_name',
        'username',
        'email'
    )
    list_filter = ('username',)
    empty_value_display = '-пусто-'


class CategoryResource(resources.ModelResource):
    name = models.CharField(max_length=100)

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')


class CategoryAdmin(ImportExportModelAdmin):
    resource_classes = [CategoryResource]
    list_display = (
        'id',
        'name',
        'slug',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class CommentResource(resources.ModelResource):
    name = models.CharField(max_length=200)

    class Meta:
        model = Comment
    #    exclude = ('pub_date', )
    #    import_id_fields = ('text',)
    #    widgets = {'published': {'format': '%d.%m.%Y'},}
        fields = (
            'id',
            'review_id',
            'text',
            'author',
            'pub_date',
        )


class CommentAdmin(ImportExportModelAdmin):
    resource_classes = [CommentResource]
    list_display = (
        'id',
        'review_id',
        'text',
        'author',
        'pub_date',
    )
    search_fields = ('review',)
    list_filter = ('review',)
    empty_value_display = '-пусто-'


class GenreResource(resources.ModelResource):
    name = models.CharField(max_length=100)

    class Meta:
        model = Genre
        fields = ('id', 'name', 'slug')


class GenreAdmin(ImportExportModelAdmin):
    resource_classes = [GenreResource]
    list_display = (
        'id',
        'name',
        'slug',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class ReviewResource(resources.ModelResource):

    class Meta:
        model = Review
        fields = ('id',
                  'title_id',
                  'text',
                  'author',
                  'score',
                  'pub_date',)


class ReviewAdmin(ImportExportModelAdmin):
    resource_classes = [ReviewResource]
    list_display = (
        'id',
        'title',
        'text',
        'author',
        'score',
        'pub_date')
    search_fields = ('id', 'pub_date',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class TitleResource(resources.ModelResource):

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'category',
            'description',)


class TitleAdmin(ImportExportModelAdmin):
    resource_classes = [TitleResource]
    list_display = (
        'id',
        'name',
        'year',
        'category',
        'description',)
    search_fields = ('name',)
    list_filter = ('name',)
    exclude = ('genres',)
    empty_value_display = '-пусто-'


class GenreTitleResource(resources.ModelResource):

    class Meta:
        model = Genre
        fields = (
            'id',
            'title_id',
            'genre_id',)


class GenreTitleAdmin(ImportExportModelAdmin):
    resource_classes = [GenreTitleResource]
    list_display = (
        'id',
        'title_id',
        'genre_id',)
    search_fields = ('id',)
    list_filter = ('id',)
    empty_value_display = '-пусто-'


admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(GenreTitle, GenreTitleAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
