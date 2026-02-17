from dataclasses import dataclass
from typing import Optional, Literal
from django.conf import settings
from django.core.mail import EmailMessage


ContactKind = Literal["contact", "demo"]


@dataclass(frozen=True)
class ContactEmailPayload:
    name: str
    email: str
    message: str
    kind: ContactKind = "contact"
    company: str = ""
    phone: str = ""


def send_contact_email(payload: ContactEmailPayload) -> None:
    to_email = getattr(settings, "CONTACT_FORM_TO_EMAIL", None) or getattr(
        settings, "DEFAULT_FROM_EMAIL", None
    )
    if not to_email:
        raise RuntimeError("CONTACT_FORM_TO_EMAIL or DEFAULT_FROM_EMAIL must be set.")

    subject = "HeartApp - Contact form"
    if payload.kind == "demo":
        subject = "HeartApp - Book a Demo"

    body = (
        f"Kind: {payload.kind}\n"
        f"Name: {payload.name}\n"
        f"Email: {payload.email}\n"
        f"Company: {payload.company}\n"
        f"Phone: {payload.phone}\n\n"
        f"Message:\n{payload.message}\n"
    )

    msg = EmailMessage(
        subject=subject,
        body=body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        to=[to_email],
        reply_to=[payload.email],
    )
    msg.send(fail_silently=False)
