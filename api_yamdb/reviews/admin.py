# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin

from .models import Category, Comment, Genre, Review, Title, User


# admin.site.register(User, UserAdmin)
# admin.site.register(Category)
# admin.site.register(Genre)
# admin.site.register(Title)
# admin.site.register(Review)
# admin.site.register(Comment)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, User
from reviews.models import Category, Comment, Genre, Review, Title
from import_export import resources
# from import_export.fields import Field
from import_export.admin import ImportExportModelAdmin

# from django.contrib import admin
from django.db import models

# from .models import Category, Comment, Genre, Review, Title


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
        fields = (
            'id',
            'review',
            'text',
            'author',
            'pub_date',
        )


class CommentAdmin(ImportExportModelAdmin):
    resource_classes = [CommentResource]
    list_display = (
        'id',
        'review',
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
        'score',)
    search_fields = ('pub_date',)
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


admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(User, UserAdmin)
