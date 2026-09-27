import { SiteLink } from "../routing";
import { projectImages } from "../data/images";
import { projectFacts } from "../data/projectFacts";
import "../styles/ona-redesign.css";

export default function Hero() {
  return (
    <section className="ona-home-hero">
      <div className="ona-home-hero-media">
        <img
          src={projectImages.hero}
          alt="ONA Towers and ONA House rising above Mazizini, Zanzibar"
        />
      </div>

      <div className="ona-home-hero-overlay" />

      <div className="ona-home-hero-content">
        <div className="ona-home-hero-copy">
          <p className="ona-home-hero-location">
            MAZIZINI <span>·</span> ZANZIBAR
          </p>

          <h1
            className="ona-home-hero-storyline"
            aria-label="Live above. See beyond."
          >
            <span className="ona-home-hero-storyline-main">LIVE ABOVE.</span>
            <span className="ona-home-hero-storyline-accent">SEE BEYOND.</span>
          </h1>

          <div className="ona-home-hero-actions">
            <SiteLink
              to="/development"
              className="ona-button ona-button--sand"
            >
              <span>Explore ONA</span>
              <span aria-hidden="true">→</span>
            </SiteLink>

            <SiteLink
              to="/residences"
              className="ona-button ona-button--glass"
            >
              <span>View residences</span>
              <span aria-hidden="true">→</span>
            </SiteLink>
          </div>
        </div>
      </div>

      <span className="sr-only">
        {projectFacts.tagline}
      </span>
    </section>
  );
}