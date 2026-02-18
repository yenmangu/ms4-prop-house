from django.db import models
from django.utils.text import slugify

# Create your models here.


class CategoryProductJoin(models.Model):
    """Join table provides many-to-many relationship between Product and Category"""

    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    category = models.ForeignKey("Category", on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "category"],
                name="unique_product_category",
            )
        ]

    def __str__(self):
        return f"{self.product} <-> {self.category}"


class Category(models.Model):
    """
    Stores a single Category entity

    """

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.build_unique_slug()
        return super().save(*args, **kwargs)

    def build_unique_slug(self) -> str:
        base_slug = slugify(self.name) or "product"
        candidate_slug = base_slug
        suffix = 2

        while (
            self.__class__.objects.filter(slug=candidate_slug)
            .exclude(pk=self.pk)
            .exists()
        ):
            candidate_slug = f"{base_slug}-{suffix}"
            suffix += 1
        return candidate_slug


class Product(models.Model):
    """
    Stores a single Product entity

    Note: slug has 'blank=true' set, but will be enforced in view logic
    """

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    categories = models.ManyToManyField(
        Category,
        related_name="products",
        through=CategoryProductJoin,
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_eligible = models.BooleanField(default=False)
    stock_quantity = models.PositiveIntegerField(default=0)
    featured_image = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.build_unique_slug()
        return super().save(*args, **kwargs)

    def build_unique_slug(self) -> str:
        base_slug = slugify(self.name) or "product"
        candidate_slug = base_slug
        suffix = 2

        while (
            self.__class__.objects.filter(slug=candidate_slug)
            .exclude(pk=self.pk)
            .exists()
        ):
            candidate_slug = f"{base_slug}-{suffix}"
            suffix += 1
        return candidate_slug
