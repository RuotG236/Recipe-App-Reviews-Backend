from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, TokenRefresh, LogoutView, RecipeViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r"recipes", RecipeViewSet, basename="recipe")
router.register(r"categories", CategoryViewSet, basename="category")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/refresh/", TokenRefresh.as_view(), name="token_refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
]
