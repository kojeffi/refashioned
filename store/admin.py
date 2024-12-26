from django.contrib import admin
from .models import Product, Cart, CartItem, Order, OrderItem, Review, Wishlist, BlogPost, FAQ, PolicyPage, Notification

from .models import Product, UserProductInteraction, Transaction, SalesData, Customer, UserBehavior, UserInterest, SocialMediaInteraction
from .views import predict_churn


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'category', 'created_at']

admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Review)
admin.site.register(Wishlist)
admin.site.register(BlogPost)
admin.site.register(FAQ)
admin.site.register(PolicyPage) 
admin.site.register(Notification)
# admin.site.register(Transaction)
admin.site.register(UserProductInteraction)
admin.site.register(SalesData)
admin.site.register(Customer)

from .models import DemandForecast, Product, SalesData

# class DemandForecastAdmin(admin.ModelAdmin):
#     list_display = ('product', 'forecast_date', 'forecast_quantity')

admin.site.register(DemandForecast)

admin.site.register(UserBehavior)

admin.site.register(UserInterest)

admin.site.register(SocialMediaInteraction)


from .models import SupplyChainForecast

class SupplyChainForecastAdmin(admin.ModelAdmin):
    list_display = ('forecast_date', 'forecast_data')
    search_fields = ('forecast_date', 'forecast_data')
    list_filter = ('forecast_date',)
    ordering = ('-forecast_date',)

admin.site.register(SupplyChainForecast, SupplyChainForecastAdmin)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'amount', 'timestamp', 'total_price')
    search_fields = ('user__username', 'product__name', 'description')
    list_filter = ('user', 'product')
