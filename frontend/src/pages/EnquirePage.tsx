import { FormEvent, useState } from "react";
import { Building2, Globe2, Mail, MapPin, Phone } from "lucide-react";
import PhoneInput from "react-phone-input-2";
import "react-phone-input-2/lib/style.css";

import { submitEnquiry, type EnquiryType } from "../api/enquiries";
import { projectImages } from "../data/images";
import "../styles/ona-redesign.css";

type ResidenceInterest =
  | ""
  | "02 Bedroom Residence"
  | "03 Bedroom Residence"
  | "03 Bedroom Signature Penthouse"
  | "04 Bedroom Signature Penthouse";

export default function EnquirePage() {
  const [fullName, setFullName] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [residenceInterest, setResidenceInterest] =
    useState<ResidenceInterest>("");
  const [enquiryType, setEnquiryType] = useState<EnquiryType>("general");
  const [message, setMessage] = useState("");
  const [consent, setConsent] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [notice, setNotice] = useState("");
  const [noticeType, setNoticeType] = useState<"success" | "error" | "">("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setNotice("");
    setNoticeType("");

    if (!consent) {
      setNotice(
        "Please confirm that your details may be used to respond to your enquiry.",
      );
      setNoticeType("error");
      return;
    }

    try {
      setSubmitting(true);

      const result = await submitEnquiry({
        name: fullName.trim(),
        phone,
        email: email.trim() || undefined,
        residence_interest: residenceInterest || undefined,
        enquiry_type: enquiryType,
        message: message.trim() || undefined,
        consent,
        source: "website",
        company_website: "",
      });

      setNotice(
        result.reference_number
          ? `Thank you. Your enquiry has been received. Reference: ${result.reference_number}`
          : "Thank you. Your enquiry has been received by the ONA Towers team.",
      );
      setNoticeType("success");

      setFullName("");
      setPhone("");
      setEmail("");
      setResidenceInterest("");
      setEnquiryType("general");
      setMessage("");
      setConsent(false);
    } catch (error) {
      setNotice(
        error instanceof Error
          ? error.message
          : "Something went wrong. Please try again.",
      );
      setNoticeType("error");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="ona-contact3-page">
      <section className="ona-contact3-hero">
        <img
          className="ona-contact3-background"
          src={projectImages.residences.threeBedroomLiving}
          alt="ONA Towers residence overlooking Zanzibar"
        />
        <div className="ona-contact3-overlay" />

        <div className="ona-section-shell ona-contact3-layout">
          <div className="ona-contact3-brand">
            <span className="ona-contact3-kicker">CONTACT</span>

            <h1>
              Live above.
              <br />
              <em>See beyond.</em>
            </h1>

            <p className="ona-contact3-brand-copy">
              A private residential collection in Mazizini, Zanzibar — shaped
              by light, generous terraces and elevated outlooks. Register your
              interest to receive residence information, official floor-plan
              material and a direct response from the ONA Towers team.
            </p>

            <div
              className="ona-contact3-facts"
              aria-label="ONA Towers collection"
            >
              <div>
                <small>Collection</small>
                <strong>2–3 BR + Penthouses</strong>
              </div>

              <div>
                <small>Address</small>
                <strong>Mazizini · Zanzibar</strong>
              </div>
            </div>

            <div
              className="ona-contact3-company"
              aria-label="ONIRIA Investments contact details"
            >

              <div className="ona-contact3-company-grid">
                <a
                  className="ona-contact3-company-link"
                  href="mailto:oniriaassist@gmail.com"
                >
                  <span
                    className="ona-contact3-company-link-icon"
                    aria-hidden="true"
                  >
                    <Mail size={16} strokeWidth={1.6} />
                  </span>

                  <span>
                    <small>Email</small>
                    <strong>oniriaassist@gmail.com</strong>
                  </span>
                </a>

                <a
                  className="ona-contact3-company-link"
                  href="tel:+255705321121"
                >
                  <span
                    className="ona-contact3-company-link-icon"
                    aria-hidden="true"
                  >
                    <Phone size={16} strokeWidth={1.6} />
                  </span>

                  <span>
                    <small>Phone</small>
                    <strong>+255 705 321 121</strong>
                  </span>
                </a>

              </div>
            </div>
          </div>

          <div className="ona-contact3-panel">
            <form className="ona-contact3-form" onSubmit={handleSubmit}>
              <div className="ona-contact3-field">
                <label htmlFor="fullName">Full name *</label>
                <input
                  id="fullName"
                  value={fullName}
                  onChange={(event) => setFullName(event.target.value)}
                  autoComplete="name"
                  required
                  placeholder="Your full name"
                />
              </div>

              <div className="ona-contact3-field">
                <label htmlFor="email">Email address *</label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  autoComplete="email"
                  required
                  placeholder="name@example.com"
                />
              </div>

              <div className="ona-contact3-field ona-contact3-field--full">
                <label htmlFor="phone">Phone / WhatsApp *</label>
                <PhoneInput
                  country="tz"
                  value={phone}
                  onChange={setPhone}
                  enableSearch
                  countryCodeEditable={false}
                  specialLabel=""
                  inputProps={{
                    id: "phone",
                    name: "phone",
                    required: true,
                    autoComplete: "tel",
                  }}
                  placeholder="Enter phone number"
                />
              </div>

              <div className="ona-contact3-field">
                <label htmlFor="residenceInterest">Residence interest</label>
                <select
                  id="residenceInterest"
                  value={residenceInterest}
                  onChange={(event) =>
                    setResidenceInterest(event.target.value as ResidenceInterest)
                  }
                >
                  <option value="">Select residence</option>
                  <option value="02 Bedroom Residence">
                    02 Bedroom Residence
                  </option>
                  <option value="03 Bedroom Residence">
                    03 Bedroom Residence
                  </option>
                  <option value="03 Bedroom Signature Penthouse">
                    03 Bedroom Signature Penthouse
                  </option>
                  <option value="04 Bedroom Signature Penthouse">
                    04 Bedroom Signature Penthouse
                  </option>
                </select>
              </div>

              <div className="ona-contact3-field">
                <label htmlFor="enquiryType">I would like to</label>
                <select
                  id="enquiryType"
                  value={enquiryType}
                  onChange={(event) =>
                    setEnquiryType(event.target.value as EnquiryType)
                  }
                >
                  <option value="general">Make a general enquiry</option>
                  <option value="enquire_about_residence">
                    Enquire about a residence
                  </option>
                  <option value="request_floor_plans">
                    Request floor plans
                  </option>
                  <option value="schedule_viewing">Schedule a viewing</option>
                  <option value="talk_to_sales">Talk to sales</option>
                </select>
              </div>

              <div className="ona-contact3-field ona-contact3-field--full">
                <label htmlFor="message">Message</label>
                <textarea
                  id="message"
                  rows={4}
                  value={message}
                  onChange={(event) => setMessage(event.target.value)}
                  placeholder="Tell us what you would like to know."
                />
              </div>

              <label className="ona-contact3-consent">
                <input
                  type="checkbox"
                  checked={consent}
                  onChange={(event) => setConsent(event.target.checked)}
                />
                <span>
                  I agree that my details may be used to respond to this enquiry.
                </span>
              </label>

              <div className="ona-contact3-submit-row">
                <button type="submit" disabled={submitting}>
                  {submitting ? "Sending..." : "SUBMIT ENQUIRY"}
                  <span aria-hidden="true">→</span>
                </button>
              </div>

              {notice && (
                <p
                  className={`ona-contact3-notice${
                    noticeType ? ` ona-contact3-notice--${noticeType}` : ""
                  }`}
                  role="status"
                >
                  {notice}
                </p>
              )}
            </form>
          </div>
        </div>
      </section>
    </main>
  );
}
