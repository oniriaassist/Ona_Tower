"""Print a secret-safe readiness report for ONA Towers transactional email."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.core.config import get_settings
from app.services.notification import NotificationService


def main() -> int:
    get_settings.cache_clear()
    settings = get_settings()
    status = NotificationService(settings).configuration_status()

    print(f"Release: {settings.app_release}")
    print(f"Environment: {settings.app_env}")
    print(f"Email enabled: {status['enabled']}")
    print(f"Email ready: {status['ready']}")
    print(f"Provider: {status['provider']}")
    print(f"Sender domain: {status['from_domain'] or '-'}")
    print(f"Resend domain match: {status['resend_domain_match']}")
    print(f"Resend key configured: {status['resend_key_configured']}")
    print(f"Resend key source: {status['resend_key_source']}")
    print(f"Staff recipient configured: {status['staff_recipient_configured']}")
    print(f"City View URL: {status['cityview_url']}")

    issues = [str(item) for item in status["issues"]]
    if issues:
        print("Issues:")
        for issue in issues:
            print(f"  - {issue}")

    if status["ready"]:
        print("EMAIL CONFIGURATION: READY")
        return 0
    print("EMAIL CONFIGURATION: NOT READY")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
