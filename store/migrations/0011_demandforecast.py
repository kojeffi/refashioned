# Generated by Django 5.0.6 on 2024-06-25 01:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_transaction_user_customer_userbehavior'),
    ]

    operations = [
        migrations.CreateModel(
            name='DemandForecast',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('forecast_date', models.DateField()),
                ('forecast_quantity', models.IntegerField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.product')),
            ],
        ),
    ]
