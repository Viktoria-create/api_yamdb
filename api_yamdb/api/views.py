from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework import mixins, viewsets

from reviews.models import Category, Genre, Review, Title, User
from .filters import TitlesFilter
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsAdminModeratorOwnerOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ProfileEditSerializer, ReadOnlyTitleSerializer, RegistrationSerializer,
                          ReviewSerializer,
                          TitleSerializer, TokenSerializer,
                          UserSerializer)


class ListCreateDestroyViewSet(mixins.ListModelMixin,
                               mixins.CreateModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet,):
    pass


class CategoryViewSet(ListCreateDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class GenreViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(rating=Avg("reviews__score",))
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitlesFilter

    def get_serializer_class(self):
        if self.action in ("retrieve", "list"):
            return ReadOnlyTitleSerializer
        return TitleSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = "username"
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)

    @action(
        detail=False,
        methods=["GET", "PATCH"],
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        if request.method == "PATCH":
            serializer = ProfileEditSerializer(
                request.user, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST",])
@permission_classes([AllowAny])
def self_registration(request):
    if request.method == "POST":
        serializer = RegistrationSerializer(data=request.data)
        data = {}
        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            user = serializer.save()
            data["email"] = user.email
            data["username"] = user.username
            code = default_token_generator.make_token(user)
            send_mail(
                subject="yamdb registrations",
                message=f"Пользователь {user.username} успешно"
                f"зарегистрирован.\n"
                f"Код подтверждения: {code}",
                from_email=None,
                recipient_list=[user.email],
            )
        return Response(data, status=status.HTTP_200_OK)


@api_view(["POST",])
@permission_classes([AllowAny])
def email_verifications(request):
    serializer = TokenSerializer(data=request.data)
    data = {}
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    user = get_object_or_404(
        User, username=serializer.validated_data["username"]
    )
    code = serializer.validated_data["confirmation_code"]
    if default_token_generator.check_token(user, code):
        token = AccessToken.for_user(user)
        data["token"] = str(token)
        return Response(data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAdminModeratorOwnerOrReadOnly]

    def get_serializer_context(self):
        context = super(ReviewViewSet, self).get_serializer_context()
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        context.update({"title": title})
        return context

    def get_queryset(self):
        title_id = self.kwargs.get("title_id")
        title = get_object_or_404(Title, pk=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get("title_id")
        title = get_object_or_404(Title, pk=title_id)
        serializer.save(author=self.request.user, title=title)
        return title.reviews.all()


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAdminModeratorOwnerOrReadOnly]
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAdminModeratorOwnerOrReadOnly]
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get("review_id"))
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id, title=title_id)
        serializer.save(author=self.request.user, review=review)
