from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (APIGetToken, APISignup, CategoryViewSet, CommentViewSet,
                    GenreViewSet, ReviewViewSet, TitleViewSet, UserViewSet)

router_v1 = DefaultRouter()

router_v1.register(r'categories', CategoryViewSet)
router_v1.register(r'genres', GenreViewSet)
router_v1.register(r'titles', TitleViewSet)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)

router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)
router_v1.register('users', UserViewSet)

urlpatterns = [
    path('api/v1/', include([
        path('', include(router_v1.urls)),
        path('auth/', include([
            path('signup/', APISignup.as_view(), name='signup'),
            path('token/', APIGetToken.as_view(), name='token'),
        ]))
    ]))
]
