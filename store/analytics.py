import numpy as np
from sklearn.linear_model import LinearRegression
from django.db.models import Sum
from .models import SalesData, SocialMediaInteraction, Product


def predictive_model(sales_data, social_media_data):
    products = list(Product.objects.all())  # Convert QuerySet to list

    X = []
    y = []
    product_ids = []

    for product in products:
        # Aggregate sales data
        sales = sales_data.filter(product=product).aggregate(total_sales=Sum('sales_quantity'))['total_sales'] or 0

        # Aggregate social media interaction data
        social_score = social_media_data.filter(product=product).aggregate(total_score=Sum('interaction_strength'))[
                           'total_score'] or 0

        # Use sales data and social media score as features
        X.append([sales, social_score])
        y.append(product.demand)
        product_ids.append(product.id)  # Collect product IDs

    # Convert lists to numpy arrays
    X = np.array(X)
    y = np.array(y)

    # Train a linear regression model
    model = LinearRegression()
    model.fit(X, y)

    # Predict trends
    predictions = model.predict(X)

    # For simplicity, just return products with highest predicted trends
    trend_indices = np.argsort(predictions)[::-1]  # Sort indices by descending predictions

    # Create a list of products sorted by predicted trends
    trending_products = [products[i] for i in trend_indices if i < len(products)]

    return trending_products
