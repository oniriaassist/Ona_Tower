import { projectImages } from "../data/images";
import { SiteLink } from "../routing";
import "../styles/ona-redesign.css";

export function PenthousesSection() {
  return (
    <section className="ona-penthouse">
      <div className="ona-section-shell">
        <div className="ona-penthouse-heading">
          <div>
            <p className="ona-eyebrow">Signature residences</p>
            <p className="ona-script-label">The most elevated expression of ONA</p>
            <h2>
              Live
              <br />
              <em>iconic.</em>
            </h2>
          </div>

          <div className="ona-penthouse-intro">
            <p>
              Crowning the towers, a limited collection of signature penthouses
              brings together expansive interiors, generous private terraces and
              panoramic outlooks.
            </p>
            <p>
              Created for privacy, entertaining and life above the horizon, these
              residences represent ONA at its most exceptional.
            </p>

            <SiteLink to="/enquire" className="ona-inline-button">
              Enquire about signature residences <span aria-hidden="true">→</span>
            </SiteLink>
          </div>
        </div>

        <div className="ona-penthouse-image">
          <img
            src={projectImages.residences.penthouseLiving}
            alt="ONA Towers signature residence with elevated ocean outlook"
            loading="lazy"
          />

          <div className="ona-penthouse-image-copy">
            <span>Elevated living</span>
            <strong>Ocean · horizon · privacy</strong>
          </div>
        </div>
      </div>
    </section>
  );
}

export default PenthousesSection;
