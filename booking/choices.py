from enum import unique

from core.enum import DocEnum
from django.utils.translation import gettext_lazy as _


@unique
class VerificationStatus(DocEnum):
    """
    Verification Status.
    """

    Uploading = "Uploading", "Course content still being uploaded"
    Submitted = "Submitted", "Course content submitted"
    InReview = "In Review", "Course still in review"
    Approved = "Approved", "Course verification approved"
    Rejected = "Rejected", "Course verification rejected"
    Removed = "Removed", "Course removed by admin"


_readable_task_status = {
    VerificationStatus.Uploading.value: _("Uploading"),
    VerificationStatus.Submitted.value: _("Submitted"),
    VerificationStatus.InReview.value: _("In Review"),
    VerificationStatus.Rejected.value: _("Rejected"),
    VerificationStatus.Approved.value: _("Approved"),
    VerificationStatus.Removed.value: _("Removed"),
}


VERIFICATION_CHOICES = [
    (d.value, _readable_task_status[d.value]) for d in VerificationStatus
]


@unique
class ReviewTag(DocEnum):
    """
    Room Review Tags.
    """

    Comfort = "Comfort", "Review on comfort"
    Facilities = "Facilities", "Review on Facilities"
    Location = "Location", "Review on location"
    Price = "Price", "Price review"


_readable_review_tag = {
    ReviewTag.Comfort.value: _("Comfort"),
    ReviewTag.Facilities.value: _("Facilities"),
    ReviewTag.Location.value: _("Location"),
    ReviewTag.Price.value: _("Price"),
}


REVIEW_TAG_CHOICES = [(d.value, _readable_review_tag[d.value]) for d in ReviewTag]


@unique
class TemplateView(DocEnum):
    """
    Template View.
    """

    Normal = "normal", "Normal View"
    Inverted = "inverted", "Inverted view"


_readable_template_view = {
    TemplateView.Normal.value: _("normal"),
    TemplateView.Inverted.value: _("inverted"),
}


TEMPLATE_VIEW_CHOICES = [
    (d.value, _readable_template_view[d.value]) for d in TemplateView
]


@unique
class ProductType(DocEnum):
    """
    Product Type Enum.
    """

    Room = "room", "Room"
    Package = "package", "Package"


_readable_product_type = {
    ProductType.Room.value: _("room"),
    ProductType.Package.value: _("package"),
}


PRODUCT_TYPE_CHOICES = [(d.value, _readable_product_type[d.value]) for d in ProductType]


@unique
class PackagePriceOption(DocEnum):
    """
    Package Price Option.
    """

    Day = "day", "Day"
    Overnight = "overnight", "Overnight"


_readable_package_option = {
    PackagePriceOption.Day.value: _("day"),
    PackagePriceOption.Overnight.value: _("overnight"),
}


PACKAGE_OPTION_CHOICES = [
    (d.value, _readable_package_option[d.value]) for d in PackagePriceOption
]


@unique
class ClientType(DocEnum):
    """
    Client Type.
    """

    Personal = "Personal", "Personal user"
    Corporate = "Corporate ", "Corporate user"


_readable__client_type = {
    ClientType.Personal.value: _("Personal"),
    ClientType.Corporate.value: _("Corporate"),
}


CLIENT_TYPE_CHOICES = [(d.value, _readable__client_type[d.value]) for d in ClientType]
