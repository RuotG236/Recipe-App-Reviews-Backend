"""
Recipe App Serializers

Serializers for converting model instances to JSON and vice versa.
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
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_staff', 'is_active', 'date_joined', 'recipes_count'
        ]
        read_only_fields = ['id', 'date_joined', 'recipes_count']

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
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
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name'
        ]

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username already exists.")
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already registered.")
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
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_staff', 'is_active', 'date_joined', 'last_login', 'recipes_count'
        ]
        read_only_fields = ['id', 'username', 'date_joined', 'last_login']

    def get_recipes_count(self, obj):
        return obj.recipes.count()


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
        return obj.recipes.filter(is_published=True).count()


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
# Rating Serializers
# ============================================

class RatingSerializer(serializers.ModelSerializer):
    """Serializer for Rating model."""
    user = serializers.ReadOnlyField(source='user.username')
    user_id = serializers.ReadOnlyField(source='user.id')

    class Meta:
        model = Rating
        fields = ['id', 'user', 'user_id', 'rating', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'user_id', 'created_at', 'updated_at']


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
    """Serializer for recipe list view (minimal data)."""
    author = serializers.ReadOnlyField(source='author.username')
    author_id = serializers.ReadOnlyField(source='author.id')
    category_name = serializers.ReadOnlyField(source='category.name')
    average_rating = serializers.SerializerMethodField()
    total_ratings = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    total_time = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'description', 'image', 'image_url',
            'author', 'author_id', 'category', 'category_name',
            'prep_time', 'cook_time', 'total_time', 'servings',
            'average_rating', 'total_ratings', 'is_favorited',
            'created_at'
        ]

    def get_average_rating(self, obj):
        return round(obj.average_rating(), 1)

    def get_total_ratings(self, obj):
        return obj.total_ratings()

    def get_total_time(self, obj):
        return obj.total_time()

    def get_image_url(self, obj):
        return obj.get_image()

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(user=request.user).exists()
        return False


class RecipeDetailSerializer(serializers.ModelSerializer):
    """Serializer for recipe detail view (full data)."""
    author = serializers.ReadOnlyField(source='author.username')
    author_id = serializers.ReadOnlyField(source='author.id')
    category_name = serializers.ReadOnlyField(source='category.name')
    ingredients_list = IngredientSerializer(many=True, read_only=True)
    ratings = RatingSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    total_ratings = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField()
    total_time = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'description', 'instructions', 'image', 'image_url',
            'author', 'author_id', 'category', 'category_name',
            'prep_time', 'cook_time', 'total_time', 'servings',
            'ingredients_list', 'ratings', 'comments',
            'average_rating', 'total_ratings', 'user_rating',
            'is_favorited', 'is_published', 'is_author',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'author_id', 'created_at', 'updated_at']

    def get_average_rating(self, obj):
        return round(obj.average_rating(), 1)

    def get_total_ratings(self, obj):
        return obj.total_ratings()

    def get_total_time(self, obj):
        return obj.total_time()

    def get_image_url(self, obj):
        return obj.get_image()

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(user=request.user).exists()
        return False

    def get_user_rating(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            rating = obj.ratings.filter(user=request.user).first()
            if rating:
                return rating.rating
        return None

    def get_is_author(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author == request.user
        return False


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating recipes."""
    ingredients = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        write_only=True
    )
    # Accept ingredients as text (one per line) for simpler form submission
    ingredients_text = serializers.CharField(
        required=False,
        write_only=True,
        allow_blank=True
    )

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'description', 'instructions', 'image', 'image_url',
            'category', 'prep_time', 'cook_time', 'servings',
            'ingredients', 'ingredients_text', 'is_published'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        ingredients_text = validated_data.pop('ingredients_text', '')

        recipe = Recipe.objects.create(**validated_data)

        # Handle structured ingredients
        for ingredient_data in ingredients_data:
            Ingredient.objects.create(recipe=recipe, **ingredient_data)

        # Handle text-based ingredients (one per line)
        if ingredients_text:
            for line in ingredients_text.strip().split('\n'):
                line = line.strip()
                if line:
                    Ingredient.objects.create(recipe=recipe, name=line)

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        ingredients_text = validated_data.pop('ingredients_text', None)

        # Update recipe fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update ingredients if provided
        if ingredients_data is not None:
            instance.ingredients_list.all().delete()
            for ingredient_data in ingredients_data:
                Ingredient.objects.create(recipe=instance, **ingredient_data)

        if ingredients_text is not None:
            instance.ingredients_list.all().delete()
            for line in ingredients_text.strip().split('\n'):
                line = line.strip()
                if line:
                    Ingredient.objects.create(recipe=instance, name=line)

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