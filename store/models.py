from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    stock = models.IntegerField()
    image = CloudinaryField('image', blank=True, null=True)
    category = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    demand = models.IntegerField(default=0)
    competition_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    social_media_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # New field
    supply_chain_forecast = models.TextField(blank=True, null=True)


    @property
    def final_price(self):
        final_price = self.price - (self.price * self.discount / 100)
        return round(final_price, 2)

    def __str__(self):
        return self.name

    @classmethod
    def search_by_name(cls, query):
        return cls.objects.filter(name__icontains=query)


class SupplyChainForecast(models.Model):
    forecast_date = models.DateField()
    forecast_data = models.TextField()

    def __str__(self):
        return f"Forecast for {self.forecast_date}"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        return self.quantity * self.product.final_price

class Order(models.Model):
    PAYMENT_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='credit_card')

    def calculate_total_price(self):
        total = sum(item.total_price for item in self.orderitem_set.all())
        return total

    def apply_discount(self, discount_amount):
        self.total_price -= discount_amount
        self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    @property
    def total_price(self):
        return self.quantity * self.product.final_price

    def __str__(self):
        return self.product.name
    from django.contrib.auth.models import User

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
except ModuleNotFoundError:
    SentimentIntensityAnalyzer = None  # or handle this case as needed

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    review_text = models.TextField()
    sentiment = models.CharField(max_length=20, blank=True, null=True)

    def save(self, *args, **kwargs):
        if SentimentIntensityAnalyzer:
            analyzer = SentimentIntensityAnalyzer()
            sentiment_score = analyzer.polarity_scores(self.review_text)
            compound = sentiment_score['compound']
            self.sentiment = 'positive' if compound > 0.05 else 'negative' if compound < -0.05 else 'neutral'
        else:
            # Handle the case where SentimentIntensityAnalyzer could not be imported
            self.sentiment = 'unknown'

        super().save(*args, **kwargs)


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ManyToManyField(Product)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Wishlist"

class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()

class PolicyPage(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()

# notification system
# models.py

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    message = models.TextField()

    def __str__(self):
        return self.message


class UserProductInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)  # Rating or interaction score

    class Meta:
        unique_together = ('user', 'product')


from django.db import models

from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    quantity = models.IntegerField()
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='transactions')

    def __str__(self):
        return f"Transaction {self.id}: {self.description} - ${self.amount}"


from django.db import models

class SalesData(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    sales_date = models.DateField()
    sales_quantity = models.IntegerField()

    def __str__(self):
        return f"{self.product} - {self.sales_date}"


from django.db import models
from django.contrib.auth.models import User

class UserBehavior(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.CharField(max_length=255)
    clicks = models.IntegerField(default=0)
    time_spent = models.FloatField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.query} ({self.clicks} clicks, {self.time_spent} sec)"



class DemandForecast(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    forecast_date = models.DateField()
    forecast_quantity = models.IntegerField()

    def __str__(self):
        return f"{self.product.name} - {self.forecast_date}: {self.forecast_quantity}"


class SearchQuery(models.Model):
    query = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.query


from django.db import models
from django.contrib.auth.models import User
from .models import Product, Cart

class AbandonedCart(models.Model):
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    abandoned_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Abandoned Cart for {self.cart.user.username}"

class Preference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_subscription = models.BooleanField(default=True)
    preferred_category = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Preferences for {self.user.username}"




import spacy

nlp = spacy.load('en_core_web_sm')

def understand_query(query):
    doc = nlp(query)
    keywords = [token.text for token in doc if token.is_alpha and not token.is_stop]
    return keywords


from django.db import models
from django.contrib.auth.models import User

class SecurityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    event_type = models.CharField(max_length=255)
    event_description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_type} - {self.timestamp}"


class UserInterest(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    interests = models.JSONField(default=list)

    def __str__(self):
        return f'{self.user.username} - Interests: {self.interests}'





# models.py

from django.db import models
from django.contrib.auth.models import User
from .models import Product

class SocialMediaInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    platform = models.CharField(max_length=50)
    interaction_type = models.CharField(max_length=50)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    interaction_strength = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.interaction_type} - {self.product.name}"


def analyze_social_media(user_id):
    from collections import defaultdict

    social_data = SocialMediaInteraction.objects.filter(user_id=user_id)

    product_scores = defaultdict(float)

    for interaction in social_data:
        product_scores[interaction.product_id] += interaction.interaction_strength

    for product_id, score in product_scores.items():
        product = Product.objects.get(id=product_id)
        product.social_media_score = score
        product.save()

    recommendations = Product.objects.filter(social_media_score__gt=0).order_by('-social_media_score')[:5]

    return recommendations


def optimize_supply_chain():

    def predictive_model(supply_chain_data):

        return f"Forecasted supply chain data based on analytics"

    supply_chain_data = SalesData.objects.all()

    supply_chain_forecast = predictive_model(supply_chain_data)

    products = Product.objects.all()
    for product in products:
        product.supply_chain_forecast = supply_chain_forecast
        product.save()

    return supply_chain_forecast




