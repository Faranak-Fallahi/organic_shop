from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


app_name = "blog"


router = DefaultRouter()
router.register(
    "posts",
    views.PostViewSet,
    basename="post"
)


urlpatterns = [
    path(
        "",
        views.post_list_view,
        name="blog-page"
    ),

    path(
        "article/<slug:slug>/",
        views.post_detail_view,
        name="blog-detail"
    ),

    path(
        "api/",
        include(router.urls)
    ),
]
