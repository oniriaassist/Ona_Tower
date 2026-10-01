from __future__ import annotations

from dataclasses import dataclass
import html
import logging
import smtplib
import ssl
from email.message import EmailMessage

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
        subject, cta_label, intro = self._customer_email_copy(enquiry)

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
                    "",
                    f"Enquiry reference: {enquiry.reference_number}",
                    "",
                    "Explore ONA Towers residences, current availability, towers, floors and floor plans:",
                    cityview_url,
                    "",
                    "A member of the ONA Towers sales team can assist you with residence selection, availability, reservations and private viewing arrangements.",
                    "",
                    "Warm regards,",
                    "ONA Towers",
                    "Zanzibar, Tanzania",
                    "Live above. See beyond.",
                ]
            )
        )

        customer_name = html.escape(enquiry.name)
        reference = html.escape(enquiry.reference_number)
        safe_intro = html.escape(intro)
        safe_url = html.escape(cityview_url, quote=True)
        safe_cta = html.escape(cta_label)

        msg.add_alternative(
            f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(subject)}</title>
</head>
<body style="margin:0;padding:0;background:#f4efe7;font-family:Arial,Helvetica,sans-serif;color:#302a26;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="width:100%;background:#f4efe7;margin:0;padding:0;">
    <tr>
      <td align="center" style="padding:32px 14px;">
        <table role="presentation" width="620" cellspacing="0" cellpadding="0" border="0" style="width:100%;max-width:620px;background:#fffdf9;border:1px solid #e8dfd4;border-radius:8px;overflow:hidden;">
          <tr>
            <td align="center" style="padding:30px 36px;background:#24333d;">
              <div style="font-family:Georgia,'Times New Roman',serif;color:#ffffff;font-size:34px;letter-spacing:7px;line-height:1;">ÔNA</div>
              <div style="margin-top:8px;color:#c7a373;font-size:10px;font-weight:700;letter-spacing:5px;line-height:1;">TOWERS</div>
            </td>
          </tr>
          <tr>
            <td style="padding:40px 42px 34px;">
              <div style="margin:0 0 13px;color:#a17b52;font-size:10px;font-weight:700;letter-spacing:2.7px;text-transform:uppercase;">Luxury Residences · Zanzibar</div>
              <h1 style="margin:0 0 20px;font-family:Georgia,'Times New Roman',serif;color:#2c2824;font-size:32px;font-weight:400;line-height:1.22;">Thank you for your interest in ONA Towers.</h1>
              <p style="margin:0 0 16px;color:#665f58;font-size:15px;line-height:1.7;">Dear {customer_name},</p>
              <p style="margin:0 0 16px;color:#665f58;font-size:15px;line-height:1.7;">{safe_intro}</p>
              <p style="margin:0 0 28px;color:#665f58;font-size:15px;line-height:1.7;">You can now explore the ONA Towers residence collection, check current availability, compare towers and floors, and view available floor plans.</p>

              <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin:0 0 30px;">
                <tr>
                  <td style="border-radius:4px;background:#ad8759;">
                    <a href="{safe_url}" style="display:inline-block;padding:16px 26px;color:#ffffff;text-decoration:none;font-size:11px;font-weight:700;letter-spacing:1.7px;text-transform:uppercase;">{safe_cta} &nbsp;→</a>
                  </td>
                </tr>
              </table>

              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="width:100%;border-top:1px solid #eadfd3;border-bottom:1px solid #eadfd3;">
                <tr>
                  <td style="padding:17px 0;">
                    <div style="color:#9a8d80;font-size:10px;font-weight:700;letter-spacing:1.6px;text-transform:uppercase;">Enquiry reference</div>
                    <div style="margin-top:6px;color:#302a26;font-size:14px;font-weight:700;">{reference}</div>
                  </td>
                </tr>
              </table>

              <p style="margin:26px 0 0;color:#756d65;font-size:13px;line-height:1.7;">A member of the ONA Towers sales team can assist you with residence selection, availability, reservations and private viewing arrangements.</p>
            </td>
          </tr>
          <tr>
            <td align="center" style="padding:23px 36px;background:#f2ece4;border-top:1px solid #e8dfd4;">
              <div style="color:#6f675f;font-size:12px;line-height:1.5;">ONA Towers · Zanzibar, Tanzania</div>
              <div style="margin-top:7px;color:#9b7650;font-family:Georgia,'Times New Roman',serif;font-size:14px;font-style:italic;">Live above. See beyond.</div>
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
