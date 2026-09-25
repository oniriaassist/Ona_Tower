import { useMemo, useState } from "react";
import { projectImages } from "../data/images";
import { SiteLink } from "../routing";
import "../styles/ona-redesign.css";

type ResidenceType = "2br" | "3br" | "3br-penthouse" | "4br-penthouse";

const residenceTypes = [
  { id: "2br" as ResidenceType, label: "02 Bedroom" },
  { id: "3br" as ResidenceType, label: "03 Bedroom" },
  { id: "3br-penthouse" as ResidenceType, label: "03 BR Penthouse" },
  { id: "4br-penthouse" as ResidenceType, label: "04 BR Penthouse" },
];

const residenceContent: Record<
  ResidenceType,
  {
    area: string;
    title: string;
    description: string;
    image: string;
    internal: string;
    terrace: string;
    towers: string[];
  }
> = {
  "2br": {
    area: "202–206 sqm",
    title: "02 Bedroom Residence",
    description:
      "Generous two-bedroom residences with open living spaces, private terraces and elevated views across Zanzibar.",
    image: projectImages.residences.twoBedroomPremium,
    internal: "146 sqm",
    terrace: "56 sqm",
    towers: ["Tower A · West", "Tower A · East", "Tower B · West", "Tower B · East"],
  },
  "3br": {
    area: "241–248 sqm",
    title: "03 Bedroom Residence",
    description:
      "Three-bedroom homes shaped by flowing living areas, natural light and private terraces designed for everyday island living.",
    image: projectImages.floorPlans.towerA3West,
    internal: "173 sqm",
    terrace: "68 sqm",
    towers: ["Tower A · West", "Tower A · East", "Tower B · West", "Tower B · East"],
  },
  "3br-penthouse": {
    area: "314 sqm",
    title: "03 Bedroom Signature Penthouse",
    description:
      "A more elevated expression of ONA living with expansive interiors, entertaining terraces and a wider outlook.",
    image: projectImages.floorPlans.towerAPenthouse3,
    internal: "218 sqm",
    terrace: "96 sqm",
    towers: ["Tower A · Penthouse", "Tower B · Penthouse"],
  },
  "4br-penthouse": {
    area: "402 sqm",
    title: "04 Bedroom Signature Penthouse",
    description:
      "The most expansive residence category at ONA — designed for privacy, entertaining and life above the horizon.",
    image: projectImages.floorPlans.towerAPenthouse4,
    internal: "286 sqm",
    terrace: "116 sqm",
    towers: ["Tower A · Penthouse", "Tower B · Penthouse"],
  },
};

const discoveryCards = [
  {
    label: "LIVE",
    title: "Residences",
    description:
      "Expansive two- and three-bedroom residences shaped by natural light, generous terraces and elevated views across Zanzibar.",
    image: projectImages.residences.twoBedroomLiving,
    link: "/residences",
    cta: "Discover residences",
  },
  {
    label: "LIFE",
    title: "Life & Community",
    description:
      "Landscaped gardens, social spaces and thoughtful amenities create more room for life.",
    image: projectImages.development.landscape,
    link: "/lifestyle",
    cta: "Explore life",
  },
  {
    label: "WORK",
    title: "ONA House",
    description:
      "A contemporary commercial address bringing offices, meeting spaces and everyday services into one connected development.",
    image: projectImages.commercial.onaHouseExterior,
    link: "/commercial",
    cta: "Discover ONA House",
  },
];

const interiorStories = [
  {
    label: "Living",
    title: "Views become part of the home.",
    description:
      "Generous glazing and private terraces open everyday living to ocean light, changing skies and the natural rhythm of Zanzibar.",
    image: projectImages.residences.twoBedroomLiving,
  },
  {
    label: "Entertain",
    title: "Space for everyday life and memorable gatherings.",
    description:
      "Open living, dining and kitchen spaces are conceived as calm social environments with effortless movement toward outdoor terraces.",
    image: projectImages.residences.threeBedroomLiving,
  },
  {
    label: "Retreat",
    title: "Private rooms made to restore.",
    description:
      "Bedrooms are quiet, warm and refined — considered private retreats shaped by soft light, natural textures and calm.",
    image: projectImages.residences.threeBedroomBedroom,
  },
];

export default function ResidencesPage() {
  const [selectedType, setSelectedType] = useState<ResidenceType>("2br");
  const selectedResidence = useMemo(
    () => residenceContent[selectedType],
    [selectedType]
  );

  return (
    <main className="ona-page ona-residences-page">
      <section className="ona-res-hero">
        <div className="ona-section-shell ona-res-hero-grid">
          <div className="ona-res-hero-copy">
            <span className="ona-kicker">Residences</span>
            <span className="ona-subkicker">Designed for elevated living</span>

            <h1>
              A home shaped around
              <span> light, space & horizon.</span>
            </h1>

            <p>
              ONA residences are designed around natural light, generous
              proportions and effortless indoor–outdoor living — creating a
              calmer and more elevated way to live in Zanzibar.
            </p>
          </div>

          <div className="ona-res-hero-image">
            <img
              src={projectImages.residences.threeBedroomLiving}
              alt="ONA Towers residence interior"
            />
          </div>
        </div>
      </section>

      <section className="ona-discover-grid-section">
        <div className="ona-section-shell">
          <div className="ona-editorial-intro ona-editorial-intro--left">
            <span className="ona-kicker">Discover ONA</span>
            <h2>
              Designed around
              <span> the way life unfolds.</span>
            </h2>
            <p>
              Residence, landscape, community and everyday convenience come
              together as one considered place in Mazizini.
            </p>
          </div>

          <div className="ona-discover-grid">
            {discoveryCards.map((card) => (
              <article className="ona-discover-card" key={card.title}>
                <div className="ona-discover-card-image">
                  <img src={card.image} alt={card.title} />
                </div>

                <div className="ona-discover-card-body">
                  <span className="ona-discover-card-label">{card.label}</span>
                  <h3>{card.title}</h3>
                  <p>{card.description}</p>
                  <SiteLink to={card.link} className="ona-text-link">
                    {card.cta} <span>↗</span>
                  </SiteLink>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="ona-portfolio-section" id="residence-portfolio">
        <div className="ona-section-shell">
          <div className="ona-editorial-intro ona-editorial-intro--left">
            <span className="ona-kicker">Typology portfolio</span>
            <span className="ona-subkicker">Designed for elevated living</span>

            <h2>
              Choose your
              <span> residence.</span>
            </h2>

            <p>
              Explore the official ONA Towers residence configurations,
              orientations and floor-plan dimensions.
            </p>
          </div>

          <div className="ona-res-tabs">
            {residenceTypes.map((type) => (
              <button
                key={type.id}
                type="button"
                className={`ona-res-tab${selectedType === type.id ? " is-active" : ""}`}
                onClick={() => setSelectedType(type.id)}
              >
                {type.label}
              </button>
            ))}
          </div>

          <div className="ona-portfolio-panel">
            <div className="ona-portfolio-copy">
              <span className="ona-portfolio-area">{selectedResidence.area}</span>
              <h3>{selectedResidence.title}</h3>
              <p>{selectedResidence.description}</p>

              <div className="ona-portfolio-tags">
                {selectedResidence.towers.map((tower) => (
                  <span key={tower}>{tower}</span>
                ))}
              </div>

              <div className="ona-metric-grid">
                <div>
                  <small>Total area</small>
                  <strong>{selectedResidence.area}</strong>
                </div>
                <div>
                  <small>Internal area</small>
                  <strong>{selectedResidence.internal}</strong>
                </div>
                <div>
                  <small>Terrace / balcony</small>
                  <strong>{selectedResidence.terrace}</strong>
                </div>
              </div>

              <SiteLink to="/enquire" className="ona-text-link">
                Request Interest <span>→</span>
              </SiteLink>
            </div>

            <div className={`ona-portfolio-image${selectedType === "2br" ? " ona-portfolio-image--lifestyle" : ""}`}>
              <img
                src={selectedResidence.image}
                alt={selectedResidence.title}
              />
            </div>
          </div>
        </div>
      </section>

      <section className="ona-penthouse-section">
        <div className="ona-section-shell ona-penthouse-grid">
          <div className="ona-penthouse-copy">
            <span className="ona-kicker">Signature residences</span>

            <h2>
              Live
              <span> iconic.</span>
            </h2>

            <p>
              Crowning ONA Towers, a limited collection of signature penthouses
              represents the most elevated expression of island living.
            </p>

            <p>
              Expansive living spaces, generous private terraces and panoramic
              outlooks create residences designed for privacy, entertaining and
              life above the horizon.
            </p>

            <div className="ona-inline-meta">
              <span>Elevated living</span>
              <strong>Ocean · Horizon · Privacy</strong>
            </div>

            <SiteLink to="/enquire" className="ona-text-link">
              Enquire <span>→</span>
            </SiteLink>
          </div>

          <div className="ona-penthouse-image">
            <img
              src={projectImages.residences.penthouseLiving}
              alt="ONA Towers signature residence"
            />
          </div>
        </div>
      </section>

      <section className="ona-interiors-section">
        <div className="ona-section-shell">
          <div className="ona-editorial-intro">
            <span className="ona-kicker">Interiors</span>
            <span className="ona-subkicker">Space, light & horizon</span>

            <h2>
              Above
              <span> ordinary.</span>
            </h2>

            <p>
              ONA residences are designed around light, space and the horizon.
              Generous proportions, natural materials and effortless
              indoor–outdoor living create interiors that feel calm, refined and
              deeply connected to Zanzibar.
            </p>
          </div>

          <div className="ona-interior-grid">
            {interiorStories.map((item) => (
              <article className="ona-interior-card" key={item.label}>
                <div className="ona-interior-card-image">
                  <img src={item.image} alt={item.title} />
                </div>

                <div className="ona-interior-card-body">
                  <span className="ona-interior-label">{item.label}</span>
                  <h3>{item.title}</h3>
                  <p>{item.description}</p>
                </div>
              </article>
            ))}
          </div>

          <div className="ona-res-final-note">
            <strong>Every detail is intentional.</strong>
            <span>Every view becomes part of the home.</span>
          </div>
        </div>
      </section>
    </main>
  );
}