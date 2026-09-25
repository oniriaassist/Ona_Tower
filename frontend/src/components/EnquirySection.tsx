import { FormEvent, useMemo, useState } from "react";

import { submitEnquiry, type EnquiryType } from "../api/enquiries";
import { projectImages } from "../data/images";
import "../styles/ona-redesign.css";

const countryCodes = [
  { value: "+255", label: "Tanzania +255" },
  { value: "+254", label: "Kenya +254" },
  { value: "+971", label: "UAE +971" },
  { value: "+966", label: "Saudi Arabia +966" },
  { value: "+974", label: "Qatar +974" },
  { value: "+968", label: "Oman +968" },
  { value: "+91", label: "India +91" },
  { value: "+44", label: "United Kingdom +44" },
  { value: "+1", label: "US / Canada +1" },
  { value: "+27", label: "South Africa +27" },
  { value: "+49", label: "Germany +49" },
  { value: "+33", label: "France +33" },
];

type EnquiryForm = {
  fullName: string;
  countryCode: string;
  phone: string;
  email: string;
  residenceInterest: string;
  enquiryType: EnquiryType;
  message: string;
  consent: boolean;
};

const initialForm: EnquiryForm = {
  fullName: "",
  countryCode: "+255",
  phone: "",
  email: "",
  residenceInterest: "",
  enquiryType: "general",
  message: "",
  consent: false,
};

function cleanPhone(value: string) {
  return value.replace(/[^\d]/g, "").replace(/^0+/, "");
}

export default function EnquirySection() {
  const [form, setForm] = useState<EnquiryForm>(initialForm);
  const [state, setState] = useState<"idle" | "submitting" | "success" | "error">("idle");
  const [feedback, setFeedback] = useState("");

  const fullPhone = useMemo(() => {
    const number = cleanPhone(form.phone);
    return number ? `${form.countryCode}${number}` : "";
  }, [form.countryCode, form.phone]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!form.consent) {
      setState("error");
      setFeedback("Please confirm that your details may be used to respond to your enquiry.");
      return;
    }

    setState("submitting");
    setFeedback("");

    try {
      const result = await submitEnquiry({
        name: form.fullName,
        phone: fullPhone,
        email: form.email || undefined,
        residence_interest: form.residenceInterest || undefined,
        enquiry_type: form.enquiryType,
        message: form.message || undefined,
        consent: form.consent,
        source: "website",
        company_website: "",
      });

      const reference = result.reference_number;
      setState("success");
      setFeedback(
        reference
          ? `Thank you. Your private enquiry has been received. Reference: ${reference}`
          : "Thank you. Your enquiry has been received by the ONA Towers team.",
      );
      setForm(initialForm);
    } catch (error) {
      setState("error");
      setFeedback(error instanceof Error ? error.message : "Unable to submit your enquiry. Please try again.");
    }
  };

  return (
    <section className="ona-enquiry">
      <div className="ona-enquiry-visual">
        <img
          src={projectImages.residences.threeBedroomLiving}
          alt="ONA Towers residence with elevated ocean outlook"
        />
        <div className="ona-enquiry-visual-overlay" />

        <div className="ona-enquiry-visual-copy">
          <p>Private sales · ONA Towers</p>
          <h2>
            Live above.
            <br />
            <em>See beyond.</em>
          </h2>
          <span>Mazizini · Zanzibar</span>

          <div className="ona-enquiry-visual-facts">
            <div>
              <small>Collection</small>
              <strong>2–3 BR + Penthouses</strong>
            </div>
            <div>
              <small>Address</small>
              <strong>Mazizini, Zanzibar</strong>
            </div>
          </div>
        </div>
      </div>

      <div className="ona-enquiry-form-wrap">
        <div className="ona-enquiry-form-inner">
          <div className="ona-enquiry-heading">
            <p className="ona-eyebrow">Private enquiry</p>
            <p className="ona-script-label">Your ONA journey starts here</p>

            <h1>
              Begin your
              <br />
              <em>ONA journey.</em>
            </h1>

            <p className="ona-enquiry-intro">
              Register your interest for residence information, floor-plan material
              and a direct conversation with the ONA Towers team.
            </p>
          </div>

          <div className="ona-enquiry-service-strip">
            <div>
              <span>01</span>
              <strong>Residence details</strong>
            </div>
            <div>
              <span>02</span>
              <strong>Floor-plan material</strong>
            </div>
            <div>
              <span>03</span>
              <strong>Sales conversation</strong>
            </div>
          </div>

          <form className="ona-enquiry-form" onSubmit={handleSubmit}>
            <div className="ona-form-field ona-form-field--full">
              <label htmlFor="fullName">Full name *</label>
              <input
                id="fullName"
                value={form.fullName}
                autoComplete="name"
                required
                placeholder="Your name"
                onChange={(event) => setForm({ ...form, fullName: event.target.value })}
              />
            </div>

            <div className="ona-form-phone">
              <div className="ona-form-field">
                <label htmlFor="countryCode">Country code *</label>
                <select
                  id="countryCode"
                  value={form.countryCode}
                  onChange={(event) => setForm({ ...form, countryCode: event.target.value })}
                >
                  {countryCodes.map((item) => (
                    <option key={item.label} value={item.value}>
                      {item.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="ona-form-field">
                <label htmlFor="phone">Phone / WhatsApp *</label>
                <input
                  id="phone"
                  type="tel"
                  required
                  autoComplete="tel-national"
                  value={form.phone}
                  placeholder="7XX XXX XXX"
                  onChange={(event) => setForm({ ...form, phone: event.target.value })}
                />
              </div>
            </div>

            <div className="ona-form-field ona-form-field--full">
              <label htmlFor="email">Email address *</label>
              <input
                id="email"
                type="email"
                required
                autoComplete="email"
                value={form.email}
                placeholder="name@example.com"
                onChange={(event) => setForm({ ...form, email: event.target.value })}
              />
            </div>

            <div className="ona-form-field ona-form-field--full">
              <label htmlFor="residence">Residence interest</label>
              <select
                id="residence"
                value={form.residenceInterest}
                onChange={(event) => setForm({ ...form, residenceInterest: event.target.value })}
              >
                <option value="">Select residence</option>
                <option value="02 Bedroom Residence">02 Bedroom Residence</option>
                <option value="03 Bedroom Residence">03 Bedroom Residence</option>
                <option value="03 Bedroom Signature Penthouse">03 Bedroom Signature Penthouse</option>
                <option value="04 Bedroom Signature Penthouse">04 Bedroom Signature Penthouse</option>
              </select>
            </div>

            <div className="ona-form-field ona-form-field--full">
              <label htmlFor="enquiryType">I would like to</label>
              <select
                id="enquiryType"
                value={form.enquiryType}
                onChange={(event) =>
                  setForm({ ...form, enquiryType: event.target.value as EnquiryType })
                }
              >
                <option value="general">Make a general enquiry</option>
                <option value="enquire_about_residence">Enquire about a residence</option>
                <option value="request_floor_plans">Request floor plans</option>
                <option value="schedule_viewing">Schedule a viewing</option>
                <option value="talk_to_sales">Talk to sales</option>
              </select>
            </div>

            <div className="ona-form-field ona-form-field--full">
              <label htmlFor="message">Message</label>
              <textarea
                id="message"
                rows={4}
                value={form.message}
                placeholder="Tell us what you would like to know."
                onChange={(event) => setForm({ ...form, message: event.target.value })}
              />
            </div>

            <label className="ona-consent">
              <input
                type="checkbox"
                checked={form.consent}
                onChange={(event) => setForm({ ...form, consent: event.target.checked })}
              />
              <span>I agree that my details may be used to respond to this enquiry.</span>
            </label>

            {feedback && (
              <div className={`ona-form-status ona-form-status--${state}`} role="status">
                {feedback}
              </div>
            )}

            <button type="submit" className="ona-enquiry-submit" disabled={state === "submitting"}>
              <span>{state === "submitting" ? "Submitting..." : "Send private enquiry"}</span>
              <span aria-hidden="true">→</span>
            </button>
          </form>

          <p className="ona-enquiry-privacy-note">
            Your details are used only to respond to your enquiry and support your
            conversation with the ONA Towers team.
          </p>
        </div>
      </div>
    </section>
  );
}
