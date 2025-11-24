"""
Recipe App Admin Configuration
"""
from django.contrib import admin
from .models import Recipe, Category, Ingredient, Favorite, Rating, Comment


class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'recipes_count', 'created_at']
    search_fields = ['name']

    def recipes_count(self, obj):
        return obj.recipes.count()
    recipes_count.short_description = 'Recipes'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'avg_rating', 'is_published', 'created_at']
    list_filter = ['category', 'is_published', 'created_at', 'author']
    search_fields = ['title', 'description', 'author__username']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_published']
    date_hierarchy = 'created_at'
    inlines = [IngredientInline]

    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'description', 'category', 'author')
        }),
        ('Details', {
            'fields': ('instructions', 'prep_time', 'cook_time', 'servings')
        }),
        ('Media', {
            'fields': ('image', 'image_url')
        }),
        ('Status', {
            'fields': ('is_published', 'created_at', 'updated_at')
        }),
    )

    def avg_rating(self, obj):
        rating = obj.average_rating()
        return f"{rating:.1f} ⭐" if rating > 0 else "No ratings"
    avg_rating.short_description = 'Rating'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'quantity', 'unit', 'recipe']
    list_filter = ['unit', 'recipe']
    search_fields = ['name', 'recipe__title']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['user__username', 'recipe__title']


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe', 'stars', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'recipe__title']

    def stars(self, obj):
        return '⭐' * obj.rating
    stars.short_description = 'Rating'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe', 'text_preview', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['user__username', 'recipe__title', 'text']

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Comment'


# Customize admin site
admin.site.site_header = 'Recipe App Administration'
admin.site.site_title = 'Recipe App Admin'
admin.site.index_title = 'Recipe App Dashboard'