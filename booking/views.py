from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.views.defaults import page_not_found
from django.views.generic import View
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from .utils import (
    cookieCart,
    cartData,
    guestOrder,
    handle_complimentary_booking,
    wee_day,
)
from . import choices
from ums.models import Profile
import requests
from django.contrib.auth.models import User

from django.conf import settings
from django.contrib import messages

from django.template.loader import render_to_string

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from django.utils.safestring import mark_safe


import json, random, string
from django.http import JsonResponse

import hmac
import hashlib


from .models import (
    CustomContentBaseTypeModel,
    Room,
    Package,
    Gallery,
    PackageComplimentary,
    OrderItem,
    Order,
    Payment,
    AppLogs,
    WebhookBackup,
)


def create_ref_code():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=20))


def return_json_response(obj):
    print("obj", obj)
    return JsonResponse(
        data=obj,
    )


def all_rooms(request):
    template = "booking/all_rooms.html"

    all_rooms = Room.objects.filter(is_active=True).all().order_by("position")

    context = {"all_rooms": all_rooms, "page_title": "Our Rooms"}

    return render(request, template, context)


def room_details(request, room_id):
    template = "booking/room_details.html"

    the_room = get_object_or_404(Room, id=room_id)

    similar_rooms = Room.objects.exclude(id__in=[the_room.id])[:3]

    context = {
        "the_room": the_room,
        "availability_count": range(1, the_room.availability + 1),
        "similar_rooms": similar_rooms,
        "page_title": f"{the_room.title}",
    }
    return render(request, template, context)


def all_packages(request):
    template = "booking/all_packages.html"

    all_packages = Package.objects.filter(is_active=True).all().order_by("position")

    context = {"all_packages": all_packages, "page_title": "Our Packages"}

    return render(request, template, context)


def package_details(request, package_id):
    template = "booking/package_details.html"

    the_package = get_object_or_404(Package, id=package_id)

    similar_packages = Package.objects.exclude(id__in=[the_package.id])

    context = {
        "the_package": the_package,
        "similar_packages": similar_packages,
        "page_title": f"{the_package.title}",
    }
    return render(request, template, context)


@require_POST
@csrf_exempt
def render_available_room_count(request):
    data = json.loads(request.body)
    productId = data["productId"]

    the_room = Room.objects.get(id=productId)

    return JsonResponse({"available": the_room.availability})


@require_POST
@csrf_exempt
def check_availabilty(request):
    data = json.loads(request.body)

    cart_data = cartData(request)

    json_resp = {}

    productId = data["productId"]
    productType = data["productType"]
    bookedDates = data["bookedDates"]
    quantity = data["quantity"]

    check_in_date, check_out_date = bookedDates.split("-")

    if productType == "room":
        check_in_datetime, check_out_datetime = datetime.strptime(
            f"{check_in_date.strip()} 12:00:00", "%d/%m/%Y %H:%M:%S"
        ), datetime.strptime(f"{check_out_date.strip()} 10:00:00", "%d/%m/%Y %H:%M:%S")
        # fetch room
        the_room = Room.objects.get(id=productId)
        product_type = ContentType.objects.get_for_model(Room)

        # check if room is already in cart
        items = cart_data["items"]
        room_in_cart = False
        room_bookings = [d for d in items if d["type"] == "room"]
        print("room bookings", room_bookings)
        if len(room_bookings) > 0:
            for r in room_bookings:
                if (
                    the_room.title in r["item"]["name"]
                    and r["item"]["check_in"] >= check_in_datetime
                    and r["item"]["check_out"] <= check_out_datetime
                ):
                    room_in_cart = True
                    break

        if room_in_cart:
            return JsonResponse(
                data={
                    "is_available": False,
                    "message": f"{the_room.title} has been fully booked between {check_in_date} and {check_out_date}. Kindly book another room",
                    "room_name": the_room.title,
                    "check_in": check_in_date,
                    "check_out": check_out_date,
                },
            )

        # check availabilty in order_item
        order_items_qs = OrderItem.objects.filter(
            content_type=product_type,
            object_id=the_room.id,
            item_type=choices.ProductType.Room.value,
            ordered=True,
            check_in__gte=datetime.strptime(
                f"{check_in_date.strip()} 12:00:00", "%d/%m/%Y %H:%M:%S"
            ),
            check_out__lte=datetime.strptime(
                f"{check_out_date.strip()} 10:00:00", "%d/%m/%Y %H:%M:%S"
            ),
        )
        sum_agrregate = order_items_qs.aggregate(Sum("quantity"))

        if order_items_qs.exists():
            # subtract quantity booked from availabilty
            if the_room.availability <= sum_agrregate["quantity__sum"]:
                print(
                    "there is a problem here, ordered room should never be more than availabilty"
                )
                raise Exception("An error occured!")
            available_rooms = the_room.availability - sum_agrregate["quantity__sum"]
            if available_rooms >= quantity:
                json_resp.update(
                    {
                        "is_available": True,
                        "message": f"{the_room.title} is available between {check_in_date} and {check_out_date}",
                        "room_name": the_room.title,
                        "check_in": check_in_date,
                        "check_out": check_out_date,
                    }
                )
            else:
                json_resp.update(
                    {
                        "is_available": False,
                        "message": f"{the_room.title} has been fully booked between {check_in_date} and {check_out_date}. Kindly book another room",
                        "room_name": the_room.title,
                        "check_in": check_in_date,
                        "check_out": check_out_date,
                    }
                )
        else:
            if the_room.availability >= quantity:
                json_resp.update(
                    {
                        "is_available": True,
                        "message": f"{the_room.title} is available between {check_in_date} and {check_out_date}",
                        "room_name": the_room.title,
                        "check_in": check_in_date,
                        "check_out": check_out_date,
                    }
                )
            else:
                json_resp.update(
                    {
                        "is_available": False,
                        "message": f"{the_room.title} has been fully booked between {check_in_date} and {check_out_date}. Kindly book another room",
                        "room_name": the_room.title,
                        "check_in": check_in_date,
                        "check_out": check_out_date,
                    }
                )

    elif productType == "package":

        the_package = Package.objects.get(id=productId)
        product_type = ContentType.objects.get_for_model(Package)

        period = data["period"]
        if period == "day":

            product_check_in = datetime.strptime(
                f"{check_in_date.strip()} 12:00:00", "%d/%m/%Y %H:%M:%S"
            )
            product_check_out = datetime.strptime(
                f"{check_out_date.strip()} 19:00:00", "%d/%m/%Y %H:%M:%S"
            )
        elif period == "night":

            product_check_in = datetime.strptime(
                f"{check_in_date.strip()} 12:00:00", "%d/%m/%Y %H:%M:%S"
            )
            product_check_out = datetime.strptime(
                f"{check_out_date.strip()} 10:00:00", "%d/%m/%Y %H:%M:%S"
            )

        # check availabilty in order_item
        any_order_items_qs = OrderItem.objects.filter(
            ordered=True,
            check_in__gte=product_check_in,
            check_out__lte=product_check_out,
        )

        items = cart_data["items"]

        package_in_cart = False
        package_bookings = [d for d in items if d["type"] == "package"]

        if len(package_bookings) > 0:

            for p in package_bookings:

                if product_check_in >= p["item"]["check_in"] and product_check_out <= p[
                    "item"
                ]["check_out"] + timedelta(days=30):
                    package_in_cart = True
                    break

        if package_in_cart:
            return JsonResponse(
                data={
                    "is_available": False,
                    "message": f"{the_package.title} has been fully booked between {check_in_date} and {check_out_date}. Kindly book another room",
                    "package_name": the_package.title,
                    "check_in": check_in_date,
                    "check_out": check_out_date,
                },
            )

        if the_package.slug == "gold":
            # check cookie cart
            room_bookings = [d for d in items if d["type"] == "room"]
            room_booking_count = len(room_bookings)
            if room_booking_count > 0:
                return JsonResponse(
                    data={
                        "is_available": False,
                        "message": f"{the_package.title} is full booked between {check_in_date} and {check_out_date}. Kindly book another package",
                        "package_name": the_package.title,
                        "check_in": check_in_date,
                        "check_out": check_out_date,
                    }
                )

            # if gold, check if there is booked room or package for that period
            if any_order_items_qs.exists():
                json_resp.update(
                    {
                        "is_available": False,
                        "message": f"{the_package.title} is full booked between {check_in_date} and {check_out_date}. Kindly book another package",
                        "package_name": the_package.title,
                        "check_in": check_in_date,
                        "check_out": check_out_date,
                    }
                )

            else:
                json_resp.update(
                    {
                        "is_available": True,
                        "message": f"{the_package.title} is available between {check_in_date} and {check_out_date}",
                        "package_name": the_package.title,
                        "check_in": check_in_date,
                        "check_out": check_out_date,
                    }
                )

        elif the_package.slug == "bronze":
            # if bronze, check if there is any available full poolview rooms
            # fetch poolview
            flplv = Room.objects.filter(slug="full-poolview")

            if not flplv.exists():
                return
            # fetch full poolview orders
            product_type = ContentType.objects.get_for_model(Room)
            flplv_ordered = any_order_items_qs.filter(
                content_type=product_type,
                object_id=flplv.first().id,
                item_type=choices.ProductType.Room.value,
            )
            if not flplv_ordered.exists():
                json_resp.update(
                    {
                        "is_available": True,
                        "message": f"{the_package.title} is available between {check_in_date} and {check_out_date}",
                        "package_name": the_package.title,
                        "check_in": check_in_date,
                        "check_out": check_out_date,
                    }
                )
            else:
                sum_agrregate = order_items_qs.aggregate(Sum("quantity"))
                quantity_remaining = (
                    flplv.first().availability - sum_agrregate["quantity__sum"]
                )
                if quantity_remaining >= 2:
                    json_resp.update(
                        {
                            "is_available": True,
                            "message": f"{the_package.title} is available between {check_in_date} and {check_out_date}",
                            "package_name": the_package.title,
                            "check_in": check_in_date,
                            "check_out": check_out_date,
                        }
                    )
                else:
                    json_resp.update(
                        {
                            "is_available": False,
                            "message": f"{the_package.title} is full booked between {check_in_date} and {check_out_date}. Kindly book another package",
                            "package_name": the_package.title,
                            "check_in": check_in_date,
                            "check_out": check_out_date,
                        }
                    )

        elif the_package.slug == "silver":
            # fetch anyroom order items
            any_room_order_item = any_order_items_qs.filter(
                item_type=choices.ProductType.Room.value,
            )
            if not any_room_order_item.exists():
                json_resp.update(
                    {
                        "is_available": True,
                        "message": f"{the_package.title} is available between {check_in_date} and {check_out_date}",
                        "package_name": the_package.title,
                        "check_in": check_in_date,
                        "check_out": check_out_date,
                    }
                )
            else:
                sum_agrregate = any_room_order_item.aggregate(Sum("quantity"))
                print("booked rooms count", sum_agrregate)

                all_rooms_sum = Room.objects.aggregate(Sum("availability"))
                all_room_sum_aggregate = all_rooms_sum["availability__sum"]
                print("all rooms count", all_room_sum_aggregate)

                quantity_remaining = (
                    all_room_sum_aggregate - sum_agrregate["quantity__sum"]
                )
                if quantity_remaining >= 10:
                    json_resp.update(
                        {
                            "is_available": True,
                            "message": f"{the_package.title} is available between {check_in_date} and {check_out_date}",
                            "package_name": the_package.title,
                            "check_in": check_in_date,
                            "check_out": check_out_date,
                        }
                    )
                else:
                    json_resp.update(
                        {
                            "is_available": False,
                            "message": f"{the_package.title} is full booked between {check_in_date} and {check_out_date}. Kindly book another package",
                            "package_name": the_package.title,
                            "check_in": check_in_date,
                            "check_out": check_out_date,
                        }
                    )

    return JsonResponse(
        data=json_resp,
    )


def cart(request):
    data = cartData(request)

    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]
    room_bookings = [d for d in items if d["type"] == "room"]
    room_booking_count = len(room_bookings)

    package_bookings = [d for d in items if d["type"] == "package"]
    package_booking_count = len(package_bookings)

    # print("items", items)
    print("room", room_bookings)
    print("pckge", package_bookings)

    template = "booking/cart.html"

    context = {
        "items": items,
        "order": order,
        "room_bookings": room_bookings,
        "package_bookings": package_bookings,
        "cartItems": cartItems,
        "room_booking_count": room_booking_count,
        "package_booking_count": package_booking_count,
    }
    return render(request, template, context)


def checkout(request):

    template = "booking/checkout.html"

    data = cartData(request)

    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]

    print(order)

    if cartItems < 1:
        print("You don not have any item in the cart")
        return redirect("core:home")

    context = {
        "items": items,
        "order": order,
    }
    return render(request, template, context)


@require_POST
@csrf_exempt
def process_checkout(request):
    from django.contrib.humanize.templatetags.humanize import intcomma

    data = json.loads(request.body)

    the_profile, order = guestOrder(request, data)

    orderInfo = {
        "order_id": str(order.id)[:12],
        "ref_code": order.ref_code,
        "ordered_date": order.ordered_date.strftime("%m/%d/%Y"),
        "ordered": order.ordered,
        "order_total": intcomma(int(order.get_total())),
    }

    bookingInfo = {
        "email": order.user.user.email,
        "phone": order.booking_info.phone,
        "other_phone": order.booking_info.other_phone,
        "full_name": order.booking_info.full_name,
        "company_name": order.booking_info.company_name,
        "address": order.booking_info.address,
        "corporate_rep": order.booking_info.corporate_rep,
        "nature_of_business": order.booking_info.nature_of_business,
    }

    order_items = []
    for item in order.items.all():
        extra_guests_cost = 0
        if item.extra_guest and item.item_type == choices.ProductType.Package.value:
            extra_guests_cost = item.extra_guest * item.content_object.extra_guest_fee
        order_items.append(
            {
                "id": str(item.id),
                "name": item.content_object.title,
                "caution": intcomma(int(item.content_object.caution_fee)),
                "type": item.item_type,
                "check_in": item.check_in.strftime("%m/%d/%Y, %H:%M:%S"),
                "check_out": item.check_out.strftime("%m/%d/%Y, %H:%M:%S"),
                "price": intcomma(int(item.get_final_price())),
                "extra_guests": item.extra_guest,
                "extra_guests_cost": intcomma(int(extra_guests_cost)),
            }
        )

    return JsonResponse(
        data={
            "the_profile_id": the_profile.id,
            "the_order_id": order.id,
            "completeOrder": json.dumps(orderInfo, default=str),
            "bookingInfo": json.dumps(bookingInfo),
            "order_items": json.dumps(order_items, default=str),
        },
    )


def payment_view(request, profile_id, order_id):
    template = "booking/payments.html"

    the_profile = Profile.objects.get(id=profile_id)

    order = Order.objects.get(id=order_id, ordered=False)

    context = {
        "order": order,
        "the_profile": the_profile,
        "TEST_PAYSTACK_PUBLIC_KEY": settings.TEST_PAYSTACK_PUBLIC_KEY,
        "LIVE_PAYSTACK_PUBLIC_KEY": settings.LIVE_PAYSTACK_PUBLIC_KEY,
        "TEST_FLW_PUBLIC_KEY": settings.TEST_FLW_PUBLIC_KEY,
    }

    return render(request, template, context)


@require_POST
@csrf_exempt
def process_paystack_payment(request):
    if request.method == "POST":
        reference = request.POST.get("paystackToken")
        order = Order.objects.get(id=reference, ordered=False)

        headers = {"Authorization": f"Bearer {settings.TEST_PAYSTACK_SECRET_KEY}"}
        resp = requests.get(
            f"https://api.paystack.co/transaction/verify/{reference}", headers=headers
        )

        response = resp.json()

        try:
            status = response["data"]["status"]
            auth_code = response["data"]["authorization"]["authorization_code"]
            if auth_code:
                print(auth_code)

            if status == "success":
                payment = Payment()
                payment.txn_code = reference
                payment.amount = int(order.get_total())
                payment.user = order.user
                payment.save()

                order_items = order.items.all()
                order_item_total = 0
                for item in order_items:
                    item.ordered = True
                    item.save()
                    try:

                        # update item stock availability for both room and packages
                        if item.item_type == choices.ProductType.Package.value:
                            the_package = Package.objects.get(id=item.object_id)

                            if the_package.slug == "silver":
                                handle_complimentary_booking(
                                    item.user.id,
                                    item.check_in,
                                    item.check_out,
                                    "silver",
                                )
                            elif the_package.slug == "gold":
                                handle_complimentary_booking(
                                    item.user.id, item.check_in, item.check_out, "gold"
                                )
                            elif the_package.slug == "bronze":
                                handle_complimentary_booking(
                                    item.user.id,
                                    item.check_in,
                                    item.check_out,
                                    "bronze",
                                )

                    except Exception as e:
                        print(e)
                        pass

                    order_item_total += item.get_final_price()

                order.ordered = True
                order.payment = payment
                order.ref_code = create_ref_code()
                order.save()
                # send an email to customer
                # send email to admin
                return redirect("core:home")
            else:
                print("payment failed")
                messages.warning(request, "Payment failed")
                return redirect(
                    "booking:payment-view", profile_id=order.user.id, order_id=order.id
                )

        except Exception as e:
            print("errors", e)
            return redirect(
                "booking:payment-view", profile_id=order.user.id, order_id=order.id
            )

    return redirect("core:home")


@require_POST
@csrf_exempt
def process_flutterwave_payment(request):
    if request.method == "POST":

        flutterwave_id = request.POST.get("flutterwave_id")
        order_ref = request.POST.get("order-ref")
        order = Order.objects.get(id=order_ref, ordered=False)

        headers = {"Authorization": f"Bearer {settings.TEST_FLW_SECRET_KEY}"}
        resp = requests.get(
            f"https://api.flutterwave.com/v3/transactions/{flutterwave_id}/verify",
            headers=headers,
        )
        response = resp.json()
        try:
            status = response["status"]
            response_tranx_ref = response["data"]["tx_ref"]
            if status == "success" and order.id == response_tranx_ref:
                payment = Payment()
                payment.txn_code = response_tranx_ref
                payment.amount = int(order.get_total())
                payment.user = order.user
                payment.save()

                order_items = order.items.all()
                order_item_total = 0
                for item in order_items:
                    item.ordered = True
                    item.save()
                    try:

                        # update item stock availability for both room and packages
                        if item.item_type == choices.ProductType.Package.value:
                            the_package = Package.objects.get(id=item.object_id)

                            if the_package.slug == "silver":
                                handle_complimentary_booking(
                                    item.user.id,
                                    item.check_in,
                                    item.check_out,
                                    "silver",
                                )
                            elif the_package.slug == "gold":
                                handle_complimentary_booking(
                                    item.user.id, item.check_in, item.check_out, "gold"
                                )
                            elif the_package.slug == "bronze":
                                handle_complimentary_booking(
                                    item.user.id,
                                    item.check_in,
                                    item.check_out,
                                    "bronze",
                                )

                    except Exception as e:
                        print(e)
                        pass
                    # update item stock availability for both room and packages

                    order_item_total += item.get_final_price()

                order.ordered = True
                order.payment = payment
                order.ref_code = create_ref_code()
                order.save()
                # send an email to customer
                # send email to admin
                return redirect("core:home")
            else:
                print("payment failed")
                messages.warning(request, "Payment failed")
                return redirect(
                    "booking:payment-view", profile_id=order.user.id, order_id=order.id
                )
        except Exception as e:
            messages.warning(request, "Payment failed")
            return redirect(
                "booking:payment-view", profile_id=order.user.id, order_id=order.id
            )

    return redirect("core:home")


@require_POST
@csrf_exempt
def paystack_webhook_view(request):
    print("This is an api webhook from paystack")
    new_wbh = WebhookBackup.objects.create(pay_sol="paystack")
    payload = json.loads(request.body)

    new_wbh.req_body = json.dumps(payload)
    new_wbh.save()

    paystack_sk = settings.TEST_PAYSTACK_SECRET_KEY

    computed_hmac = hmac.new(
        bytes(paystack_sk, "utf-8"),
        str.encode(request.body.decode("utf-8")),
        digestmod=hashlib.sha512,
    ).hexdigest()

    print(payload)

    sig_hash = request.headers.get("x-paystack-signature")

    if computed_hmac == sig_hash:
        reference = payload.get("data", {}).get("reference")
        if payload["event"] == "charge.success":
            user_email = payload["data"]["customer"]["email"]
            amount = payload["data"]["amount"]

            # check for the user
            the_user = User.objects.get(email=user_email)

            the_order_qs = Order.objects.filter(user=the_user.profile, ordered=False)
            if the_order_qs.exists():
                order = the_order_qs[0]
                # check order amount
                if order.get_total() == int(amount):
                    payment = Payment()
                    payment.txn_code = reference
                    payment.amount = int(order.get_total())
                    payment.user = the_user.profile
                    payment.save()

                    order_items = order.items.all()
                    # order_items.update(ordered=True)
                    for item in order_items:
                        item.ordered = True
                        item.save()

                    order.ordered = True
                    order.payment = payment
                    order.ref_code = create_ref_code()
                    order.save()

                    # send a successful card payment with receipt
                    return HttpResponse(status=200)

                else:
                    print("could not verify order amount")
                    # send help to shola or record to logs
                    new_app_log = AppLogs.objects.create(log_title="amount mismatch")
                    new_app_log.log = f"webhook body amount {int(amount)} does not match with order amount {order.get_total()}."
                    new_app_log.save()
                    return HttpResponse(status=200)
            else:
                print("payment already processed")
                return HttpResponse(status=200)
        else:
            return HttpResponse(status=200)


@require_POST
@csrf_exempt
def flutterwave_webhook_view(request):
    secret_hash = settings.FLW_SECRET_HASH
    signature = request.headers.get("verifi-hash")
    if signature == None or (signature != secret_hash):
        # This request isn't from Flutterwave; discard
        return HttpResponse(status=401)
    payload = request.body
    # It's a good idea to log all received events.
    new_wbh = WebhookBackup.objects.create(pay_sol="flutterwave")
    new_wbh.req_body = json.dumps(payload)
    new_wbh.save()
    # Do something (that doesn't take too long) with the payload
    return HttpResponse(status=200)
