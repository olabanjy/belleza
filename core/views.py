from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.views.defaults import page_not_found
from django.views.generic import View
from django.core.paginator import Paginator


import json
from django.http import JsonResponse


from booking.models import Room, Package, Gallery, PackageComplimentary


def error404(request, exception):
    return page_not_found(request, exception, "errors/404.html")


def error500(request):
    return render(request, "errors/500.html")


def homepage(request):

    template = "core/index.html"

    all_rooms_qs = Room.objects.filter(is_active=True)
    featured_room = all_rooms_qs.filter(featured=True).first()
    other_rooms = all_rooms_qs.exclude(id__in=[featured_room.id]).all()[:2]

    all_packages = Package.objects.filter(is_active=True).all()

    context = {
        "all_rooms_qs": all_rooms_qs,
        "featured_room": featured_room,
        "other_rooms": other_rooms,
        "all_packages": all_packages,
        "page_title": "Beach Resort in Lagos",
    }

    return render(request, template, context)


def about(request):

    template = "core/about.html"

    context = {"page_title": "Beach Resort in Lagos"}

    return render(request, template, context)


def contact_us(request):

    template = "core/contact_us.html"

    context = {"page_title": "Contact Us"}

    return render(request, template, context)


def policy(request):

    template = "core/policy.html"

    context = {"page_title": "Privacy Policy"}

    return render(request, template, context)


def terms_and_condition(request):

    template = "core/terms.html"

    context = {"page_title": "Terms and Condition"}

    return render(request, template, context)
