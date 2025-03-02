from django.db import models
from base.models import BaseModel
from django.utils.text import slugify
from django.utils.html import mark_safe
from django.conf import settings  # ✅ Ensure AUTH_USER_MODEL is used dynamically

# Create your models here.

class Category(BaseModel):
    category_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
    category_image = models.ImageField(upload_to="categories")  # ✅ Fixed folder name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.category_name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.category_name


class ColorVariant(BaseModel):
    color_name = models.CharField(max_length=100)
    price = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.color_name


class SizeVariant(BaseModel):
    size_name = models.CharField(max_length=100)
    price = models.IntegerField(default=0)
    order = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.size_name


class Product(BaseModel):
    parent = models.ForeignKey(
        'self', related_name='variants', on_delete=models.CASCADE, blank=True, null=True)
    product_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    price = models.IntegerField()
    product_description = models.TextField()
    color_variant = models.ManyToManyField(ColorVariant, blank=True)
    size_variant = models.ManyToManyField(SizeVariant, blank=True)
    newest_product = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.product_name)
        super(Product, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.product_name

    def get_product_price_by_size(self, size):
        try:
            size_variant = SizeVariant.objects.get(size_name=size)
            return self.price + size_variant.price
        except SizeVariant.DoesNotExist:
            return self.price

    def get_rating(self):
        from django.db.models import Avg
        rating = self.reviews.aggregate(avg_rating=Avg('stars'))["avg_rating"]
        return rating if rating else 0


class ProductImage(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images')
    image = models.ImageField(upload_to='product')

    def img_preview(self):
        return mark_safe(f'<img src="{self.image.url}" width="500"/>')


class Coupon(BaseModel):
    coupon_code = models.CharField(max_length=10)
    is_expired = models.BooleanField(default=False)
    discount_amount = models.IntegerField(default=100)
    minimum_amount = models.IntegerField(default=500)


class ProductReview(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # ✅ Changed User to AUTH_USER_MODEL
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="liked_reviews", blank=True)
    dislikes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="disliked_reviews", blank=True)
    stars = models.IntegerField(default=3, choices=[(i, i) for i in range(1, 6)])
    content = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def like_count(self):
        return self.likes.count()

    def dislike_count(self):
        return self.dislikes.count()


class Wishlist(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist")  # ✅ Changed User to AUTH_USER_MODEL
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlisted_by")
    size_variant = models.ForeignKey(SizeVariant, on_delete=models.SET_NULL, null=True, blank=True, related_name="wishlist_items")
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product', 'size_variant')

    def __str__(self) -> str:
        return f'{self.user.email} - {self.product.product_name} - {self.size_variant.size_name if self.size_variant else "No Size"}'
