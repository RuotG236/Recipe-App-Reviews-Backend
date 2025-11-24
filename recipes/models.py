"""
Recipe App Models

Database models for the Recipe application.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    """Recipe category for organization."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Main recipe model containing all recipe information."""
    title = models.CharField(max_length=255)
    description = models.TextField(help_text="Brief description of the recipe")
    instructions = models.TextField(
        help_text="Step-by-step cooking instructions",
        blank=True,
        default=''
    )
    prep_time = models.PositiveIntegerField(
        help_text="Preparation time in minutes",
        default=0
    )
    cook_time = models.PositiveIntegerField(
        help_text="Cooking time in minutes",
        default=0
    )
    servings = models.PositiveIntegerField(default=4)
    image = models.ImageField(
        upload_to='recipes/',
        blank=True,
        null=True,
        help_text="Recipe image"
    )
    image_url = models.URLField(
        max_length=500,
        blank=True,
        default='',
        help_text="External image URL"
    )

    # Relationships
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recipes'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Status
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def average_rating(self):
        """Calculate and return the average rating for this recipe."""
        ratings = self.ratings.all()
        if ratings.exists():
            return sum(r.rating for r in ratings) / ratings.count()
        return 0.0

    def total_ratings(self):
        """Return the total number of ratings."""
        return self.ratings.count()

    def total_time(self):
        """Return total cooking time (prep + cook)."""
        return self.prep_time + self.cook_time

    def get_image(self):
        """Return image URL from either upload or external URL."""
        if self.image:
            return self.image.url
        return self.image_url or None


class Ingredient(models.Model):
    """Ingredient model linked to recipes."""
    UNIT_CHOICES = [
        ('', 'No unit'),
        ('g', 'Grams'),
        ('kg', 'Kilograms'),
        ('ml', 'Milliliters'),
        ('l', 'Liters'),
        ('tsp', 'Teaspoon'),
        ('tbsp', 'Tablespoon'),
        ('cup', 'Cup'),
        ('oz', 'Ounce'),
        ('lb', 'Pound'),
        ('piece', 'Piece'),
        ('pinch', 'Pinch'),
        ('to taste', 'To Taste'),
    ]

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_list'
    )
    name = models.CharField(max_length=200)
    quantity = models.CharField(max_length=50, blank=True, default='')
    unit = models.CharField(
        max_length=20,
        choices=UNIT_CHOICES,
        blank=True,
        default=''
    )
    notes = models.CharField(max_length=200, blank=True, default='')

    class Meta:
        ordering = ['id']

    def __str__(self):
        parts = []
        if self.quantity:
            parts.append(str(self.quantity))
        if self.unit:
            parts.append(self.unit)
        parts.append(self.name)
        return ' '.join(parts)


class Favorite(models.Model):
    """User's favorite recipes."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.recipe.title}"


class Rating(models.Model):
    """User ratings for recipes (1-5 stars)."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'recipe')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} rated {self.recipe.title}: {self.rating}/5"


class Comment(models.Model):
    """User comments on recipes."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        preview = self.text[:50] + '...' if len(self.text) > 50 else self.text
        return f"{self.user.username}: {preview}"