from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import numpy as np

def segment_customers(customer_data):
    X = np.array([[customer['age'], customer['income'], customer['spending_score']] for customer in customer_data])

    
    kmeans = KMeans(n_clusters=3, random_state=42)
    segments = kmeans.fit_predict(X)

    return segments.tolist()

def predict_churn(customer_features, churn_target):
    
    X = np.array([[customer['age'], customer['income'], customer['spending_score']] for customer in customer_features])
    y = np.array(churn_target)

    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

   
    model = LogisticRegression(random_state=42)

   
    model.fit(X_train, y_train)

  
    churn_probabilities = model.predict_proba(X_test)[:, 1]

    return churn_probabilities.tolist()  # Convert numpy array to list for JSON serialization


# utils.py

import numpy as np
from .models import UserBehavior


def behavior_model(user_behavior_data):
    if not user_behavior_data:
        return {'average_clicks': 0, 'average_time_spent': 0}

    clicks = [behavior.clicks for behavior in user_behavior_data]
    time_spent = [behavior.time_spent for behavior in user_behavior_data]

    average_clicks = np.mean(clicks)
    average_time_spent = np.mean(time_spent)

    return {
        'average_clicks': average_clicks,
        'average_time_spent': average_time_spent
    }


def analyze_behavior(user_id):
    user_behavior_data = UserBehavior.objects.filter(user_id=user_id)
    behavior_patterns = behavior_model(user_behavior_data)
    # Example behavior patterns generation
    behavior_descriptions = [
        f"Logged in {np.random.randint(1, 10)} times",
        f"Purchased {np.random.randint(1, 5)} items",
        f"Browsed {np.random.randint(5, 20)} pages"
    ]
    return behavior_descriptions


# utils.py

from .models import UserInterest

def get_user_interests(user_id):
    interests = UserInterest.objects.filter(user_id=user_id).values_list('interest', flat=True)
    return list(interests)

def generate_landing_page(interests):
    content = (f"<h1>Welcome!</h1><p>Based on your interests in {', '.join(interests)}, "
               f"we recommend the following:</p>")
    # Add more logic to generate content dynamically based on interests
    return content

def create_dynamic_page(user_id):
    interests = get_user_interests(user_id)
    landing_page = generate_landing_page(interests)
    return landing_page


# utils.py
def process_query(query):
    # Example processing logic (replace with your actual processing logic)
    processed_query = query.lower()  # Convert query to lowercase
    return processed_query

from .models import Transaction
import pandas as pd
import joblib

# Load the pre-trained CLV model
clv_model = joblib.load('store/clv_model.pkl')

def predict_clv(customer_data):
    # Ensure the features are floats
    features = [float(customer_data['total_spent']), float(customer_data['total_quantity']),
                float(customer_data['days_since_last_purchase'])]

    # Predict CLV
    clv = clv_model.predict([features])

    return clv[0]  # Return the predicted CLV va




from .models import Transaction
import pandas as pd

def get_customer_data(customer_id):
    transactions = Transaction.objects.filter(user_id=customer_id).values('quantity', 'amount', 'timestamp')

    if not transactions:
        print(f"No transactions found for customer_id: {customer_id}")
        return None

    # Convert transactions to DataFrame
    df = pd.DataFrame(list(transactions))
    print(f"Transactions DataFrame:\n{df}")

    if df.empty:
        print("DataFrame is empty")
        return None

    df['total_price'] = df['quantity'] * df['amount']

    # Compute features
    total_spent = df['total_price'].sum()
    total_quantity = df['quantity'].sum()
    days_since_last_purchase = (pd.Timestamp.now() - pd.to_datetime(df['timestamp']).max().replace(tzinfo=None)).days

    return {
        'total_spent': float(total_spent),
        'total_quantity': float(total_quantity),
        'days_since_last_purchase': float(days_since_last_purchase),
    }


from datetime import datetime, timedelta
from django.db.models import Count, Min, Max
from .models import Transaction


def get_user_behavior(user_id):
    try:
        # Fetch transactions for the user
        transactions = Transaction.objects.filter(user_id=user_id)

        # Calculate recent activity window (e.g., last 6 months)
        recent_window = datetime.now() - timedelta(days=180)

        # Filter transactions within the recent window
        recent_transactions = transactions.filter(timestamp__gte=recent_window)

        # Get frequent categories
        frequent_categories = recent_transactions.values_list('product__category', flat=True).annotate(
            count=Count('product__category')).order_by('-count')[:3]

        # Get preferred price range
        preferred_price_range = (
            recent_transactions.aggregate(min_price=Min('amount'))['min_price'] or 0,
            recent_transactions.aggregate(max_price=Max('amount'))['max_price'] or 1000
        )

        # Return user behavior data
        user_behavior = {
            'frequent_categories': frequent_categories,
            'preferred_price_range': preferred_price_range,
        }
    except Exception as e:
        print(f"Error fetching user behavior: {e}")
        user_behavior = {}

    return user_behavior


from .models import Product

from .models import Product


def adaptive_ranking(query, user_id):
    user_behavior = get_user_behavior(user_id)
    search_results = Product.objects.filter(name__icontains=query).values('id', 'name', 'category', 'price')

    # Convert search results to list of dictionaries
    search_results_list = list(search_results)

    # Rank search results based on user behavior
    ranked_results = rank_search_results(search_results_list, user_behavior)

    return ranked_results


def get_user_behavior(user_id):
    # Implement logic to fetch and analyze user behavior
    # Example: frequent categories, preferred price range
    user_behavior = {}
    return user_behavior


def rank_search_results(search_results, user_behavior):
    def calculate_rank_score(product):
        score = 0

        # Boost score for products in frequent categories
        if product['category'] in user_behavior.get('frequent_categories', []):
            score += 10

        # Boost score for products within preferred price range
        min_price, max_price = user_behavior.get('preferred_price_range', (0, 1000))
        if min_price <= product['price'] <= max_price:
            score += 5

        return score

    # Rank results by score
    search_results.sort(key=lambda product: calculate_rank_score(product), reverse=True)

    return search_results


# utils.py

from collections import defaultdict
from .models import Product, SocialMediaInteraction, SalesData


def analyze_social_media(user_id):
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
        # Placeholder for actual predictive modeling logic
        return "Forecasted supply chain data based on analytics"

    supply_chain_data = SalesData.objects.all()

    supply_chain_forecast = predictive_model(supply_chain_data)

    products = Product.objects.all()
    for product in products:
        product.supply_chain_forecast = supply_chain_forecast
        product.save()

    return supply_chain_forecast


# utils.py

from collections import defaultdict
from .models import Product, SalesData
from datetime import datetime, timedelta


def optimize_supply_chain():
    def predictive_model(supply_chain_data):
        # Initialize data structures
        product_sales = defaultdict(list)
        product_forecast = {}

        # Collect sales data and compute averages
        for data in supply_chain_data:
            product_sales[data.product_id].append(data.sales_quantity)

        # Calculate average sales for each product
        for product_id, quantities in product_sales.items():
            average_quantity = sum(quantities) / len(quantities)

            # Example forecasting logic
            # Assuming we want to forecast sales for the next 30 days
            forecast_quantity = average_quantity * 30

            product_forecast[product_id] = forecast_quantity

        return product_forecast

    # Fetch all sales data
    supply_chain_data = SalesData.objects.filter(sales_date__gte=datetime.now() - timedelta(days=365))
    supply_chain_forecast = predictive_model(supply_chain_data)

    # Save forecasts to products
    products = Product.objects.all()
    for product in products:
        forecast_quantity = supply_chain_forecast.get(product.id, "No forecast data available")
        product.supply_chain_forecast = f"Forecasted quantity for next 30 days: {forecast_quantity}" if isinstance(
            forecast_quantity, (int, float)) else forecast_quantity
        product.save()

    return supply_chain_forecast


# views.py

from django.shortcuts import render
from .utils import optimize_supply_chain


def supply_chain_view(request):
    forecast = optimize_supply_chain()  # Optimize supply chain

    # Prepare data for display
    formatted_forecast = {Product.objects.get(id=pid): quantity for pid, quantity in forecast.items()}

    context = {
        'forecast': formatted_forecast
    }
    return render(request, 'store/supply_chain.html', context)



# myapp/utils.py

from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_recovery_email(abandoned_cart):
    try:
        # Fetch the email and cart items
        user_email = abandoned_cart.cart.user.email
        cart_items = abandoned_cart.cart.cartitem_set.all()

        # Construct the email content
        subject = 'Recover Your Abandoned Cart'
        message = f'Hello {abandoned_cart.cart.user.username},\n\n'
        message += 'You have abandoned the following items in your cart:\n'
        for item in cart_items:
            message += f'- {item.product.name}, Quantity: {item.quantity}\n'
        message += '\nPlease visit our website to complete your purchase.\n\n'
        message += 'Thank you!\nYour Store Team'

        # Send the email
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user_email])
        logger.info(f'Recovery email sent to {user_email}')
    except AttributeError as e:
        logger.error(f'Attribute error: {e}')
    except Exception as e:
        logger.error(f'An error occurred: {e}')


# utils.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


def send_recovery_email(abandoned_cart):
    # Example email context
    context = {
        'user': abandoned_cart.cart.user,
        'cart': abandoned_cart.cart,
    }
    subject = 'Recover Your Abandoned Cart'
    message = render_to_string('store/recover_cart_email.html', context)
    recipient_list = [abandoned_cart.cart.user.email]

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)


