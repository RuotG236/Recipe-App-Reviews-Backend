from django.contrib import admin
from .models import Recipe, Category, Ingredient, Favorite, Rating, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'prep_time', 'cook_time', 'servings', 'is_published', 'created_at']
    list_filter = ['category', 'is_published', 'created_at', 'author']
    search_fields = ['title', 'description', 'ingredients', 'instructions']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_published']
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'description', 'category', 'author')
        }),
        ('Recipe Details', {
            'fields': ('ingredients', 'instructions')
        }),
        ('Time & Servings', {
            'fields': ('prep_time', 'cook_time', 'servings')
        }),
        ('Media', {
            'fields': ('image', 'image_url')
        }),
        ('Status', {
            'fields': ('is_published',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'quantity', 'unit', 'notes', 'recipe']
    list_filter = ['recipe']
    search_fields = ['name', 'recipe__title']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['user__username', 'recipe__title']
    readonly_fields = ['created_at']


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe', 'rating', 'created_at', 'updated_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'recipe__title']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe', 'text_preview', 'created_at', 'updated_at']
    list_filter = ['created_at', 'user']
    search_fields = ['user__username', 'recipe__title', 'text']
    readonly_fields = ['created_at', 'updated_at']

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Comment'