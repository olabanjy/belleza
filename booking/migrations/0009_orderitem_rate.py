# Generated by Django 4.2.7 on 2024-02-25 20:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("booking", "0008_room_stock_availability"),
    ]

    operations = [
        migrations.AddField(
            model_name="orderitem",
            name="rate",
            field=models.IntegerField(default=1),
        ),
    ]
