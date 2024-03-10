import string

from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

from core.mail import send_email

from . import choices
from .models import Order, OrderItem

from celery import shared_task

from datetime import datetime, timedelta


@shared_task
def auto_booking_reminder():
    datetime_now = datetime.astimezone(datetime.now())
    date_today = datetime_now.date()

    all_order_items = OrderItem.objects.filter(ordered=True)
    for item in all_order_items:
        day_before = item.check_in - timedelta(days=1)
        if date_today == day_before.date():
            # send a mail
            send_reminder_email.delay(item.id)

    print("all remiders sent for", date_today)


@shared_task
def auto_checkout():
    datetime_now = datetime.astimezone(datetime.now())

    all_order_items = OrderItem.objects.filter(
        ordered=True, check_out__lte=datetime_now
    )
    for item in all_order_items:
        print(item)
        # checkout item i.e set ordered to False and checked_out, caution_refunded
        item.caution_refunded = True
        item.ordered = False
        item.exited = True

        # send checkout message .delay

        item.save()
        send_check_out_email.delay(item.id)

    print("all checkout emails sent for", datetime_now)


@shared_task
def send_check_out_email(item_id):
    try:
        the_item = OrderItem.objects.get(id=item_id)
        the_order = Order.objects.filter(items__id=the_item.id).first()
        send_email(
            [the_item.user.user.email],
            "Thank you for choosing Belleza",
            html_path="emails/check_out.html",
            context={
                "fullName": (
                    f"{the_order.booking_info.full_name}"
                    if the_item.item_type == choices.ProductType.Room.value
                    else f"{the_order.booking_info.corporate_rep}"
                )
            },
        )
    except Exception as ex:
        print(ex)
        pass


@shared_task
def send_reminder_email(item_id):
    try:
        the_item = OrderItem.objects.get(id=item_id)
        the_order = Order.objects.filter(items__id=the_item.id).first()

        send_email(
            [the_item.user.user.email],
            "Thank you for choosing Belleza",
            html_path="emails/reminder.html",
            context={
                "fullName": (
                    f"{the_order.booking_info.full_name}"
                    if the_item.item_type == choices.ProductType.Room.value
                    else f"{the_order.booking_info.corporate_rep}"
                ),
                "check_in": the_item.check_in,
                "check_out": the_item.check_out,
            },
        )

    except Exception as ex:
        print(ex)
        pass


@shared_task
def send_booking_email(order_id, item_id):
    try:
        the_item = OrderItem.objects.get(id=item_id)
        the_order = Order.objects.get(id=order_id)

        send_email(
            [the_order.user.user.email],
            "Your Reservation at Belleza",
            html_path="emails/reservation.html",
            context={
                "item": the_item,
                "fullName": (
                    f"{the_order.booking_info.full_name}"
                    if the_item.item_type == choices.ProductType.Room.value
                    else f"{the_order.booking_info.corporate_rep}"
                ),
                "check_in": the_item.check_in,
                "check_out": the_item.check_out,
                "amount": the_item.get_final_price(),
            },
        )
    except Exception as ex:
        print(ex)
        raise


@shared_task
def send_admin_booking_email(order_id, item_id):
    try:
        the_item = OrderItem.objects.get(id=item_id)
        the_order = Order.objects.get(id=order_id)

        send_email(
            ["bookings@bellezabeachresort.com"],
            f"New {the_item.item_type} Reservation",
            html_path="emails/notify_admin_on_booking.html",
            context={
                "type": the_item.item_type,
                "item": the_item,
                "email": the_order.user.user.email,
                "phone": the_order.booking_info.phone,
                "other_phone": the_order.booking_info.other_phone,
                "fullName": (
                    f"{the_order.booking_info.full_name}"
                    if the_item.item_type == choices.ProductType.Room.value
                    else f"{the_order.booking_info.corporate_rep}"
                ),
                "check_in": the_item.check_in,
                "check_out": the_item.check_out,
                "amount": the_item.get_final_price(),
            },
        )

    except Exception as ex:
        print(ex)
        raise
