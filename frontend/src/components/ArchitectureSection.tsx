import { projectImages } from "../data/images";
import "../styles/ona-redesign.css";

const storyDetails = [
  "Two sculptural residential towers",
  "ONA House woven into the everyday address",
  "Landscape connecting arrival, life and movement",
  "Homes shaped by light, terraces and outward views",
];

export default function ArchitectureSection() {
  return (
    <section className="ona-story-place">
      <div className="ona-section-shell">
        <header className="ona-story-place-heading">
          <p className="ona-story-overline">From idea to place</p>
          <span className="ona-story-rule" aria-hidden="true" />
          <p className="ona-story-script">The story becomes physical</p>
        </header>

        <div className="ona-story-place-grid">
          <div className="ona-story-place-intro">
            <h2>
              One vision.
              <br />
              <em>Three expressions.</em>
            </h2>

            <p>
              Home, landscape and work each have their own character, but every
              part of ONA is designed to feel like one complete address — refined,
              welcoming and unmistakably rooted in Zanzibar.
            </p>

            <div className="ona-story-place-main-image">
              <img
                src={projectImages.hero}
                alt="Sunset aerial view of ONA Towers in Zanzibar"
                loading="lazy"
              />
            </div>
          </div>

          <div className="ona-story-place-copy">
            <span className="ona-story-place-kicker">
              Architecture · Landscape · Life
            </span>

            <h3>A presence shaped by the way island life unfolds.</h3>

            <p>
              Sculptural architecture, generous terraces, natural shade and
              garden-led spaces give ONA its identity — open to the horizon,
              yet grounded in the rhythm of everyday life.
            </p>

            <div className="ona-story-place-details">
              {storyDetails.map((detail) => (
                <p key={detail}>
                  <span aria-hidden="true">✓</span>
                  {detail}
                </p>
              ))}
            </div>
          </div>

          <aside className="ona-story-perspective-card">
            <div className="ona-story-perspective-image">
              <img
                src={projectImages.development.gardens}
                alt="Outdoor work garden and landscaped social space at ONA Towers"
                loading="lazy"
              />
            </div>

            <div className="ona-story-perspective-copy">
              <span>The perspective</span>
              <h3>
                Open to the horizon.
                <br />
                Rooted in everyday life.
              </h3>
              <p>
                From skyline views to shaded outdoor work gardens, ONA balances
                premium outlooks with a sense of ease — contemporary in ambition,
                distinctly Zanzibar in character.
              </p>
            </div>
          </aside>
        </div>
      </div>
    </section>
  );
}
