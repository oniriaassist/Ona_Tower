import { projectImages } from "../data/images";
import "../styles/ona-redesign.css";

export default function InteriorsStory() {
  return (
    <section className="ona-interiors">
      <div className="ona-section-shell">
        <header className="ona-interiors-heading">
          <div>
            <p className="ona-eyebrow">Interiors</p>
            <p className="ona-script-label">Space, light & horizon</p>
          </div>

          <h2>
            ABOVE
            <br />
            <span>ORDINARY.</span>
          </h2>

          <p className="ona-interiors-lead">
            Generous proportions, natural light and effortless indoor–outdoor
            living shape interiors that feel calm, refined and deeply connected
            to Zanzibar.
          </p>
        </header>

        <div className="ona-interiors-feature">
          <img
            src={projectImages.residences.twoBedroomLiving}
            alt="ONA Towers residence living area"
            loading="lazy"
          />

          <div className="ona-interiors-feature-caption">
            <span>01 · Living</span>
            <h3>Views become part of the home.</h3>
            <p>
              Generous glazing and private terraces bring ocean light, changing
              skies and a stronger sense of openness into everyday living.
            </p>
          </div>
        </div>

        <div className="ona-interiors-grid">
          <article className="ona-interiors-story-card">
            <div className="ona-interiors-story-image">
              <img
                src={projectImages.residences.kitchenDining}
                alt="ONA Towers kitchen and dining interior"
                loading="lazy"
              />
            </div>
            <span>02 · Entertain</span>
            <h3>Made for everyday life and memorable gatherings.</h3>
            <p>
              Living, dining and kitchen spaces are arranged as generous social
              environments with an easy relationship to outdoor terraces.
            </p>
          </article>

          <article className="ona-interiors-story-card ona-interiors-story-card--offset">
            <div className="ona-interiors-story-image">
              <img
                src={projectImages.residences.threeBedroomBedroom}
                alt="ONA Towers private bedroom retreat"
                loading="lazy"
              />
            </div>
            <span>03 · Retreat</span>
            <h3>Private rooms made to restore.</h3>
            <p>
              Bedrooms are conceived as warm, quiet retreats — shaped by soft
              light, considered proportions and a calmer material character.
            </p>
          </article>
        </div>

        <div className="ona-interiors-closing">
          <p>Every detail is intentional.</p>
          <strong>Every view becomes part of the home.</strong>
        </div>
      </div>
    </section>
  );
}
