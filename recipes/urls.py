from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, LoginView, TokenRefreshViewCustom, LogoutView, ProfileView,
    RecipeViewSet, CategoryViewSet, FavoriteListView, CommentUpdateDeleteView,
    UserListView, UserDetailView, AdminRecipeListView, AdminRecipeDetailView
)

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshViewCustom.as_view(), name='token_refresh'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),
    
    # User endpoints
    path('favorites/', FavoriteListView.as_view(), name='favorites'),
    path('comments/<int:pk>/', CommentUpdateDeleteView.as_view(), name='comment-detail'),
    
    # Admin endpoints
    path('admin/users/', UserListView.as_view(), name='admin-users'),
    path('admin/users/<int:pk>/', UserDetailView.as_view(), name='admin-user-detail'),
    path('admin/recipes/', AdminRecipeListView.as_view(), name='admin-recipes'),
    path('admin/recipes/<int:pk>/', AdminRecipeDetailView.as_view(), name='admin-recipe-detail'),
    
    # ViewSet routes
    path('', include(router.urls)),
]
