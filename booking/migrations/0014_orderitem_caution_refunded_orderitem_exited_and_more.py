# Generated by Django 4.2.7 on 2024-03-09 13:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("booking", "0013_remove_room_stock_availability"),
    ]

    operations = [
        migrations.AddField(
            model_name="orderitem",
            name="caution_refunded",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="orderitem",
            name="exited",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="order",
            name="items",
            field=models.ManyToManyField(related_name="items", to="booking.orderitem"),
        ),
    ]
