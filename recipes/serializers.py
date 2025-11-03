from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Recipe, Category


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name')
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id',)


class CategorySerializer(serializers.ModelSerializer):
    recipe_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'recipe_count')
        read_only_fields = ('id',)

    def get_recipe_count(self, obj):
        return obj.recipe_set.count()


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'description', 'created_at', 'author', 'category', 'category_name')
        read_only_fields = ('id', 'created_at', 'author')