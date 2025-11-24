from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructions = models.TextField(blank=True)
    ingredients = models.TextField(blank=True, help_text="Legacy field for plain text ingredients")
    image = models.ImageField(upload_to='recipes/', blank=True, null=True)
    image_url = models.URLField(blank=True, help_text="External image URL")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='recipes')
    prep_time = models.PositiveIntegerField(default=0, help_text="Preparation time in minutes")
    cook_time = models.PositiveIntegerField(default=0, help_text="Cooking time in minutes")
    servings = models.PositiveIntegerField(default=4)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def average_rating(self):
        """Calculate average rating for the recipe."""
        ratings = self.ratings.all()
        if ratings.exists():
            return sum(r.rating for r in ratings) / ratings.count()
        return 0

    def total_ratings(self):
        """Get total number of ratings."""
        return self.ratings.count()

    def total_time(self):
        """Calculate total cooking time."""
        return self.prep_time + self.cook_time

    def get_image_url(self):
        """Return image URL from either uploaded image or external URL."""
        if self.image:
            return self.image.url
        return self.image_url or ''


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.CharField(max_length=50, blank=True)
    unit = models.CharField(max_length=50, blank=True)
    notes = models.CharField(max_length=200, blank=True)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredient_items')

    def __str__(self):
        parts = []
        if self.quantity:
            parts.append(self.quantity)
        if self.unit:
            parts.append(self.unit)
        parts.append(self.name)
        if self.notes:
            parts.append(f"({self.notes})")
        return " ".join(parts)


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.recipe.title}"


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f"{self.user.username} rated {self.recipe.title}: {self.rating}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} on {self.recipe.title}"