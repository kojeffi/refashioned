# Generated by Django 5.0.6 on 2024-06-23 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_userproductinteraction'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='competition_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='product',
            name='demand',
            field=models.IntegerField(default=0),
        ),
    ]