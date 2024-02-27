from django.contrib import admin
from .models import *

from import_export import resources

from import_export.admin import ImportExportModelAdmin


# Register your models here.


class RoomResource(resources.ModelResource):

    class Meta:
        model = Room


class RoomAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_classes = [RoomResource]
    list_display = (
        "slug",
        "title",
        "short_desc",
        "price",
        "caution_fee",
        "availability",
        # "stock_availability",
        "template_view",
    )
    search_fields = ["slug", "title"]


class RoomReviewAdmin(admin.ModelAdmin):

    list_display = ("room", "full_name", "tag", "title", "review", "rating", "status")
    search_fields = ["title"]


class FeatureResource(resources.ModelResource):
    class Meta:
        model = Features


class FeaturesAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_classes = [FeatureResource]
    list_display = (
        "slug",
        "title",
        "icon",
    )
    search_fields = ["title"]


admin.site.register(Room, RoomAdmin)


class GalleryResource(resources.ModelResource):
    class Meta:
        model = Gallery


class GalleryAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_classes = [GalleryResource]


admin.site.register(Gallery, GalleryAdmin)
admin.site.register(Features, FeaturesAdmin)
admin.site.register(RoomReview, RoomReviewAdmin)


class PackageResource(resources.ModelResource):

    class Meta:
        model = Package


class PackageAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_classes = [PackageResource]
    list_display = (
        "slug",
        "title",
        "short_desc",
        "day_weekday_price",
        "overnight_weekday_price",
        "day_weekend_price",
        "overnight_weekend_price",
        "caution_fee",
        "nos_of_guest",
        "extra_guest_fee",
    )
    search_fields = ["slug", "title"]


admin.site.register(Package, PackageAdmin)


class PackageComplimentaryResource(resources.ModelResource):

    class Meta:
        model = PackageComplimentary


class PackageComplimentaryAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_classes = [PackageComplimentaryResource]
    list_display = ("room", "package", "number")
    search_fields = ["package"]


admin.site.register(PackageComplimentary, PackageComplimentaryAdmin)


class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "ordered",
        "item_type",
        "package_price_option",
        "quantity",
        "check_in",
        "check_out",
        "object_id",
        "content_object",
    )


admin.site.register(OrderItem, OrderItemAdmin)


class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "ref_code",
        "ordered_date",
        "ordered",
        "payment",
        "booking_info",
        "refund_requested",
        "refund_granted",
    )


admin.site.register(Order, OrderAdmin)
