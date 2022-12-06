from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.shortcuts import get_object_or_404
# from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Review, Title, User, Comment


# User = get_user_model()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class EmailAuthSerializer(serializers.Serializer):
    email = serializers.EmailField()
    confirmation_code = serializers.CharField(max_length=100)

    def validate(self, data):
        user = get_object_or_404(
            User, confirmation_code=data['confirmation_code'],
            email=data['email']
        )
        return get_tokens_for_user(user)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True,
                                          slug_field='username')

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True,
                                          slug_field='username')

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate_score(self, value):
        if value > 10 or value <= 0:
            raise serializers.ValidationError('Проверьте оценку!')
        return value

    def validate(self, data):
        current_user = self.context['request'].user
        title_id = self.context['view'].kwargs.get('title_id')
        if (
            current_user.reviews.filter(title=title_id).exists()
            and self.context['request'].method == 'POST'
        ):
            raise serializers.ValidationError(
                'Больше одного отзыва оставлять нельзя')
        return data


class CategorySerializer(serializers.ModelSerializer):

#  class Meta:
#        model = Category
#        fields = '__all__'
    class Meta:
        model = Category
        exclude = ('id',)
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}}


class GenreSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = Genre
#        fields = '__all__'
    class Meta:
        model = Genre
        exclude = ('id',)
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}}


class TitleSerializer(serializers.ModelSerializer):
    # rating = serializers.IntegerField(read_only=True, allow_null=True)
    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all())
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all())

    class Meta:
        model = Title
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all())],
        required=True,)
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all())])

    class Meta:
        fields = ("username", "email", "first_name",
                  "last_name", "bio", "role")
        model = User


class ReadOnlyTitleSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(
        source='reviews__score__avg', read_only=True)
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )
