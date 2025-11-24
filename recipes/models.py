
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    Main recipe model containing all recipe information.
    """
    title = models.CharField(max_length=255)
    description = models.TextField(help_text="Brief description of the recipe")
    instructions = models.TextField(help_text="Step-by-step cooking instructions")
    prep_time = models.PositiveIntegerField(
        help_text="Preparation time in minutes",
        default=0
    )
    cook_time = models.PositiveIntegerField(
        help_text="Cooking time in minutes",
        default=0
    )
    servings = models.PositiveIntegerField(default=1)
    image = models.ImageField(
        upload_to='recipes/',
        blank=True,
        null=True,
        help_text="Recipe image"
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

    @property
    def is_favorited_by(self):
        """Helper property for serializer context."""
        return None  # Handled in serializer with request context


class Ingredient(models.Model):
    """
    Ingredient model linked to recipes.
    """
    UNIT_CHOICES = [
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
        related_name='ingredient_items'
    )
    name = models.CharField(max_length=200)
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
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
        if self.quantity and self.unit:
            return f"{self.quantity} {self.unit} {self.name}"
        elif self.quantity:
            return f"{self.quantity} {self.name}"
        return self.name


class Favorite(models.Model):
    """
    User's favorite recipes.
    """
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
    """
    User ratings for recipes (1-5 stars).
    """
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
    """
    User comments on recipes.
    """
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