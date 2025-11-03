from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Recipe, Category


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
# Category
# ------------------------
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


# ------------------------
# Recipe
# ------------------------
class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    category_name = serializers.ReadOnlyField(source="category.name")

    class Meta:
        model = Recipe
        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "author",
            "category",
            "category_name",
        ]
        read_only_fields = ["created_at", "author"]
