from django.contrib import admin
from .models import Recipe, Category, Ingredient, Favorite, Rating, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'created_at']
    list_filter = ['category', 'created_at', 'author']
    search_fields = ['title', 'description', 'ingredients']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'quantity', 'unit', 'recipe']
    list_filter = ['recipe']
    search_fields = ['name', 'recipe__title']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['user__username', 'recipe__title']


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'recipe__title']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe', 'created_at', 'text_preview']
    list_filter = ['created_at', 'user']
    search_fields = ['user__username', 'recipe__title', 'text']

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Comment'