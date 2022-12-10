from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, TitleViewSet, UserViewSet,
                    APISignup, APIGetToken,)

# email_verifications, self_registration,

router_v1 = DefaultRouter()

router_v1.register(r'categories', CategoryViewSet)
router_v1.register(r'genres', GenreViewSet)
router_v1.register(r'titles', TitleViewSet)
router_v1.register(r'titles/(?P<title_id>\d+)/reviews',
                   ReviewViewSet, basename='reviews')
router_v1.register(r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)'
                   r'/comments', CommentViewSet, basename='comments')
router_v1.register('users', UserViewSet)

auth_patterns = [
    path('signup/', APISignup.as_view({'get': 'list'}), name='apisignup'),
    path('token/', APIGetToken.as_view({'get': 'list'}), name='apigettoken'),
    # path('signup/', self_registration, name="self_registration"),
    # path('token/', email_verifications, name="email_verifications"),
]


urlpatterns = [
    path('v1/auth/', include(auth_patterns)),
    path('v1/', include(router_v1.urls)),
]
