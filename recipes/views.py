"""
Recipe App Views

API views for handling HTTP requests.
"""
from rest_framework import generics, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.db.models import Q

from .models import Recipe, Category, Favorite, Rating, Comment, Ingredient
from .serializers import (
    RegisterSerializer, UserSerializer, UserUpdateSerializer,
    RecipeListSerializer, RecipeDetailSerializer, RecipeCreateUpdateSerializer,
    CategorySerializer, FavoriteSerializer, RatingSerializer, CommentSerializer
)
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly


# ============================================
# Authentication Views
# ============================================

class RegisterView(generics.CreateAPIView):
    """Handle user registration."""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens for the new user
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    """Handle user login with JWT tokens."""
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = User.objects.get(username=request.data['username'])
            response.data['user'] = UserSerializer(user).data
        return response


class TokenRefreshViewCustom(TokenRefreshView):
    """Handle JWT token refresh."""
    permission_classes = [permissions.AllowAny]


class LogoutView(generics.GenericAPIView):
    """Handle user logout by blacklisting refresh token."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({"detail": "Successfully logged out"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    """Handle user profile retrieval and updates."""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user


# ============================================
# Recipe Views
# ============================================

class RecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Recipe CRUD operations.

    Endpoints:
    - GET /recipes/ - List all recipes
    - POST /recipes/ - Create a recipe
    - GET /recipes/{id}/ - Get recipe detail
    - PUT/PATCH /recipes/{id}/ - Update recipe
    - DELETE /recipes/{id}/ - Delete recipe
    - GET /recipes/my_recipes/ - List user's recipes
    - POST /recipes/{id}/favorite/ - Add to favorites
    - DELETE /recipes/{id}/unfavorite/ - Remove from favorites
    - POST /recipes/{id}/rate/ - Rate a recipe
    - POST /recipes/{id}/comment/ - Add a comment
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = Recipe.objects.filter(is_published=True)

        # Search filter
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(ingredients__icontains=search)
            )

        # Category filter
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__id=category)

        # Author filter
        author = self.request.query_params.get('author', None)
        if author:
            queryset = queryset.filter(author__username=author)

        return queryset.select_related('author', 'category').order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'list':
            return RecipeListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateUpdateSerializer
        return RecipeDetailSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        """Add recipe to user's favorites."""
        recipe = self.get_object()
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            recipe=recipe
        )
        if created:
            return Response({'detail': 'Recipe added to favorites'}, status=status.HTTP_201_CREATED)
        return Response({'detail': 'Recipe already in favorites'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], permission_classes=[permissions.IsAuthenticated])
    def unfavorite(self, request, pk=None):
        """Remove recipe from user's favorites."""
        recipe = self.get_object()
        favorite = Favorite.objects.filter(user=request.user, recipe=recipe).first()
        if favorite:
            favorite.delete()
            return Response({'detail': 'Recipe removed from favorites'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Recipe not in favorites'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def rate(self, request, pk=None):
        """Rate a recipe (1-5 stars)."""
        recipe = self.get_object()
        rating_value = request.data.get('rating')

        if not rating_value:
            return Response({'detail': 'Rating is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rating_value = int(rating_value)
            if not (1 <= rating_value <= 5):
                raise ValueError()
        except (ValueError, TypeError):
            return Response({'detail': 'Rating must be between 1 and 5'}, status=status.HTTP_400_BAD_REQUEST)

        rating, created = Rating.objects.update_or_create(
            user=request.user,
            recipe=recipe,
            defaults={'rating': rating_value}
        )

        return Response(
            RatingSerializer(rating).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def comment(self, request, pk=None):
        """Add a comment to a recipe."""
        recipe = self.get_object()
        text = request.data.get('text')

        if not text or not text.strip():
            return Response({'detail': 'Comment text is required'}, status=status.HTTP_400_BAD_REQUEST)

        comment = Comment.objects.create(
            user=request.user,
            recipe=recipe,
            text=text.strip()
        )

        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_recipes(self, request):
        """Get all recipes created by the current user."""
        recipes = Recipe.objects.filter(author=request.user).order_by('-created_at')
        serializer = RecipeListSerializer(recipes, many=True, context={'request': request})
        return Response(serializer.data)


# ============================================
# Category Views
# ============================================

class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Category CRUD operations."""
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


# ============================================
# Favorite Views
# ============================================

class FavoriteListView(generics.ListAPIView):
    """List all favorites for the current user."""
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('recipe', 'recipe__author',
                                                                              'recipe__category')

    def get_serializer_context(self):
        return {'request': self.request}


# ============================================
# Comment Views
# ============================================

class CommentUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """Handle comment updates and deletion."""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]


# ============================================
# Admin Views
# ============================================

class UserListView(generics.ListAPIView):
    """List all users (admin only)."""
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class UserDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve and update user details (admin only)."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminRecipeListView(generics.ListAPIView):
    """List all recipes for admin management."""
    queryset = Recipe.objects.all().select_related('author', 'category').order_by('-created_at')
    serializer_class = RecipeDetailSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_context(self):
        return {'request': self.request}


class AdminRecipeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin recipe detail, update, and delete."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeDetailSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_context(self):
        return {'request': self.request}