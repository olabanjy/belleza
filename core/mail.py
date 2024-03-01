from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.mail import EmailMultiAlternatives, EmailMessage, send_mail
from django.template.loader import render_to_string


# _logos = [
#     finders.find("images/app-icon.png"),
#     finders.find("images/app-logo.png"),
# ]


def _send_email_old(
    recipient, subject="", body_text="", body_html="", attachments=None, quiet=True
):
    """
    Sends email to recipient.
    """

    body_html = body_html or f"<p>{body_text}</p>"

    email = EmailMultiAlternatives(
        subject=subject,
        body=f"{body_text}\n",
        from_email=settings.EMAIL_HOST,
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


def send_email_old(*args, **kwargs):
    _send_email_old(*args, **kwargs)


def send_email(recipients, subject="", html_path="", context={}):

    subject, from_email, to = (
        subject,
        "Belleza Beach Resort <notifications@bellezabeachresort.com>",
        recipients,
    )
    html_content = render_to_string(
        html_path,
        context,
    )

    msg = EmailMessage(subject, html_content, from_email, to)
    msg.content_subtype = "html"
    msg.send()
    return msg
