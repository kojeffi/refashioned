# custom_admin.py
from django.contrib.admin import AdminSite

class MyAdminSite(AdminSite):
    site_header = "My Custom Admin"
    site_title = "Admin Portal"
    index_title = "Welcome to My Custom Admin"

custom_admin_site = MyAdminSite(name='custom_admin')


# custom_admin.py
from django.contrib import admin
from .models import Product, Cart, CartItem, Order, OrderItem, Review, Wishlist, BlogPost, FAQ, PolicyPage, Notification, UserProductInteraction, Customer, Transaction, SalesData, UserBehavior, DemandForecast, SearchQuery, AbandonedCart, Preference, SecurityLog, UserInterest, SocialMediaInteraction

custom_admin_site.register(Product)
custom_admin_site.register(Cart)
custom_admin_site.register(CartItem)
custom_admin_site.register(Order)
custom_admin_site.register(OrderItem)
custom_admin_site.register(Review)
custom_admin_site.register(Wishlist)
custom_admin_site.register(BlogPost)
custom_admin_site.register(FAQ)
custom_admin_site.register(PolicyPage)
custom_admin_site.register(Notification)
custom_admin_site.register(UserProductInteraction)
custom_admin_site.register(Customer)
custom_admin_site.register(Transaction)
custom_admin_site.register(SalesData)
custom_admin_site.register(UserBehavior)
custom_admin_site.register(DemandForecast)
custom_admin_site.register(SearchQuery)
custom_admin_site.register(AbandonedCart)
custom_admin_site.register(Preference)
custom_admin_site.register(SecurityLog)
custom_admin_site.register(UserInterest)
custom_admin_site.register(SocialMediaInteraction)
