import { Facebook, Instagram, Linkedin } from "lucide-react";
import { SiteLink } from "../routing";
import "../styles/ona-redesign.css";

function WhatsAppIcon({ size = 17 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="currentColor"
      aria-hidden="true"
    >
      <path d="M19.11 17.2c-.29-.15-1.72-.85-1.99-.95-.27-.1-.47-.15-.67.15-.2.29-.77.95-.94 1.15-.17.2-.35.22-.64.07-.29-.15-1.24-.46-2.36-1.46-.87-.78-1.46-1.74-1.63-2.03-.17-.29-.02-.45.13-.6.13-.13.29-.35.44-.52.15-.17.2-.29.29-.49.1-.2.05-.37-.02-.52-.07-.15-.67-1.61-.91-2.2-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.79.37-.27.29-1.04 1.02-1.04 2.49s1.07 2.89 1.22 3.09c.15.2 2.1 3.21 5.09 4.5.71.31 1.27.49 1.7.63.71.23 1.36.19 1.87.12.57-.08 1.72-.7 1.96-1.38.24-.68.24-1.26.17-1.38-.07-.12-.27-.2-.57-.35Z" />
      <path d="M16.03 3C8.84 3 3 8.73 3 15.8c0 2.49.74 4.91 2.14 6.98L3 29l6.42-2.08a13.18 13.18 0 0 0 6.6 1.79h.01C23.21 28.71 29 22.98 29 15.9 29 8.82 23.21 3 16.03 3Zm0 23.55h-.01a11 11 0 0 1-5.61-1.53l-.4-.24-3.81 1.23 1.26-3.69-.26-.41a10.55 10.55 0 0 1-1.71-5.77c0-5.93 4.72-10.75 10.54-10.75 5.82 0 10.53 4.82 10.53 10.75 0 5.93-4.71 10.41-10.53 10.41Z" />
    </svg>
  );
}

const socialLinks = [
  {
    label: "WhatsApp",
    href: "https://wa.me/",
    icon: WhatsAppIcon,
  },
  {
    label: "Instagram",
    href: "https://www.instagram.com/",
    icon: Instagram,
  },
  {
    label: "LinkedIn",
    href: "https://www.linkedin.com/",
    icon: Linkedin,
  },
  {
    label: "Facebook",
    href: "https://www.facebook.com/",
    icon: Facebook,
  },
];

export default function Footer() {
  return (
    <footer className="ona-footer">
      <div className="ona-section-shell">
        <div className="ona-footer-main">
          <div className="ona-footer-brand">
            <SiteLink
              to="/"
              className="ona-footer-logo"
              aria-label="ONA Towers home"
            >
              <span>ÔNA</span>
              <small>TOWERS</small>
            </SiteLink>

            <p className="ona-footer-tagline">Live above. See beyond.</p>
          </div>

          <div className="ona-footer-center">
            <p>
              Two residential towers and ONA House rising above Mazizini, Zanzibar.
            </p>
          </div>

          <div className="ona-footer-meta">
            <strong>ONA Towers Limited</strong>
            <p>Mazizini, Zanzibar, Tanzania</p>
            <p>Tower A · ONA House · Tower B</p>

            <SiteLink to="/enquire" className="ona-footer-register">
              <span>Register interest</span>
              <span className="ona-footer-register-arrow" aria-hidden="true">
                →
              </span>
            </SiteLink>

            <div
              className="ona-footer-socials"
              aria-label="ONA Towers social media"
            >
              {socialLinks.map(({ label, href, icon: Icon }) => (
                <a
                  key={label}
                  href={href}
                  className="ona-footer-social-link"
                  target="_blank"
                  rel="noreferrer"
                  aria-label={label}
                  title={label}
                >
                  <Icon size={17} />
                </a>
              ))}
            </div>
          </div>
        </div>

        <div className="ona-footer-bottom">
          <p>&copy; {new Date().getFullYear()} ONA Towers. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
