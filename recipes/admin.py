"""
Django Admin Configuration for Recipe App
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Recipe, Category, Ingredient, Favorite, Rating, Comment


class IngredientInline(admin.TabularInline):
    """Inline admin for ingredients within recipe."""
    model = Ingredient
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'recipes_count', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']

    def recipes_count(self, obj):
        return obj.recipes.count()
    recipes_count.short_description = 'Recipes'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'avg_rating',
                    'is_published', 'created_at']
    list_filter = ['category', 'is_published', 'created_at', 'author']
    search_fields = ['title', 'description', 'author__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [IngredientInline]
    list_editable = ['is_published']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'description', 'category', 'author')
        }),
        ('Details', {
            'fields': ('instructions', 'prep_time', 'cook_time', 'servings', 'image')
        }),
        ('Status', {
            'fields': ('is_published',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def avg_rating(self, obj):
        rating = obj.average_rating()
        return f"{rating:.1f} ★" if rating > 0 else "No ratings"
    avg_rating.short_description = 'Rating'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'quantity', 'unit', 'recipe']
    list_filter = ['unit', 'recipe__category']
    search_fields = ['name', 'recipe__title']
    autocomplete_fields = ['recipe']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'recipe__title']
    autocomplete_fields = ['user', 'recipe']


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe', 'rating_stars', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'recipe__title']
    autocomplete_fields = ['user', 'recipe']

    def rating_stars(self, obj):
        return '★' * obj.rating + '☆' * (5 - obj.rating)
    rating_stars.short_description = 'Rating'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe', 'text_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'recipe__title', 'text']
    autocomplete_fields = ['user', 'recipe']

    def text_preview(self, obj):
        return obj.text[:75] + '...' if len(obj.text) > 75 else obj.text
    text_preview.short_description = 'Comment'


# Customize admin site headers
admin.site.site_header = 'Recipe App Administration'
admin.site.site_title = 'Recipe App Admin'
admin.site.index_title = 'Welcome to Recipe App Admin Panel'