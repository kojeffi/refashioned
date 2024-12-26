# Generated by Django 5.0.6 on 2024-06-24 03:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_salesdata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salesdata',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.product'),
        ),
    ]