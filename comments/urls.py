from . import views
from django.urls import path

app_name = "comments"

urlpatterns = [
     path("add/<slug:slug>/", views.add_post_comment, name="add_post_comment"),
    path("delete/<int:comment_id>/", views.delete_post_comment, name="delete_post_comment"),
    path("edit/<int:comment_id>/", views.edit_post_comment, name="edit_post_comment"),
    path("product/add/<slug:slug>/", views.add_product_comment, name="add_product_comment"),
    path("product/delete/<int:comment_id>/", views.delete_product_comment, name="delete_product_comment"),
    path("product/edit/<int:comment_id>/", views.edit_product_comment, name="edit_product_comment"),

]
