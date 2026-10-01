import html
import logging
import smtplib
import ssl
from email.message import EmailMessage

from app.core.config import Settings
from app.schemas.enquiry import EnquiryRecord, EnquiryType

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def send_enquiry_notifications(self, enquiry: EnquiryRecord) -> None:
        """Send staff and customer email notifications without risking the enquiry.

        The enquiry is already stored before this method is called. Each email is
        therefore attempted independently: a temporary SMTP problem must never
        prevent the customer enquiry from remaining available in the admin area.
        """
        if not self.settings.smtp_enabled:
            logger.info("SMTP disabled; enquiry notifications skipped")
            return

        if not self.settings.smtp_host or not self.settings.smtp_from_email:
            logger.warning("SMTP enabled but SMTP_HOST or SMTP_FROM_EMAIL is missing")
            return

        if bool(self.settings.smtp_username) != bool(self.settings.smtp_password):
            logger.warning("SMTP authentication is incomplete; SMTP_USERNAME and SMTP_PASSWORD must be configured together")
            return

        if self.settings.sales_notification_email:
            try:
                self._send_sales_notification(enquiry)
            except Exception:
                logger.exception("Sales notification failed for enquiry %s", enquiry.reference_number)
        else:
            logger.warning(
                "SALES_NOTIFICATION_EMAIL is not configured; staff email skipped for enquiry %s",
                enquiry.reference_number,
            )

        if enquiry.email:
            try:
                self._send_customer_acknowledgement(enquiry)
            except Exception:
                logger.exception("Customer acknowledgement failed for enquiry %s", enquiry.reference_number)

    def _smtp_send(self, message: EmailMessage) -> None:
        host = self.settings.smtp_host
        if not host:
            raise RuntimeError("SMTP_HOST is not configured")

        with smtplib.SMTP(host, self.settings.smtp_port, timeout=10) as server:
            if self.settings.smtp_use_tls:
                server.starttls(context=ssl.create_default_context())
            if self.settings.smtp_username and self.settings.smtp_password:
                server.login(self.settings.smtp_username, self.settings.smtp_password)
            server.send_message(message)

    def _from_header(self) -> str:
        return f"{self.settings.smtp_from_name} <{self.settings.smtp_from_email}>"

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
                    f"City View: {self.settings.cityview_url}",
                ]
            )
        )
        self._smtp_send(msg)

    def _send_customer_acknowledgement(self, enquiry: EnquiryRecord) -> None:
        cityview_url = self.settings.cityview_url.strip() or "https://www.onatowers.com/cityview"
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

        self._smtp_send(msg)

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
