"""
Recipe App Serializers

"""
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Recipe, Category, Ingredient, Favorite, Rating, Comment


# ============================================
# User Serializers
# ============================================

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model (read-only representation)."""
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'is_staff', 'is_active', 'date_joined', 'recipes_count']
        read_only_fields = ['id', 'date_joined', 'recipes_count']

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm',
                  'first_name', 'last_name']

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username already exists.")
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters.")
        if len(value) > 30:
            raise serializers.ValidationError("Username cannot exceed 30 characters.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value

    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password_confirm": "Passwords do not match."
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already in use.")
        return value


class AdminUserSerializer(serializers.ModelSerializer):
    """Serializer for admin user management."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'is_staff', 'is_active', 'date_joined', 'last_login']
        read_only_fields = ['id', 'username', 'date_joined', 'last_login']


# ============================================
# Category Serializers
# ============================================

class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'recipes_count', 'created_at']
        read_only_fields = ['id', 'created_at', 'recipes_count']

    def get_recipes_count(self, obj):
        return obj.recipes.count()


# ============================================
# Ingredient Serializers
# ============================================

class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for Ingredient model."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'quantity', 'unit', 'notes']
        read_only_fields = ['id']


# ============================================
# Rating Serializers - UPDATED WITH COMMENT
# ============================================

class RatingSerializer(serializers.ModelSerializer):
    """Serializer for Rating model."""
    user = serializers.ReadOnlyField(source='user.username')
    user_id = serializers.ReadOnlyField(source='user.id')

    class Meta:
        model = Rating
        fields = ['id', 'user', 'user_id', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'user_id', 'created_at', 'updated_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value


# ============================================
# Comment Serializers
# ============================================

class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model."""
    user = serializers.ReadOnlyField(source='user.username')
    user_id = serializers.ReadOnlyField(source='user.id')

    class Meta:
        model = Comment
        fields = ['id', 'user', 'user_id', 'text', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'user_id', 'created_at', 'updated_at']


# ============================================
# Recipe Serializers
# ============================================

class RecipeListSerializer(serializers.ModelSerializer):
    """Serializer for Recipe list view."""
    author = serializers.ReadOnlyField(source='author.username')
    category_name = serializers.ReadOnlyField(source='category.name')
    average_rating = serializers.SerializerMethodField()
    total_ratings = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'description', 'image_url', 'author',
            'category', 'category_name', 'prep_time', 'cook_time', 'servings',
            'average_rating', 'total_ratings', 'created_at'
        ]

    def get_average_rating(self, obj):
        return round(obj.average_rating(), 1)

    def get_total_ratings(self, obj):
        return obj.total_ratings()


class RecipeDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Recipe model."""
    author = serializers.ReadOnlyField(source='author.username')
    author_id = serializers.ReadOnlyField(source='author.id')
    category_name = serializers.ReadOnlyField(source='category.name')
    ingredients_list = IngredientSerializer(source='ingredient_items', many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    ratings = RatingSerializer(many=True, read_only=True)  # Include ratings with comments
    average_rating = serializers.SerializerMethodField()
    total_ratings = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'description', 'instructions', 'ingredients',
            'ingredients_list', 'image_url', 'author', 'author_id',
            'category', 'category_name', 'prep_time', 'cook_time', 'servings',
            'is_published', 'average_rating', 'total_ratings', 'is_favorited',
            'user_rating', 'comments', 'ratings',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'author_id', 'created_at', 'updated_at']

    def get_average_rating(self, obj):
        return round(obj.average_rating(), 1)

    def get_total_ratings(self, obj):
        return obj.total_ratings()

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, recipe=obj).exists()
        return False

    def get_user_rating(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                rating = Rating.objects.get(user=request.user, recipe=obj)
                return rating.rating
            except Rating.DoesNotExist:
                return None
        return None


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating recipes."""
    ingredients_list = IngredientSerializer(source='ingredient_items', many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'description', 'instructions', 'image_url',
            'ingredients', 'ingredients_list',
            'category', 'prep_time', 'cook_time', 'servings',
            'is_published'
        ]
        read_only_fields = ['id']

    def validate_title(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters.")
        return value

    def validate_description(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Description must be at least 10 characters.")
        return value

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredient_items', [])
        recipe = Recipe.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            Ingredient.objects.create(recipe=recipe, **ingredient_data)

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredient_items', None)

        # Update recipe fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update ingredients if provided
        if ingredients_data is not None:
            instance.ingredient_items.all().delete()
            for ingredient_data in ingredients_data:
                Ingredient.objects.create(recipe=instance, **ingredient_data)

        return instance


# ============================================
# Favorite Serializers
# ============================================

class FavoriteSerializer(serializers.ModelSerializer):
    """Serializer for Favorite model."""
    recipe = RecipeListSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'recipe', 'created_at']
        read_only_fields = ['id', 'created_at']
