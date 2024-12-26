from django.urls import path
from .views import (analyze_sentiment_view,
                    detect_fraud_view, churn_prediction_view, dynamic_price_update, recommend_products, paypal_cancel,
                    paypal_return, order_success, blog_detail, blog_list, create_blog_post, index, order_detail,
                    leave_review, wishlist_detail,
                    add_to_wishlist, remove_from_wishlist, cart_detail, add_to_cart,
                    update_cart_item, blog_post_detail, faq_list, policy_page_detail,
                    product_list, product_detail, add_product,
                    checkout, order_history, remove_cart_item, security_monitor_view, user_behavior_analysis_view,
                    suggest, chatbot_view, dynamic_landing_page, user_profile, supply_chain_view, set_currency,
                    set_language, notifications_view

                    )
from . import views

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CartViewSet, CartItemViewSet, OrderViewSet, OrderItemViewSet, ReviewViewSet, WishlistViewSet, BlogPostViewSet, FAQViewSet, PolicyPageViewSet, NotificationViewSet, UserProductInteractionViewSet, CustomerViewSet, TransactionViewSet, SalesDataViewSet, UserBehaviorViewSet, DemandForecastViewSet, SearchQueryViewSet, AbandonedCartViewSet, PreferenceViewSet, SecurityLogViewSet, UserInterestViewSet, SocialMediaInteractionViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'carts', CartViewSet)
router.register(r'cart-items', CartItemViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'wishlists', WishlistViewSet)
router.register(r'blog-posts', BlogPostViewSet)
router.register(r'faqs', FAQViewSet)
router.register(r'policy-pages', PolicyPageViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'user-product-interactions', UserProductInteractionViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'sales-data', SalesDataViewSet)
router.register(r'user-behaviors', UserBehaviorViewSet)
router.register(r'demand-forecasts', DemandForecastViewSet)
router.register(r'search-queries', SearchQueryViewSet)
router.register(r'abandoned-carts', AbandonedCartViewSet)
router.register(r'preferences', PreferenceViewSet)
router.register(r'security-logs', SecurityLogViewSet)
router.register(r'user-interests', UserInterestViewSet)
router.register(r'social-media-interactions', SocialMediaInteractionViewSet)

from .views import ProfileListCreateView, ProfileDetailView, MessageListCreateView, MessageDetailView, SubscriptionListCreateView, SubscriptionDetailView



urlpatterns = [
    path('', index, name='home-url'),
    path('product_list/', product_list, name='product_list'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('add_to_compare/<int:product_id>/', views.add_to_compare, name='add_to_compare'),
    path('compare/', views.compare_products, name='compare_products'),
    path('compare/remove/<int:product_id>/', views.remove_from_compare, name='remove_from_compare'),

    path('add-product/', add_product, name='add_product'),
    path('checkout/<int:order_id>/', checkout, name='checkout'),
    path('order/<int:order_id>/', order_detail, name='order_detail'),
    path('order-history/', order_history, name='order_history'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('update-cart-item/<int:cart_item_id>/', update_cart_item, name='update_cart_item'),
    path('remove-cart-item/<int:cart_item_id>/', remove_cart_item, name='remove_cart_item'),  # New URL pattern
    path('cart/', cart_detail, name='cart_detail'),
    path('add_to_wishlist/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/', wishlist_detail, name='wishlist_detail'),
    path('remove_from_wishlist/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('product/<int:product_id>/review/', leave_review, name='leave_review'),
    path('blog/<int:blog_post_id>/', blog_post_detail, name='blog_post_detail'),
    path('faq/', faq_list, name='faq_list'),
    path('policy/<int:policy_page_id>/', policy_page_detail, name='policy_page_detail'),
    path('create_blog_post/', create_blog_post, name='create_blog_post'),
    path('blog/', blog_list, name='blog_list'),
    path('create_blog_post/', create_blog_post, name='create_blog_post'),
    path('blog/<int:blog_post_id>/', blog_detail, name='blog_detail'),
    path('order-success/<int:order_id>/', order_success, name='order_success'),
    path('paypal-return/', paypal_return, name='paypal_return'),
    path('paypal-cancel/', paypal_cancel, name='paypal_cancel'),
    path('recommendations/<int:user_id>/', recommend_products, name='recommend_products'),
    path('dynamic_price_update/<int:product_id>/', dynamic_price_update, name='dynamic_price_update'),
    # path('customer_segmentation/', customer_segmentation_view, name='customer_segmentation'),
    path('churn_prediction/', churn_prediction_view, name='churn_prediction'),
    path('detect_fraud/', detect_fraud_view, name='detect_fraud'),
    path('analyze_sentiment/', analyze_sentiment_view, name='analyze_sentiment'),
    path('forecasts/', views.forecast_list, name='forecast_list'),
    path('trends/', views.trends_view, name='trends'),

    path('recover/<int:user_id>/', views.recover_abandoned_cart, name='recover_abandoned_cart'),

    path('personalized/', views.personalized_view, name='personalized_view'),


    path('send-email/', views.send_personalized_email, name='send_personalized_email'),

    path('recommend-bundles/', views.display_bundle_recommendations, name='recommend_bundles'),

    path('predict-clv/', views.display_clv_prediction, name='predict_clv'),

    path('image-search/', views.image_search, name='image_search'),


    path('security-monitor/', security_monitor_view, name='security_monitor'),

    # path('user-behavior/<int:user_id>/', user_behavior_analysis_view, name='user_behavior_analysis'),

    # path('dynamic-landing-page/<int:user_id>/', views.dynamic_landing_page_view, name='dynamic_landing_page'),

    path('analytics/', views.real_time_analytics, name='real_time_analytics'),

    # path('voice_search/', views.voice_search, name='voice_search'),

    path('search/', views.search_view, name='search'),


    # path('clear-notifications/', views.clear_notifications, name='clear_notifications'),
    path('clear_notification/<int:notification_id>/', views.clear_notification, name='clear_notification'),

    # path('admin/customer-segmentation/', views.admin_customer_segmentation_view, name='admin_customer_segmentation'),

    path('suggest/', suggest, name='suggest'),

    path('chatbot/', chatbot_view, name='chatbot'),

    path('dynamic-landing/', dynamic_landing_page, name='dynamic_landing_page'),


    path('user-profile/', user_profile, name='user_profile'),
    path('supply-chain/', supply_chain_view, name='supply_chain'),


    path('set_currency/<str:currency>/', views.set_currency, name='set_currency'),
    path('set_language/<str:language>/', views.set_language, name='set_language'),


    path('api/', include(router.urls)),

    # Profile API
    path('api/profiles/', ProfileListCreateView.as_view(), name='profile-list-create'),
    path('api/profiles/<int:pk>/', ProfileDetailView.as_view(), name='profile-detail'),

    # Message API
    path('api/messages/', MessageListCreateView.as_view(), name='message-list-create'),
    path('api/messages/<int:pk>/', MessageDetailView.as_view(), name='message-detail'),

    # Subscription API
    path('api/subscriptions/', SubscriptionListCreateView.as_view(), name='subscription-list-create'),
    path('api/subscriptions/<int:pk>/', SubscriptionDetailView.as_view(), name='subscription-detail'),

    path('notifications/', notifications_view, name='notifications'),

    #  mpesa urls
    path('daraja/stk-push', views.stk_push_callback, name='mpesa_stk_push_callback'),
    path('mpesa/', views.mpesa, name='mpesa'),
]