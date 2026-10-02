from __future__ import annotations

from dataclasses import dataclass
import html
import logging
import smtplib
import ssl
from email.message import EmailMessage
from urllib.parse import urlsplit

import httpx

from app.core.config import Settings, email_domain
from app.schemas.enquiry import EnquiryRecord, EnquiryType

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class NotificationResult:
    staff_sent: bool = False
    customer_sent: bool = False
    provider: str = "none"


class NotificationService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def configuration_status(self) -> dict[str, object]:
        provider = self.settings.effective_email_provider
        enabled = self.settings.email_delivery_enabled
        issues: list[str] = []

        if not enabled:
            issues.append("Transactional email is disabled. Set EMAIL_ENABLED=true or configure RESEND_API_KEY.")
        from_email = self.settings.effective_from_email
        if not from_email:
            issues.append("The active email provider does not have a sender address configured.")
        if provider == "none":
            issues.append("No email transport is configured. Set RESEND_API_KEY or SMTP_HOST.")
        elif provider == "resend":
            if not self.settings.effective_resend_api_key:
                issues.append("EMAIL_PROVIDER=resend requires RESEND_API_KEY or legacy Resend SMTP credentials.")
        elif provider == "smtp":
            if not self.settings.smtp_host:
                issues.append("EMAIL_PROVIDER=smtp requires SMTP_HOST.")
            if bool(self.settings.smtp_username) != bool(self.settings.smtp_password):
                issues.append("SMTP_USERNAME and SMTP_PASSWORD must be configured together.")
        if self.settings.uses_resend_transport and not self.settings.resend_sender_domain_matches:
            issues.append(
                "Resend sender domain mismatch: "
                f"RESEND_FROM_EMAIL must use @{self.settings.resend_sending_domain}."
            )
        if not self.settings.sales_notification_email:
            issues.append("SALES_NOTIFICATION_EMAIL is not configured; staff notifications will be skipped.")
        cityview_url = self.settings.cityview_public_url

        customer_ready = enabled and bool(from_email) and provider != "none"
        if provider == "resend":
            customer_ready = customer_ready and bool(self.settings.effective_resend_api_key)
        elif provider == "smtp":
            customer_ready = customer_ready and bool(self.settings.smtp_host) and (
                bool(self.settings.smtp_username) == bool(self.settings.smtp_password)
            )
        if self.settings.uses_resend_transport:
            customer_ready = customer_ready and self.settings.resend_sender_domain_matches

        return {
            "enabled": enabled,
            "ready": customer_ready,
            "provider": provider,
            "from_configured": bool(from_email),
            "from_domain": email_domain(from_email),
            "resend_domain_match": self.settings.resend_sender_domain_matches,
            "staff_recipient_configured": bool(self.settings.sales_notification_email),
            "cityview_url_configured": bool(cityview_url),
            "cityview_url": cityview_url,
            "resend_key_configured": bool(self.settings.effective_resend_api_key),
            "resend_key_source": self.settings.resend_key_source,
            "issues": issues,
        }

    def send_enquiry_notifications(self, enquiry: EnquiryRecord) -> NotificationResult:
        """Send staff and customer email notifications without risking the enquiry.

        The enquiry is already stored before this method is called. Each email is
        attempted independently so a temporary provider error cannot remove or
        invalidate the saved lead.
        """
        status = self.configuration_status()
        provider = str(status["provider"])
        if not status["enabled"]:
            logger.warning("Transactional email disabled; enquiry notifications skipped")
            return NotificationResult(provider=provider)
        if not status["ready"]:
            logger.warning("Transactional email is not ready: %s", "; ".join(status["issues"]))
            return NotificationResult(provider=provider)

        staff_sent = False
        customer_sent = False

        # Customer acknowledgement is the primary transactional response, so it
        # is attempted first. The enquiry is already persisted, and a slower
        # internal staff notification must not delay the buyer's City View email.
        if enquiry.email:
            try:
                self._send_customer_acknowledgement(enquiry)
                customer_sent = True
            except Exception:
                logger.exception("Customer acknowledgement failed for enquiry %s", enquiry.reference_number)
        else:
            logger.info("Customer email absent; acknowledgement skipped for enquiry %s", enquiry.reference_number)

        if self.settings.sales_notification_email:
            try:
                self._send_sales_notification(enquiry)
                staff_sent = True
            except Exception:
                logger.exception("Sales notification failed for enquiry %s", enquiry.reference_number)
        else:
            logger.warning(
                "SALES_NOTIFICATION_EMAIL is not configured; staff email skipped for enquiry %s",
                enquiry.reference_number,
            )

        return NotificationResult(
            staff_sent=staff_sent,
            customer_sent=customer_sent,
            provider=provider,
        )

    def send_test_email(self, recipient: str) -> str:
        status = self.configuration_status()
        if not status["ready"]:
            raise RuntimeError("Email delivery is not ready: " + "; ".join(status["issues"]))

        msg = EmailMessage()
        msg["Subject"] = "ONA Towers email delivery test"
        msg["From"] = self._from_header()
        msg["To"] = recipient
        if self.settings.sales_notification_email:
            msg["Reply-To"] = str(self.settings.sales_notification_email)
        msg["Auto-Submitted"] = "auto-generated"
        msg.set_content(
            "ONA Towers email delivery is working.\n\n"
            f"City View: {self.settings.cityview_public_url}\n"
        )
        msg.add_alternative(
            f"""<!doctype html><html><body style="margin:0;background:#f4efe7;font-family:Arial,sans-serif;color:#302a26;">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f4efe7;padding:32px 14px;"><tr><td align="center">
<table role="presentation" width="620" cellspacing="0" cellpadding="0" style="width:100%;max-width:620px;background:#fffdf9;border:1px solid #e8dfd4;border-radius:8px;overflow:hidden;">
<tr><td align="center" style="padding:28px;background:#24333d;color:#fff;"><div style="font-family:Georgia,serif;font-size:32px;letter-spacing:7px;">ÔNA</div><div style="margin-top:7px;color:#c7a373;font-size:10px;letter-spacing:5px;">TOWERS</div></td></tr>
<tr><td style="padding:38px 42px;"><h1 style="font-family:Georgia,serif;font-weight:400;font-size:30px;margin:0 0 18px;">Email delivery is working.</h1><p style="color:#665f58;line-height:1.7;">This test confirms that the ONA Towers backend can send transactional email using the configured provider.</p><p style="margin:28px 0 0;"><a href="{html.escape(self.settings.cityview_public_url, quote=True)}" style="display:inline-block;background:#ad8759;color:#fff;text-decoration:none;padding:15px 24px;font-size:12px;font-weight:700;letter-spacing:1.4px;">OPEN CITY VIEW →</a></p></td></tr>
</table></td></tr></table></body></html>""",
            subtype="html",
        )
        return self._send_message(msg, idempotency_key=f"ona-test/{recipient}")

    def _send_message(self, message: EmailMessage, *, idempotency_key: str) -> str:
        provider = self.settings.effective_email_provider
        if provider == "resend":
            return self._resend_send(message, idempotency_key=idempotency_key)
        if provider == "smtp":
            self._smtp_send(message)
            return "smtp"
        raise RuntimeError("No configured email provider")

    def _resend_send(self, message: EmailMessage, *, idempotency_key: str) -> str:
        api_key = self.settings.effective_resend_api_key
        if not api_key:
            raise RuntimeError("RESEND_API_KEY is not configured")

        plain_part = message.get_body(preferencelist=("plain",))
        html_part = message.get_body(preferencelist=("html",))
        payload: dict[str, object] = {
            "from": str(message["From"]),
            "to": [str(message["To"])],
            "subject": str(message["Subject"]),
            "text": plain_part.get_content() if plain_part else "",
        }
        if html_part:
            payload["html"] = html_part.get_content()
        if message.get("Reply-To"):
            payload["reply_to"] = str(message["Reply-To"])

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Idempotency-Key": idempotency_key[:256],
        }
        with httpx.Client(timeout=self.settings.email_timeout_seconds) as client:
            response = client.post(self.settings.resend_api_url, headers=headers, json=payload)
        if response.is_error:
            detail = response.text[:500]
            raise RuntimeError(f"Resend returned HTTP {response.status_code}: {detail}")
        body = response.json()
        email_id = body.get("id")
        if not email_id:
            raise RuntimeError("Resend accepted the request but did not return an email id")
        logger.info("Resend accepted email %s", email_id)
        return str(email_id)

    def _smtp_send(self, message: EmailMessage) -> None:
        host = self.settings.smtp_host
        if not host:
            raise RuntimeError("SMTP_HOST is not configured")

        timeout = self.settings.email_timeout_seconds
        if self.settings.smtp_port in {465, 2465}:
            with smtplib.SMTP_SSL(host, self.settings.smtp_port, timeout=timeout, context=ssl.create_default_context()) as server:
                if self.settings.smtp_username and self.settings.smtp_password:
                    server.login(self.settings.smtp_username, self.settings.smtp_password)
                server.send_message(message)
            return

        with smtplib.SMTP(host, self.settings.smtp_port, timeout=timeout) as server:
            if self.settings.smtp_use_tls:
                server.starttls(context=ssl.create_default_context())
            if self.settings.smtp_username and self.settings.smtp_password:
                server.login(self.settings.smtp_username, self.settings.smtp_password)
            server.send_message(message)

    def _from_header(self) -> str:
        from_email = self.settings.effective_from_email
        if not from_email:
            raise RuntimeError("No sender email is configured for the active email provider")
        return f"{self.settings.smtp_from_name} <{from_email}>"

    def _send_sales_notification(self, enquiry: EnquiryRecord) -> None:
        msg = EmailMessage()
        msg["Subject"] = f"New ONA Towers enquiry - {enquiry.reference_number}"
        msg["From"] = self._from_header()
        msg["To"] = str(self.settings.sales_notification_email)
        if enquiry.email:
            msg["Reply-To"] = str(enquiry.email)

        msg.set_content(
            "\n".join(
                [
                    f"Reference: {enquiry.reference_number}",
                    f"Name: {enquiry.name}",
                    f"Phone: {enquiry.phone}",
                    f"Email: {enquiry.email or '-'}",
                    f"Residence interest: {enquiry.residence_interest or '-'}",
                    f"Enquiry type: {enquiry.enquiry_type.value}",
                    f"Message: {enquiry.message or '-'}",
                    f"Source: {enquiry.source}",
                    "",
                    f"City View: {self.settings.cityview_public_url}",
                ]
            )
        )
        self._send_message(msg, idempotency_key=f"ona-staff/{enquiry.reference_number}")

    def _send_customer_acknowledgement(self, enquiry: EnquiryRecord) -> None:
        cityview_url = self.settings.cityview_public_url
        parsed_public_url = urlsplit(cityview_url)
        site_root = f"{parsed_public_url.scheme}://{parsed_public_url.netloc}"
        layouts_url = f"{site_root}/layouts"
        enquire_url = f"{site_root}/enquire"
        hero_url = f"{site_root}/ona-assets/hero/hero-ocean-view.jpg"
        tower_url = f"{site_root}/ona-assets/hero/ona-home-vision-premium.png"
        floorplan_url = f"{site_root}/ona-assets/floorplans/brochure-3br.png"
        viewing_url = f"{site_root}/ona-assets/commercial/ona-house-gate-premium.png"
        subject, _, intro = self._customer_email_copy(enquiry)

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self._from_header()
        msg["To"] = str(enquiry.email)
        if self.settings.sales_notification_email:
            msg["Reply-To"] = str(self.settings.sales_notification_email)
        msg["Auto-Submitted"] = "auto-generated"

        msg.set_content(
            "\n".join(
                [
                    f"Dear {enquiry.name},",
                    "",
                    "Thank you for your interest in ONA Towers.",
                    intro,
                    "A dedicated member of our team will be in touch with you shortly to assist with your residence selection, current availability and private viewing arrangements.",
                    "",
                    "In the meantime, you can explore the ONA Towers collection, view available units, compare towers and floors, and download the floor plans.",
                    "",
                    f"Explore ONA Towers: {layouts_url}",
                    f"Current availability: {cityview_url}",
                    f"Book a viewing: {enquire_url}",
                    "",
                    f"Enquiry reference: {enquiry.reference_number}",
                    "",
                    "ONA Towers · Zanzibar, Tanzania",
                    "Live above. See beyond.",
                ]
            )
        )

        customer_name = html.escape(enquiry.name)
        reference = html.escape(enquiry.reference_number)
        safe_intro = html.escape(intro)
        safe_layouts_url = html.escape(layouts_url, quote=True)
        safe_cityview_url = html.escape(cityview_url, quote=True)
        safe_enquire_url = html.escape(enquire_url, quote=True)
        safe_hero_url = html.escape(hero_url, quote=True)
        safe_tower_url = html.escape(tower_url, quote=True)
        safe_floorplan_url = html.escape(floorplan_url, quote=True)
        safe_viewing_url = html.escape(viewing_url, quote=True)

        msg.add_alternative(
            f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(subject)}</title>
  <style>
    @media only screen and (max-width: 640px) {{
      .email-shell {{ width:100% !important; }}
      .content-pad {{ padding:34px 24px 30px !important; }}
      .hero-copy {{ padding:34px 24px !important; }}
      .hero-logo {{ font-size:36px !important; letter-spacing:8px !important; }}
      .headline {{ font-size:35px !important; }}
      .card-cell {{ display:block !important; width:100% !important; padding:0 0 20px !important; }}
      .footer-cell {{ display:block !important; width:100% !important; text-align:left !important; padding:8px 24px !important; }}
    }}
  </style>
</head>
<body style="margin:0;padding:0;background:#eee9e1;font-family:Arial,Helvetica,sans-serif;color:#37302b;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="width:100%;background:#eee9e1;margin:0;padding:0;">
    <tr>
      <td align="center" style="padding:0;">
        <table role="presentation" width="760" cellspacing="0" cellpadding="0" border="0" class="email-shell" style="width:100%;max-width:760px;background:#faf7f2;margin:0 auto;">
          <tr>
            <td background="{safe_hero_url}" valign="top" style="height:330px;background-image:url('{safe_hero_url}');background-size:cover;background-position:center center;background-color:#c9b59f;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="height:330px;">
                <tr>
                  <td valign="top" class="hero-copy" style="padding:34px 46px;">
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                      <tr>
                        <td valign="top">
                          <div class="hero-logo" style="font-family:Georgia,'Times New Roman',serif;color:#26231f;font-size:43px;letter-spacing:10px;line-height:1;font-weight:400;">ÔNA</div>
                          <div style="margin-top:10px;color:#7f674f;font-size:11px;font-weight:700;letter-spacing:6px;line-height:1;text-transform:uppercase;">Towers</div>
                        </td>
                        <td valign="top" align="right" style="color:#685a4d;font-size:10px;font-weight:700;letter-spacing:3.4px;line-height:2;text-transform:uppercase;">LIVE ABOVE<br>SEE BEYOND<br><span style="display:inline-block;width:42px;border-top:1px solid #8d7a67;margin-top:6px;">&nbsp;</span></td>
                      </tr>
                      <tr>
                        <td colspan="2" valign="bottom" style="height:168px;">
                          <div style="color:#675c51;font-size:10px;font-weight:700;letter-spacing:3px;line-height:1.8;text-transform:uppercase;">Luxury Residences<br>Zanzibar</div>
                          <div style="width:38px;border-top:1px solid #9d8a76;margin-top:10px;">&nbsp;</div>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <tr>
            <td class="content-pad" style="padding:38px 48px 34px;background:#fbf8f3;">
              <p style="margin:0 0 24px;color:#474039;font-size:15px;line-height:1.6;">Dear {customer_name},</p>
              <h1 class="headline" style="margin:0 0 26px;font-family:Georgia,'Times New Roman',serif;color:#39312b;font-size:43px;font-weight:400;line-height:1.12;">Thank you for your interest<br>in ÔNA Towers.</h1>
              <p style="margin:0 0 20px;color:#59524c;font-size:15px;line-height:1.75;">{safe_intro} A dedicated member of our team will be in touch with you shortly to assist with your residence selection, current availability and private viewing arrangements.</p>
              <p style="margin:0 0 26px;color:#59524c;font-size:15px;line-height:1.75;">In the meantime, you can explore the ÔNA Towers collection, view available units, compare towers and floors, and download the floor plans.</p>

              <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin:0 0 28px;">
                <tr>
                  <td style="background:#b48b5e;">
                    <a href="{safe_layouts_url}" style="display:inline-block;padding:17px 28px;color:#ffffff;text-decoration:none;font-size:11px;font-weight:700;letter-spacing:2.8px;text-transform:uppercase;">EXPLORE ÔNA TOWERS &nbsp;&nbsp;→</a>
                  </td>
                </tr>
              </table>

              <div style="border-top:1px solid #ddd3c7;margin:0 0 22px;"></div>

              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="width:100%;">
                <tr>
                  <td width="25%" valign="top" class="card-cell" style="padding:0 6px 0 0;">
                    <a href="{safe_layouts_url}" style="text-decoration:none;color:#39312b;">
                      <img src="{safe_hero_url}" width="154" alt="ÔNA Towers residences" style="display:block;width:100%;height:126px;object-fit:cover;border:0;">
                      <div style="padding:12px 4px 0;text-align:center;font-size:10px;font-weight:700;letter-spacing:2.1px;text-transform:uppercase;">Residences</div>
                      <div style="padding:7px 4px 0;text-align:center;color:#9a8d80;font-size:8px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;">Explore the collection</div>
                    </a>
                  </td>
                  <td width="25%" valign="top" class="card-cell" style="padding:0 6px;">
                    <a href="{safe_cityview_url}" style="text-decoration:none;color:#39312b;">
                      <img src="{safe_tower_url}" width="154" alt="ÔNA Towers availability" style="display:block;width:100%;height:126px;object-fit:cover;border:0;">
                      <div style="padding:12px 4px 0;text-align:center;font-size:10px;font-weight:700;letter-spacing:2.1px;text-transform:uppercase;">Availability</div>
                      <div style="padding:7px 4px 0;text-align:center;color:#9a8d80;font-size:8px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;">Check current units</div>
                    </a>
                  </td>
                  <td width="25%" valign="top" class="card-cell" style="padding:0 6px;">
                    <a href="{safe_layouts_url}" style="text-decoration:none;color:#39312b;">
                      <img src="{safe_floorplan_url}" width="154" alt="ÔNA Towers floor plans" style="display:block;width:100%;height:126px;object-fit:cover;border:0;">
                      <div style="padding:12px 4px 0;text-align:center;font-size:10px;font-weight:700;letter-spacing:2.1px;text-transform:uppercase;">Floor Plans</div>
                      <div style="padding:7px 4px 0;text-align:center;color:#9a8d80;font-size:8px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;">View &amp; download</div>
                    </a>
                  </td>
                  <td width="25%" valign="top" class="card-cell" style="padding:0 0 0 6px;">
                    <a href="{safe_enquire_url}" style="text-decoration:none;color:#39312b;">
                      <img src="{safe_viewing_url}" width="154" alt="Book an ÔNA Towers viewing" style="display:block;width:100%;height:126px;object-fit:cover;border:0;">
                      <div style="padding:12px 4px 0;text-align:center;font-size:10px;font-weight:700;letter-spacing:2.1px;text-transform:uppercase;">Book a Viewing</div>
                      <div style="padding:7px 4px 0;text-align:center;color:#9a8d80;font-size:8px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;">Private appointment</div>
                    </a>
                  </td>
                </tr>
              </table>

              <div style="border-top:1px solid #ddd3c7;margin:29px 0 20px;"></div>
              <div style="color:#9a8d80;font-size:9px;font-weight:700;letter-spacing:2px;text-transform:uppercase;">Enquiry reference</div>
              <div style="margin-top:8px;color:#39312b;font-size:15px;font-weight:700;letter-spacing:.5px;">{reference}</div>
            </td>
          </tr>

          <tr>
            <td style="padding:24px 40px;background:#f0e9df;border-top:1px solid #e2d8ca;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                <tr>
                  <td width="28%" valign="middle" class="footer-cell" style="font-family:Georgia,'Times New Roman',serif;color:#625548;font-size:25px;letter-spacing:6px;">ÔNA<br><span style="font-family:Arial,Helvetica,sans-serif;font-size:8px;font-weight:700;letter-spacing:4px;text-transform:uppercase;">Towers</span></td>
                  <td width="45%" valign="middle" class="footer-cell" style="border-left:1px solid #d4c9bc;padding-left:24px;color:#8b7b6a;font-size:11px;line-height:1.55;">A member of ONIRIA Investments<br><span style="color:#a38d73;">Distinctive places. Unmistakably ONIRIA.</span></td>
                  <td width="27%" valign="middle" align="right" class="footer-cell" style="color:#8b7b6a;font-size:8px;font-weight:700;letter-spacing:2px;line-height:1.8;text-transform:uppercase;">Zanzibar, Tanzania<br>ONATOWERS.COM</td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>""",
            subtype="html",
        )

        self._send_message(msg, idempotency_key=f"ona-customer/{enquiry.reference_number}")

    @staticmethod
    def _customer_email_copy(enquiry: EnquiryRecord) -> tuple[str, str, str]:
        if enquiry.enquiry_type == EnquiryType.request_floor_plans:
            return (
                "Your ONA Towers floor plans and residence availability",
                "View floor plans & availability",
                "We have received your request for ONA Towers floor plans and residence information.",
            )
        if enquiry.enquiry_type == EnquiryType.schedule_viewing:
            return (
                "Your ONA Towers viewing enquiry",
                "Explore residences",
                "We have received your viewing enquiry and shared it with the ONA Towers sales team.",
            )
        if enquiry.enquiry_type == EnquiryType.talk_to_sales:
            return (
                "Your ONA Towers private sales enquiry",
                "Explore available residences",
                "We have received your request to speak with the ONA Towers sales team.",
            )
        if enquiry.enquiry_type == EnquiryType.enquire_about_residence:
            return (
                "Explore available ONA Towers residences",
                "View available residences",
                "We have received your residence enquiry and shared it with the ONA Towers sales team.",
            )
        return (
            "We received your ONA Towers enquiry",
            "Explore ONA Towers residences",
            "We have received your enquiry and shared it with the ONA Towers sales team.",
        )
