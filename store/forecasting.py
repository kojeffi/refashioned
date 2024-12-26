import pandas as pd
from .models import SalesData, DemandForecast, Product

def time_series_analysis(sales_data):
    return sales_data['sales_quantity'].mean()

def forecast_demand():
    products = Product.objects.all()
    for product in products:
        sales_data = SalesData.objects.filter(product=product)
        if sales_data.exists():
            sales_df = pd.DataFrame(list(sales_data.values('sales_date', 'sales_quantity')))
            forecast_quantity = time_series_analysis(sales_df)
            forecast = DemandForecast(
                product=product,
                forecast_date=pd.Timestamp.now().date(),
                forecast_quantity=int(forecast_quantity)
            )
            forecast.save()
