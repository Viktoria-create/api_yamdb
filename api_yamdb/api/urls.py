from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ReviewViewSet, CommentViewSet

router_v1 = DefaultRouter()
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='review'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='review'
)

urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
