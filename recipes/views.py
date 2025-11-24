"""
Recipe App Views

API views for handling all recipe-related operations.
"""
from rest_framework import generics, viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.db.models import Q, Avg
from django.shortcuts import get_object_or_404

from .models import Recipe, Category, Ingredient, Favorite, Rating, Comment
from .serializers import (
    UserSerializer, RegisterSerializer, UserUpdateSerializer, AdminUserSerializer,
    RecipeListSerializer, RecipeDetailSerializer, RecipeCreateUpdateSerializer,
    CategorySerializer, IngredientSerializer,
    FavoriteSerializer, RatingSerializer, CommentSerializer
)
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly, IsAdminUser, IsOwnerOrAdmin


# ============================================
# Authentication Views
# ============================================

class RegisterView(generics.CreateAPIView):
    """User registration endpoint."""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens for immediate login
        refresh = RefreshToken.for_user(user)

        return Response({
            'message': 'Registration successful',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    """User login endpoint with enhanced response."""
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            # Add user info to response
            user = User.objects.get(username=request.data['username'])
            response.data['user'] = UserSerializer(user).data
            response.data['message'] = 'Login successful'

        return response


class LogoutView(APIView):
    """User logout endpoint - blacklists the refresh token."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response(
                {'message': 'Successfully logged out'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )


class TokenRefreshViewCustom(TokenRefreshView):
    """Custom token refresh view."""
    permission_classes = [permissions.AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
    """User profile view and update."""
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
    - POST /recipes/ - Create a new recipe
    - GET /recipes/{id}/ - Get recipe details
    - PUT/PATCH /recipes/{id}/ - Update a recipe
    - DELETE /recipes/{id}/ - Delete a recipe
    - POST /recipes/{id}/favorite/ - Add to favorites
    - DELETE /recipes/{id}/unfavorite/ - Remove from favorites
    - POST /recipes/{id}/rate/ - Rate a recipe
    - POST /recipes/{id}/comment/ - Comment on a recipe
    - GET /recipes/my_recipes/ - Get current user's recipes
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'ingredient_items__name']
    ordering_fields = ['created_at', 'title', 'prep_time', 'cook_time']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Recipe.objects.filter(is_published=True)

        # Search by title or ingredient
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(ingredient_items__name__icontains=search)
            ).distinct()

        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category_id=category)

        # Filter by author
        author = self.request.query_params.get('author', None)
        if author:
            queryset = queryset.filter(author__username=author)

        # Filter by minimum rating
        min_rating = self.request.query_params.get('min_rating', None)
        if min_rating:
            queryset = queryset.annotate(
                avg_rating=Avg('ratings__rating')
            ).filter(avg_rating__gte=float(min_rating))

        return queryset

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
            return Response(
                {'message': 'Recipe added to favorites'},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {'message': 'Recipe already in favorites'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['delete'], permission_classes=[permissions.IsAuthenticated])
    def unfavorite(self, request, pk=None):
        """Remove recipe from user's favorites."""
        recipe = self.get_object()
        favorite = Favorite.objects.filter(user=request.user, recipe=recipe).first()

        if favorite:
            favorite.delete()
            return Response(
                {'message': 'Recipe removed from favorites'},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {'error': 'Recipe not in favorites'},
            status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def rate(self, request, pk=None):
        """Rate a recipe (1-5 stars)."""
        recipe = self.get_object()
        rating_value = request.data.get('rating')

        try:
            rating_value = int(rating_value)
            if not (1 <= rating_value <= 5):
                raise ValueError()
        except (TypeError, ValueError):
            return Response(
                {'error': 'Rating must be an integer between 1 and 5'},
                status=status.HTTP_400_BAD_REQUEST
            )

        rating, created = Rating.objects.update_or_create(
            user=request.user,
            recipe=recipe,
            defaults={'rating': rating_value}
        )

        return Response(
            {
                'message': 'Rating saved' if created else 'Rating updated',
                'rating': RatingSerializer(rating).data
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def comment(self, request, pk=None):
        """Add a comment to a recipe."""
        recipe = self.get_object()
        text = request.data.get('text', '').strip()

        if not text:
            return Response(
                {'error': 'Comment text is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        comment = Comment.objects.create(
            user=request.user,
            recipe=recipe,
            text=text
        )

        return Response(
            {
                'message': 'Comment added',
                'comment': CommentSerializer(comment).data
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_recipes(self, request):
        """Get all recipes created by the current user."""
        recipes = Recipe.objects.filter(author=request.user).order_by('-created_at')
        page = self.paginate_queryset(recipes)

        if page is not None:
            serializer = RecipeListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = RecipeListSerializer(recipes, many=True, context={'request': request})
        return Response(serializer.data)


# ============================================
# Category Views
# ============================================

class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Category CRUD operations."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


# ============================================
# Favorite Views
# ============================================

class FavoriteListView(generics.ListAPIView):
    """List user's favorite recipes."""
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)


# ============================================
# Comment Views
# ============================================

class CommentUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """Update or delete a comment (owner only)."""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]


# ============================================
# Admin Views
# ============================================

class AdminUserListView(generics.ListAPIView):
    """Admin: List all users."""
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']


class AdminUserDetailView(generics.RetrieveUpdateAPIView):
    """Admin: View and update user details (e.g., deactivate)."""
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUser]


class AdminRecipeListView(generics.ListAPIView):
    """Admin: List all recipes (including unpublished)."""
    queryset = Recipe.objects.all().order_by('-created_at')
    serializer_class = RecipeDetailSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'author__username']

    def get_serializer_context(self):
        return {'request': self.request}


class AdminRecipeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin: View, update, or delete any recipe."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeDetailSerializer
    permission_classes = [IsAdminUser]

    def get_serializer_context(self):
        return {'request': self.request}