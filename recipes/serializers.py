from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Recipe, Category


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        return user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    category_name = serializers.ReadOnlyField(source="category.name")

    class Meta:
        model = Recipe
        fields = ["id", "title", "description", "created_at", "author", "category", "category_name"]
        read_only_fields = ["created_at", "author"]