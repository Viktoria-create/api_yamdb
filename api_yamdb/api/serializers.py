from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import ValidationError
from reviews.models import Category, Comment, Genre, Review, Title
from reviews.validators import username_validate

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                "Имя пользователя не может быть 'me'."
            )
        return value

    def validate(self, data):
        if self.context['request'].POST:
            sources = list(User.objects.values('username', 'email'))
            for item in sources:
                for field in set(item.items()):
                    if field in set(data.items()):
                        raise ValidationError('error')
        return data


class ProfileEditSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )
        model = User
        read_only_fields = ('role',)

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                "Имя пользователя не может быть 'me'."
            )
        return value


class GetTokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        validators=(username_validate,)
    )
    confirmation_code = serializers.CharField(required=True)

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                "Имя пользователя не может быть 'me'."
            )
        return value

    class Meta:
        model = User
        fields = (
            'username',
            'confirmation_code'
        )


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)

    def validate_username(self, name):
        if name == 'me':
            raise serializers.ValidationError(
                "Имя пользователя не может быть 'me'."
            )
        return name

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        if (
            User.objects.filter(username=username).exists()
            and User.objects.get(username=username).email != email
        ):
            raise serializers.ValidationError("Пользователь существует!")
        if (
            User.objects.filter(email=email).exists()
            and User.objects.get(email=email).username != username
        ):
            raise serializers.ValidationError("Емайл существует!")
        return data

    class Meta:
        model = User
        fields = ('username', 'email')


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True,
                                          slug_field='username')

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True,
                                          slug_field='username')

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
                'Больше одного отзыва оставлять нельзя.'
            )
        return data

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        exclude = ('id',)
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}}


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        exclude = ('id',)
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}}


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True, allow_null=True)
    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all())
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all())

    class Meta:
        model = Title
        fields = '__all__'


class ReadOnlyTitleSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True)
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )
