from rest_framework import generics, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.db.models import Q

from .models import Recipe, Category, Favorite, Rating, Comment, Ingredient
from .serializers import (
    RegisterSerializer, UserSerializer, RecipeListSerializer,
    RecipeDetailSerializer, CategorySerializer, FavoriteSerializer,
    RatingSerializer, CommentSerializer
)
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly


# Authentication Views
class RegisterView(generics.CreateAPIView):
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
        }, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = User.objects.get(username=request.data['username'])
            response.data['user'] = UserSerializer(user).data
        return response


class TokenRefreshViewCustom(TokenRefreshView):
    permission_classes = [permissions.AllowAny]


class LogoutView(generics.GenericAPIView):
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
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# Recipe Views
class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = Recipe.objects.all()

        # Search functionality
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

        return queryset.order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'list':
            return RecipeListSerializer
        return RecipeDetailSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
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
        recipe = self.get_object()
        favorite = Favorite.objects.filter(user=request.user, recipe=recipe).first()
        if favorite:
            favorite.delete()
            return Response({'detail': 'Recipe removed from favorites'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Recipe not in favorites'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def rate(self, request, pk=None):
        recipe = self.get_object()
        rating_value = request.data.get('rating')

        if not rating_value or not (1 <= int(rating_value) <= 5):
            return Response({'detail': 'Rating must be between 1 and 5'}, status=status.HTTP_400_BAD_REQUEST)

        rating, created = Rating.objects.update_or_create(
            user=request.user,
            recipe=recipe,
            defaults={'rating': rating_value}
        )

        return Response(RatingSerializer(rating).data,
                        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def comment(self, request, pk=None):
        recipe = self.get_object()
        text = request.data.get('text')

        if not text:
            return Response({'detail': 'Comment text is required'}, status=status.HTTP_400_BAD_REQUEST)

        comment = Comment.objects.create(
            user=request.user,
            recipe=recipe,
            text=text
        )

        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_recipes(self, request):
        recipes = Recipe.objects.filter(author=request.user)
        serializer = RecipeListSerializer(recipes, many=True, context={'request': request})
        return Response(serializer.data)


# Category Views
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


# Favorite Views
class FavoriteListView(generics.ListAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)


# Comment Views
class CommentUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]


# Admin Views
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminRecipeListView(generics.ListAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeDetailSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_context(self):
        return {'request': self.request}


class AdminRecipeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeDetailSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_context(self):
        return {'request': self.request}