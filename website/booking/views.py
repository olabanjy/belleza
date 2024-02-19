from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.views.defaults import page_not_found
from django.views.generic import View
from django.core.paginator import Paginator
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from .utils import cookieCart, cartData, guestOrder, wee_day
from . import choices


import json
from django.http import JsonResponse


from .models import (
    Room,
    Package,
    Gallery,
    PackageComplimentary,
    OrderItem,
    Order,
)


def all_rooms(request):
    template = "booking/all_rooms.html"

    all_rooms = Room.objects.filter(is_active=True).all().order_by("created_at")

    context = {"all_rooms": all_rooms, "page_title": "Our Rooms"}

    return render(request, template, context)


def room_details(request, room_id):
    template = "booking/room_details.html"

    the_room = get_object_or_404(Room, id=room_id)

    similar_rooms = Room.objects.exclude(id__in=[the_room.id])

    context = {
        "the_room": the_room,
        "similar_rooms": similar_rooms,
        "page_title": f"{the_room.title}",
    }
    return render(request, template, context)


def all_packages(request):
    template = "booking/all_packages.html"

    all_packages = Package.objects.filter(is_active=True).all().order_by("created_at")

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


def check_availabilty(request):
    data = json.loads(request.body)
    print(data)
    json_resp = {}

    productId = data["productId"]
    productType = data["productType"]
    bookedDates = data["bookedDates"]
    quantity = data["quantity"]

    check_in_date, check_out_date = bookedDates.split("-")

    if productType == "room":
        # fetch room
        the_room = Room.objects.get(id=productId)
        product_type = ContentType.objects.get_for_model(Room)
        # check availabilty in order_item
        order_items_qs = OrderItem.objects.filter(
            content_type=product_type,
            object_id=the_room.id,
            item_type=choices.ProductType.Room.value,
            ordered=True,
            check_in__gte=datetime.strptime(check_in_date.strip(), "%d/%m/%Y"),
            check_out__lte=datetime.strptime(check_out_date.strip(), "%d/%m/%Y"),
        )
        print(order_items_qs)
        sum_agrregate = order_items_qs.aggregate(Sum("quantity"))
        print(sum_agrregate)
        if order_items_qs.exists():
            # subtract quantity booked from availabilty
            if the_room.availability <= sum_agrregate["quantity__sum"]:
                print(
                    "there is a problem here, ordered room should never be more than availabilty"
                )
                raise Exception("An error occured!")
            available_rooms = the_room.availability - sum_agrregate["quantity__sum"]
            if available_rooms > quantity:
                json_resp.update(
                    {
                        "is_available": True,
                        "message": "Room is available",
                        "room_name": the_room.title,
                        "check_in": check_in_date,
                        "check_out": check_out_date,
                    }
                )
            else:
                json_resp.update(
                    {
                        "is_available": False,
                        "message": f"{the_room.title} is full booked between {check_in_date} and {check_out_date}. Kindly book another room",
                        "room_name": the_room.title,
                        "check_in": check_in_date,
                        "check_out": check_out_date,
                    }
                )
        else:
            if the_room.availability > quantity:
                json_resp.update(
                    {
                        "is_available": True,
                        "message": "Room is available",
                        "room_name": the_room.title,
                        "check_in": check_in_date,
                        "check_out": check_out_date,
                    }
                )
            else:
                json_resp.update(
                    {
                        "is_available": False,
                        "message": f"{the_room.title} is full booked between {check_in_date} and {check_out_date}. Kindly book another room",
                        "room_name": the_room.title,
                        "check_in": check_in_date,
                        "check_out": check_out_date,
                    }
                )

    elif productType == "package":

        # Rework Package
        period = data["period"]

        check_weekday = wee_day(check_in_date)

        if check_weekday == True and period == "day":
            price_option = choices.PackagePriceOption.DayWeekday.value
        elif check_weekday == True and period == "night":
            price_option = choices.PackagePriceOption.OvernightWeekday.value

        elif check_weekday == False and period == "day":
            price_option = choices.PackagePriceOption.DayWeekend.value

        elif check_weekday == False and period == "night":
            price_option = choices.PackagePriceOption.OvernightWeekend.value

        the_package = Package.objects.get(id=productId)
        product_type = ContentType.objects.get_for_model(Package)
        # check availabilty in order_item
        order_items_qs = OrderItem.objects.filter(
            content_type=product_type,
            object_id=the_package.id,
            item_type=choices.ProductType.Package.value,
            ordered=True,
            check_in__gte=datetime.strptime(check_in_date.strip(), "%d/%m/%Y"),
            check_out__lte=datetime.strptime(check_out_date.strip(), "%d/%m/%Y"),
            package_price_option=price_option,
        )
        if order_items_qs.exists():

            json_resp.update(
                {
                    "is_available": False,
                    "message": f"{the_package.title} is full booked between {check_in_date} and {check_out_date}. Kindly book another room",
                    "package_name": the_package.title,
                    "check_in": check_in_date,
                    "check_out": check_out_date,
                }
            )
        else:
            json_resp.update(
                {
                    "is_available": True,
                    "message": f"{the_package.title} is available between {check_in_date} and {check_out_date}. Kindly book another room",
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

    print(cookieCart(request))

    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]

    template = "booking/cart.html"

    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, template, context)
