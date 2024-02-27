from django.db import models
from core.models import BaseAbstractModel
from . import choices

from django.utils.translation import gettext_lazy as _
from ums.models import Profile
from django.utils import timezone

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Features(BaseAbstractModel):
    slug = models.SlugField(null=False)
    title = models.CharField(max_length=240)
    icon = models.CharField(max_length=120, null=True)

    def __str__(self):
        return self.title


class Room(BaseAbstractModel):
    slug = models.SlugField(null=False)
    title = models.CharField(max_length=255)
    short_desc = models.CharField(max_length=400)
    long_desc = models.TextField(blank=True, null=True)
    price = models.DecimalField(
        decimal_places=2,
        help_text=_("the cost of the room"),
        max_digits=19,
    )
    discount_price = models.DecimalField(
        decimal_places=2,
        help_text=_("the cost of the room"),
        max_digits=19,
    )
    caution_fee = models.DecimalField(
        decimal_places=2,
        help_text=_("the caution fee"),
        max_digits=19,
    )
    availability = models.IntegerField(default=1)
    # stock_availability = models.IntegerField(default=1)
    check_in = models.CharField(max_length=240, null=True)
    check_out = models.CharField(max_length=240, null=True)
    banner = models.ImageField(upload_to="rooms/banner/", blank=True, null=True)
    thumbnail = models.ImageField(upload_to="rooms/thumbnail/", blank=True, null=True)
    gallery = models.ManyToManyField("Gallery", blank=True, related_name="room_gallery")
    featured = models.BooleanField(default=False)
    features = models.ManyToManyField("Features", blank=True, related_name="features")
    featured_feat = models.ManyToManyField(
        "Features", blank=True, related_name="featured_features"
    )
    template_view = models.TextField(
        choices=choices.TEMPLATE_VIEW_CHOICES,
        default=choices.TemplateView.Normal.value,
        verbose_name=_("template_view"),
    )
    position = models.IntegerField(default=1)

    def __str__(self):
        return self.title


class Gallery(BaseAbstractModel):
    images = models.ImageField(upload_to="rooms/gallery/", blank=True, null=True)


class RoomReview(BaseAbstractModel):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True)
    full_name = models.CharField(max_length=240, blank=True, null=True)
    tag = models.TextField(
        choices=choices.REVIEW_TAG_CHOICES,
        default=choices.ReviewTag.Comfort.value,
        verbose_name=_("tag"),
    )
    title = models.CharField(max_length=240, blank=True, null=True)
    review = models.TextField(blank=True, null=True)
    rating = models.IntegerField(default=0)
    status = models.TextField(
        choices=choices.VERIFICATION_CHOICES,
        default=choices.VerificationStatus.Approved.value,
        verbose_name=_("status"),
    )

    def __str__(self):
        return self.room.title


class Package(BaseAbstractModel):
    slug = models.SlugField(null=False)
    title = models.CharField(max_length=255)
    short_desc = models.CharField(max_length=400)
    long_desc = models.TextField(blank=True, null=True)
    nos_of_guest = models.IntegerField(default=0)
    banner = models.ImageField(upload_to="package/banner/", blank=True, null=True)
    detail_banner_1 = models.ImageField(
        upload_to="package/detail_banner/", blank=True, null=True
    )
    detail_banner_2 = models.ImageField(
        upload_to="package/detail_banner/", blank=True, null=True
    )
    detail_banner_3 = models.ImageField(
        upload_to="package/detail_banner/", blank=True, null=True
    )
    gallery = models.ManyToManyField(
        "Gallery", blank=True, related_name="package_gallery"
    )
    # complimentary = models.CharField(max_length=400, null=True)
    caution_fee = models.DecimalField(
        decimal_places=2,
        help_text=_("the caution fee"),
        max_digits=19,
    )
    extra_guest_fee = models.DecimalField(
        decimal_places=2,
        help_text=_("the cost of extra guest"),
        max_digits=19,
    )
    day_price = models.DecimalField(
        decimal_places=2,
        help_text=_("day booking price"),
        max_digits=19,
        blank=True,
        null=True,
    )
    overnight_price = models.DecimalField(
        decimal_places=2,
        help_text=_("overnight booking price"),
        max_digits=19,
        blank=True,
        null=True,
    )

    day_weekday_price = models.DecimalField(
        decimal_places=2,
        help_text=_("weekday day booking price"),
        max_digits=19,
        blank=True,
        null=True,
    )
    overnight_weekday_price = models.DecimalField(
        decimal_places=2,
        help_text=_("weekday overnight booking price"),
        max_digits=19,
        blank=True,
        null=True,
    )
    day_weekend_price = models.DecimalField(
        decimal_places=2,
        help_text=_("weekend day booking price"),
        max_digits=19,
        blank=True,
        null=True,
    )
    overnight_weekend_price = models.DecimalField(
        decimal_places=2,
        help_text=_("weekend overnight booking price"),
        max_digits=19,
        blank=True,
        null=True,
    )

    features = models.ManyToManyField("Features", blank=True)
    position = models.IntegerField(default=1)

    def __str__(self):
        return self.title


class PackageComplimentary(BaseAbstractModel):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="room")
    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name="package"
    )
    number = models.IntegerField(default=1)

    def __str__(self):
        return self.package.title


###Base Models
class CustomContentBaseTypeModel(BaseAbstractModel):
    content_type = models.ForeignKey(
        ContentType, on_delete=models.PROTECT, blank=True, null=True
    )
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        ordering = ["id"]


class OrderItem(CustomContentBaseTypeModel):
    user = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)
    ordered = models.BooleanField(default=False)

    item_type = models.TextField(
        choices=choices.PRODUCT_TYPE_CHOICES,
        default=choices.ProductType.Room.value,
        verbose_name=_("product_type"),
    )
    package_price_option = models.TextField(
        choices=choices.PACKAGE_OPTION_CHOICES,
        null=True,
        blank=True,
        verbose_name=_("package_option"),
    )
    extra_guest = models.IntegerField(blank=True, null=True)
    is_complimentary = models.BooleanField(default=False)
    quantity = models.IntegerField(default=1)
    rate = models.IntegerField(default=1)
    check_in = models.DateTimeField(null=True)
    check_out = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.id} - {self.user} - {self.quantity}"

    def get_total_item_price(self):
        if self.content_object:
            if self.item_type == choices.ProductType.Room.value:
                return (
                    self.quantity * self.rate * self.content_object.price
                    + self.content_object.caution_fee
                )
            elif self.item_type == choices.ProductType.Package.value:
                if self.package_price_option == choices.PackagePriceOption.Day.value:
                    if self.extra_guest and self.extra_guest > 0:
                        extra_guest_cost = (
                            self.extra_guest * self.content_object.extra_guest_fee
                        )
                        return (
                            (self.quantity * self.content_object.day_price * self.rate)
                            + extra_guest_cost
                            + self.content_object.caution_fee
                        )
                    return (
                        self.quantity * self.content_object.day_price * self.rate
                        + self.content_object.caution_fee
                    )
                elif (
                    self.package_price_option
                    == choices.PackagePriceOption.Overnight.value
                ):
                    if self.extra_guest and self.extra_guest > 0:
                        extra_guest_cost = (
                            self.extra_guest * self.content_object.extra_guest_fee
                        )
                        return (
                            (self.quantity * self.content_object.day_price * self.rate)
                            + extra_guest_cost
                            + self.content_object.caution_fee
                        )

                    return (
                        self.quantity * self.content_object.overnight_price * self.rate
                        + self.content_object.caution_fee
                    )

            else:
                return 0

    def get_total_discount_item_price(self):
        if self.content_object and self.item_type == choices.ProductType.Room.value:
            return self.quantity * self.content_object.discount_price * self.rate
        else:
            return 0

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item_type == choices.ProductType.Room.value:
            if self.content_object and self.content_object.discount_price:
                return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(BaseAbstractModel):
    user = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)
    items = models.ManyToManyField("OrderItem")
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    ordered_date = models.DateTimeField(default=timezone.now)
    ordered = models.BooleanField(default=False)

    payment = models.ForeignKey(
        "Payment", on_delete=models.SET_NULL, blank=True, null=True
    )
    coupon = models.ForeignKey(
        "Coupon", on_delete=models.SET_NULL, blank=True, null=True
    )

    booking_info = models.ForeignKey(
        "BookingInfo", on_delete=models.CASCADE, blank=True, null=True
    )

    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user}"

    def get_total(self):
        total = 0
        if self.items:
            for order_item in self.items.all():
                total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount

        return total


class Payment(BaseAbstractModel):
    txn_code = models.CharField(max_length=50)
    user = models.ForeignKey(Profile, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.txn_code}"


class Coupon(BaseAbstractModel):
    code = models.CharField(max_length=15)
    amount = models.IntegerField()

    def __str__(self):
        return self.code


class Refund(BaseAbstractModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.pk}"


class WebhookBackup(BaseAbstractModel):
    pay_sol = models.CharField(max_length=100, blank=True, null=True)
    req_body = models.TextField(blank=True, null=True)


class AppLogs(BaseAbstractModel):
    log_title = models.CharField(max_length=500, blank=True, null=True)
    log = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.log_title} - {self.created_at}"


class BookingInfo(BaseAbstractModel):
    user = models.ForeignKey(Profile, on_delete=models.SET_NULL, blank=True, null=True)
    phone = models.CharField(max_length=40, null=True, blank=True)
    other_phone = models.CharField(max_length=40, null=True, blank=True)
    phone_verified = models.BooleanField(default=False)
    full_name = models.CharField(blank=True, null=True, max_length=200)
    company_name = models.CharField(blank=True, null=True, max_length=200)
    address = models.TextField(blank=True, null=True)
    corporate_rep = models.CharField(blank=True, null=True, max_length=200)
    number_of_guests = models.IntegerField(default=1)
    nature_of_business = models.CharField(blank=True, null=True, max_length=400)
    client_type = models.TextField(
        choices=choices.CLIENT_TYPE_CHOICES,
        default=choices.ClientType.Personal.value,
        verbose_name=_("client_type"),
    )

    def __str__(self):
        return f"{self.user}"
