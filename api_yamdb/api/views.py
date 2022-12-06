# from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings

from rest_framework import filters, status, viewsets
# permissions,
from rest_framework.decorators import api_view
# , permission_classes
# from rest_framework.permissions import AllowAny
# IsAuthenticated, IsAdminUser
# from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import mixins, viewsets
from rest_framework_simplejwt.tokens import AccessToken

import random

from reviews.models import Category, Genre, Review, Title, User
# from .email import email_is_valid, generate_mail
# from .filters import TitlesFilter
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsAdminModeratorOwnerOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReadOnlyTitleSerializer,
                          ReviewSerializer,
                          TitleSerializer,
                          UserSerializer, CheckConfirmationCodeSerializer,
                          SendCodeSerializer)
# RegistrationizerSerial, TokenSerializer, UserEditSerializer,


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
    # filterset_class = TitlesFilter

    def get_serializer_class(self):
        if self.action in ("retrieve", "list"):
            return ReadOnlyTitleSerializer
        return TitleSerializer


# @api_view(['POST'])
# @permission_classes([AllowAny])
# def send_confirmation_code(request):
#     email = request.data.get('email')
#     if email is None:
#         message = 'Email is required'
#     else:
#         if email_is_valid(email):
#             user = get_object_or_404(User, email=email)
#             confirmation_code = default_token_generator.make_token(user)
#             generate_mail(email, confirmation_code)
#             user.confirmation_code = confirmation_code
#             message = email
#             user.save()
#         else:
#             message = 'Valid email is required'
#     return Response({'email': message})

@api_view(['POST'])
def send_confirmation_code(request):
    serializer = SendCodeSerializer(data=request.data)
    email = request.data.get('email', False)
    if serializer.is_valid():
        confirmation_code = ''.join(map(str, random.sample(range(10), 6)))
        user = User.objects.filter(email=email).exists()
        if not user:
            User.objects.create_user(email=email)
        User.objects.filter(email=email).update(
            confirmation_code=make_password(confirmation_code, salt=None, hasher='default')
        )
        mail_subject = 'Confirmation code for Yamdb'
        message = f'Your confirmation code {confirmation_code}'
        send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        return Response(f'The code has been sent to email adress {email}', status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view
def get_jwt_token(request):
    serializer = CheckConfirmationCodeSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.data.get('email')
        confirmation_code = serializer.data.get('confirmation_code')
        user = get_object_or_404(User, email=email)
        if check_password(confirmation_code, user.confirmation_code):
            token = AccessToken.for_user(user)
            return Response({token: f'{token}'}, status=status.HTTP_200_OK)
        return Response({'confirmation_code': 'Wrong confirmation code'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = [IsAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username', ]


class APIUser(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            user = get_object_or_404(User, id=request.user.id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        return Response(
            'You are not authorized',
            status=status.HTTP_401_UNAUTHORIZED
        )

    def patch(self, request):
        if request.user.is_authenticated:
            user = get_object_or_404(User, id=request.user.id)
            serializer = UserSerializer(
                user,
                data=request.data,
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_200_OK
                )
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            'You are not authorized',
            status=status.HTTP_401_UNAUTHORIZED
        )
# class UserViewSet(viewsets.ModelViewSet):
#     lookup_field = "username"
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     pagination_class = PageNumberPagination
#     permission_classes = (IsAdmin,)

#     def users_own_profile(self, request):
#         user = request.user
#         if request.method == "GET":
#             serializer = self.get_serializer(user)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         if request.method == "PATCH":
#             serializer = self.get_serializer(
#                 user,
#                 data=request.data,
#                 partial=True)
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


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
