import { projectImages } from "../data/images";
import { SiteLink } from "../routing";
import "../styles/ona-redesign.css";

const experiences = [
  {
    label: "LIVE",
    title: "Residences",
    description:
      "Two- and three-bedroom homes shaped by natural light, generous terraces and elevated views across Zanzibar.",
    image: projectImages.residences.twoBedroomLiving,
    alt: "ONA Towers residence living interior",
    to: "#residence-portfolio",
    anchor: true,
    cta: "Explore residences",
  },
  {
    label: "LIFE",
    title: "Life & Community",
    description:
      "Landscape, social spaces and everyday convenience create more room to live well beyond the front door.",
    image: projectImages.amenities.pool,
    alt: "ONA Towers pool and community lifestyle",
    to: "/lifestyle",
    anchor: false,
    cta: "Explore life",
  },
  {
    label: "WORK",
    title: "ONA House",
    description:
      "A contemporary commercial address bringing work, meetings and useful services into one connected development.",
    image: projectImages.commercial.boardroom,
    alt: "ONA House contemporary boardroom",
    to: "/commercial",
    anchor: false,
    cta: "Discover ONA House",
  },
];

export default function ResidencesIntro() {
  return (
    <>
      <section className="ona-residences-hero">
        <img
          className="ona-residences-hero-image"
          src={projectImages.residences.exterior}
          alt="ONA Towers residential architecture"
        />
        <div className="ona-residences-hero-overlay" />

        <div className="ona-section-shell ona-residences-hero-inner">
          <div className="ona-residences-hero-copy">
            <p className="ona-eyebrow">Discover ONA</p>
            <p className="ona-script-label">Live above. See beyond.</p>

            <h1>
              A home shaped around
              <br />
              <em>light, space & horizon.</em>
            </h1>

            <p>
              ONA brings residence, landscape, community and everyday
              convenience together in one considered address in Mazizini — with
              generous homes designed to feel open, calm and connected to
              Zanzibar.
            </p>

            <div className="ona-residences-hero-actions">
              <a href="#residence-portfolio" className="ona-button ona-button--sand">
                Choose your residence <span aria-hidden="true">↓</span>
              </a>
              <SiteLink to="/enquire" className="ona-button ona-button--glass">
                Register interest <span aria-hidden="true">→</span>
              </SiteLink>
            </div>
          </div>
        </div>
      </section>

      <section className="ona-residences-world">
        <div className="ona-section-shell">
          <header className="ona-residences-world-heading">
            <p className="ona-eyebrow">One connected address</p>
            <h2>
              Home is only the
              <br />
              <em>beginning.</em>
            </h2>
            <p>
              Three expressions of ONA bring together how you live, how you
              spend your time and how the wider address works around you.
            </p>
          </header>

          <div className="ona-residences-world-grid">
            {experiences.map((item) => {
              const content = (
                <>
                  <img src={item.image} alt={item.alt} loading="lazy" />
                  <div className="ona-residences-world-overlay" />
                  <span className="ona-residences-world-label">{item.label}</span>
                  <div className="ona-residences-world-content">
                    <h3>{item.title}</h3>
                    <p>{item.description}</p>
                    <span className="ona-text-link">
                      {item.cta} <span aria-hidden="true">↗</span>
                    </span>
                  </div>
                </>
              );

              return item.anchor ? (
                <a key={item.label} href={item.to} className="ona-residences-world-card">
                  {content}
                </a>
              ) : (
                <SiteLink key={item.label} to={item.to} className="ona-residences-world-card">
                  {content}
                </SiteLink>
              );
            })}
          </div>
        </div>
      </section>
    </>
  );
}
