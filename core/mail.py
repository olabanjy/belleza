from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.mail import EmailMultiAlternatives


# _logos = [
#     finders.find("images/app-icon.png"),
#     finders.find("images/app-logo.png"),
# ]


def _send_email(recipient, subject="", body_text="", body_html="", attachments=None, quiet=True):
    """
    Sends email to recipient.
    """

    body_html = body_html or f"<p>{body_text}</p>"

    email = EmailMultiAlternatives(
        subject=subject,
        body=f"{body_text}\n",
        from_email=settings.AUTO_MAIL_FROM,
        to=[recipient],
        alternatives=[(body_html, "text/html")],
        attachments=attachments,
    )

    # always attach logos
    # for img_path in _logos:
    #     img_name = img_path.split('/')[-1]

    #     with open(img_path, 'rb') as fp:
    #         img_file = MIMEImage(fp.read())

    #     img_file.add_header('Content-ID', f'<{img_name}>')

    #     email.attach(img_file)

    email.send(fail_silently=not quiet)
    return email


def send_email(*args, **kwargs):
    _send_email(*args, **kwargs)
