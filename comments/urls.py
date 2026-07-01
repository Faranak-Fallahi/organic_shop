from django.urls import path
from . import views

app_name = "comments"

urlpatterns = [
    path(
        "add/<slug:slug>/",
        views.add_post_comment,
        name="add_post_comment"
    ),

    path(
        "delete/<int:comment_id>/",
        views.delete_post_comment,
        name="delete_post_comment"
    ),

    path(
        "edit/<int:comment_id>/",
        views.edit_post_comment,
        name="edit_post_comment"
    ),
]
