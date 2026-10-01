# ONA Towers transactional email

The enquiry endpoint stores the buyer lead first, then attempts two independent emails:

1. Customer acknowledgement containing `https://www.onatowers.com/cityview`.
2. Internal sales notification.

Email failure never removes the saved enquiry.

## Recommended production configuration (Vercel + Resend)

Set these in Vercel Project Settings -> Environment Variables for Production:

```env
EMAIL_ENABLED=true
EMAIL_PROVIDER=resend
RESEND_API_KEY=re_your_real_key
RESEND_API_URL=https://api.resend.com/emails
EMAIL_TIMEOUT_SECONDS=12
SMTP_FROM_EMAIL=sales@onatowers.com
SMTP_FROM_NAME=ONA Towers
SALES_NOTIFICATION_EMAIL=onatowers@proton.me
CITYVIEW_URL=https://www.onatowers.com/cityview
```

The `onatowers.com` domain must be verified in Resend before sending from
`sales@onatowers.com`. Never commit the real API key.

## SMTP fallback

If required, use:

```env
EMAIL_ENABLED=true
EMAIL_PROVIDER=smtp
SMTP_ENABLED=true
SMTP_HOST=smtp.resend.com
SMTP_PORT=587
SMTP_USERNAME=resend
SMTP_PASSWORD=re_your_real_key
SMTP_FROM_EMAIL=sales@onatowers.com
SMTP_FROM_NAME=ONA Towers
SMTP_USE_TLS=true
SALES_NOTIFICATION_EMAIL=onatowers@proton.me
CITYVIEW_URL=https://www.onatowers.com/cityview
```

## Production verification

After redeploying:

- Open `/admin/settings` and choose **Email**.
- Confirm **Email delivery is ready**.
- Send a test email to an address you control.
- Submit the public enquiry form with the same address.
- The API response now indicates whether the customer and staff emails were accepted for delivery.
- `/api/health/config` reports non-secret readiness flags under `email`.

If a test email is rejected by Resend, the admin test endpoint returns the provider error while keeping API keys secret.
