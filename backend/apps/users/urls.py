"""
用户路由
"""
from django.urls import path
from . import views

urlpatterns = [
    path("users/me/", views.UserMeView.as_view(), name="user-me"),
    path("users/me/add/", views.UserCreateView.as_view(), name="user-create"),
    path("users/cooked/<int:recipe_id>/", views.UserCookedRecipeView.as_view(), name="user-cooked"),
]
