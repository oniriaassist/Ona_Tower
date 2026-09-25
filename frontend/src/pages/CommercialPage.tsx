import { projectImages } from "../data/images";
import { SiteLink } from "../routing";
import "../styles/ona-redesign.css";

const commercialFeatures = [
  "Flexible office suites",
  "Reception & waiting lounge",
  "Boardroom",
  "Shared lounge",
  "Kitchen & services",
];

export default function CommercialPage() {
  return (
    <main className="ona-page ona-commercial-page">
      <section className="ona-commercial-hero">
        <div className="ona-section-shell ona-commercial-hero-grid">
          <div className="ona-commercial-hero-copy">
            <span className="ona-kicker">ONA House</span>
            <span className="ona-subkicker">Work. Meet. Connect.</span>

            <h1>
              Work
              <span> at ONA.</span>
            </h1>

            <p>
              A contemporary commercial address designed for flexible work,
              meetings, everyday services and convenience within ONA.
            </p>
          </div>

          <div className="ona-commercial-hero-image">
            <img
              src={projectImages.commercial.onaHouseExterior}
              alt="ONA House exterior and commercial arrival"
            />
          </div>
        </div>
      </section>

      <section className="ona-commercial-office-section">
        <div className="ona-section-shell ona-commercial-office-grid">
          <div className="ona-commercial-office-image">
            <img
              src={projectImages.commercial.workspacePremium}
              alt="ONA House premium workspace and meeting environment"
            />
          </div>

          <div className="ona-commercial-office-copy">
            <span className="ona-kicker">Office level</span>

            <h2>
              Space made for
              <span> productive work.</span>
            </h2>

            <p>
              Flexible office suites are supported by reception, waiting,
              lounge, meeting, boardroom and service spaces — creating a more
              composed and connected work environment.
            </p>

            <div className="ona-feature-list">
              {commercialFeatures.map((feature) => (
                <span key={feature}>{feature}</span>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="ona-commercial-convenience-section">
        <div className="ona-section-shell ona-commercial-convenience-grid">
          <div className="ona-commercial-convenience-copy">
            <span className="ona-kicker">Everyday convenience</span>

            <h2>
              Services
              <span> close to home.</span>
            </h2>

            <p>
              Ground-floor retail and convenience functions support residents,
              visitors and the wider ONA community — bringing useful daily
              services into one connected address.
            </p>

            <SiteLink to="/enquire" className="ona-text-link">
              Enquire about ONA House <span>→</span>
            </SiteLink>
          </div>

          <div className="ona-commercial-convenience-image">
            <img
              src="/ona-assets/lifestyle/mini-market.webp"
              alt="ONA House everyday convenience"
            />
          </div>
        </div>
      </section>
    </main>
  );
}