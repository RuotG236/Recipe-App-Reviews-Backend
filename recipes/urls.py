"""
Recipe App URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    # Auth views
    RegisterView, LoginView, LogoutView, TokenRefreshViewCustom, ProfileView,
    # Recipe views
    RecipeViewSet, CategoryViewSet,
    # User views
    FavoriteListView, CommentUpdateDeleteView,
    # Admin views
    AdminUserListView, AdminUserDetailView,
    AdminRecipeListView, AdminRecipeDetailView
)

# Create router for viewsets
router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/refresh/', TokenRefreshViewCustom.as_view(), name='token-refresh'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),

    # User endpoints
    path('favorites/', FavoriteListView.as_view(), name='favorites'),
    path('comments/<int:pk>/', CommentUpdateDeleteView.as_view(), name='comment-detail'),

    # Admin endpoints
    path('admin/users/', AdminUserListView.as_view(), name='admin-users'),
    path('admin/users/<int:pk>/', AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('admin/recipes/', AdminRecipeListView.as_view(), name='admin-recipes'),
    path('admin/recipes/<int:pk>/', AdminRecipeDetailView.as_view(), name='admin-recipe-detail'),

    # Router URLs (recipes and categories)
    path('', include(router.urls)),
]