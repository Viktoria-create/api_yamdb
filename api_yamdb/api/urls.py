from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    # TokenObtainPairView,
    TokenRefreshView,
)

# from .serializers import EmailAuthSerializer
from .views import (APIUser, CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, TitleViewSet, UserViewSet,
                    send_confirmation_code, get_jwt_token)


router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'genres', GenreViewSet)
router.register(r'titles', TitleViewSet)
router.register(r'titles/(?P<title_id>\d+)/reviews',
                ReviewViewSet, basename='reviews')
router.register(r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)'
                r'/comments', CommentViewSet, basename='comments')
router.register(r'users', UserViewSet)

auth_patterns = [
    path('signup/', send_confirmation_code, name='get_token'),
    path('token/', get_jwt_token, name='send_confirmation_code'),
    # path('token/',
    #      TokenObtainPairView.as_view(serializer_class=EmailAuthSerializer),
    #      name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]


urlpatterns = [
    path('v1/auth/', include(auth_patterns)),
    path('v1/users/me/', APIUser.as_view()),
    path('v1/', include(router.urls)),
]
