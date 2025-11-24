from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Recipe, Category, Favorite, Rating, Comment, Ingredient


# ------------------------
# User Registration
# ------------------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken")
        return value

    def validate_email(self, value):
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )


# ------------------------
# User Profile
# ------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


# ------------------------
# Category
# ------------------------
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


# ------------------------
# Recipe List & Detail
# ------------------------
class RecipeListSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    category_name = serializers.ReadOnlyField(source="category.name")

    class Meta:
        model = Recipe
        fields = ["id", "title", "author", "category_name", "created_at"]


class RecipeDetailSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    category_name = serializers.ReadOnlyField(source="category.name")
    ingredients = serializers.StringRelatedField(many=True, read_only=True)
    ratings = serializers.StringRelatedField(many=True, read_only=True)
    comments = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = [
            "id", "title", "description", "created_at",
            "author", "category", "category_name",
            "ingredients", "ratings", "comments"
        ]
        read_only_fields = ["created_at", "author"]


# ------------------------
# Favorite
# ------------------------
class FavoriteSerializer(serializers.ModelSerializer):
    recipe_title = serializers.ReadOnlyField(source="recipe.title")

    class Meta:
        model = Favorite
        fields = ["id", "recipe", "recipe_title"]


# ------------------------
# Rating
# ------------------------
class RatingSerializer(serializers.ModelSerializer):
    recipe_title = serializers.ReadOnlyField(source="recipe.title")
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Rating
        fields = ["id", "recipe", "recipe_title", "user", "rating"]


# ------------------------
# Comment
# ------------------------
class CommentSerializer(serializers.ModelSerializer):
    recipe_title = serializers.ReadOnlyField(source="recipe.title")
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Comment
        fields = ["id", "recipe", "recipe_title", "user", "text", "created_at"]
        read_only_fields = ["created_at", "user"]
