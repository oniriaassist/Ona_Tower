import { projectImages } from "../../data/images";
import { SiteLink } from "../../routing";
import "../../styles/ona-redesign.css";

type ShowcaseCard = {
  title: string;
  description: string;
  action: string;
  path: string;
  image: string;
};

const showcaseCards: ShowcaseCard[] = [
  {
    title: "Residences",
    description:
      "Two- and three-bedroom residences, crowned by signature oceanfront penthouses.",
    action: "Discover Homes",
    path: "/residences",
    image: projectImages.residences.threeBedroomLiving,
  },
  {
    title: "Life & Community",
    description:
      "Landscape, wellbeing, social spaces and everyday convenience create more room to live well.",
    action: "Explore Life",
    path: "/lifestyle",
    image: projectImages.development.gardens,
  },
  {
    title: "ONA House",
    description:
      "Contemporary workspaces, meeting facilities and useful services within one connected address.",
    action: "View Workspaces",
    path: "/commercial",
    image: projectImages.commercial.onaHouseExterior,
  },
];

export default function HomeNextSteps() {
  return (
    <section
      className="ona-home-showcase"
      aria-label="Explore ONA Towers"
    >
      <div className="ona-section-shell">
        <div className="ona-home-showcase-intro">
          <span className="ona-home-showcase-kicker">Explore</span>

          <h2 className="ona-home-showcase-title">
            Two towers. Two perspectives.
            <br />
            One unmistakable presence.
          </h2>

          <p className="ona-home-showcase-copy">
            Rising above Mazizini, ONA is shaped by light, ocean and horizon.
            Two sculptural residential towers come together with ONA House and
            a landscape designed around elevated living in Zanzibar.
          </p>
        </div>

        <div className="ona-home-showcase-grid">
          {showcaseCards.map((card) => (
            <SiteLink
              key={card.title}
              to={card.path}
              className="ona-home-showcase-card"
              style={{
                backgroundImage: `
                  linear-gradient(
                    180deg,
                    rgba(20, 17, 15, 0.02) 0%,
                    rgba(20, 17, 15, 0.08) 42%,
                    rgba(20, 17, 15, 0.82) 100%
                  ),
                  url("${card.image}")
                `,
              }}
            >
              <div className="ona-home-showcase-card-content">
                <h3>{card.title}</h3>
                <p>{card.description}</p>

                <span className="ona-home-showcase-card-action">
                  {card.action}
                  <span aria-hidden="true">→</span>
                </span>
              </div>
            </SiteLink>
          ))}
        </div>
      </div>

      <section
        className="ona-home-sales-finale"
        aria-label="ONA Towers private sales"
      >
        <img
          className="ona-home-sales-finale-image"
          src={projectImages.heroOceanView}
          alt="ONA Towers elevated ocean-view living"
          loading="lazy"
        />

        <div className="ona-home-sales-finale-overlay" />

        <div className="ona-section-shell ona-home-sales-finale-inner">
          <div className="ona-home-sales-finale-copy">
            <span>Private sales · ONA Towers</span>

            <h2>
              Find your place
              <br />
              <em>above Zanzibar.</em>
            </h2>

            <p>
              Explore the residence collection, review official floor-plan
              material and speak directly with the ONA Towers team about
              current availability.
            </p>

            <div className="ona-home-sales-finale-facts">
              <span>2–3 Bedroom residences</span>
              <span>Signature penthouses</span>
              <span>Mazizini · Zanzibar</span>
            </div>

            <div className="ona-home-sales-finale-actions">
              <SiteLink
                to="/residences"
                className="ona-home-sales-finale-button ona-home-sales-finale-button--primary"
              >
                Explore residences <span aria-hidden="true">→</span>
              </SiteLink>

              <SiteLink
                to="/enquire"
                className="ona-home-sales-finale-button ona-home-sales-finale-button--secondary"
              >
                Register interest
              </SiteLink>
            </div>
          </div>
        </div>
      </section>
    </section>
  );
}
