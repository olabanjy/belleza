from enum import unique

from core.enum import DocEnum
from django.utils.translation import gettext_lazy as _


@unique
class UserType(DocEnum):
    """
    User Type.
    """

    Client = "Client", "Client"
    Admin = "Admin ", "Corporate user"


_readable__user_type = {
    UserType.Client.value: _("Client"),
    UserType.Admin.value: _("Admin"),
}

USER_TYPE_CHOICES = [(d.value, _readable__user_type[d.value]) for d in UserType]
