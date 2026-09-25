import { projectImages } from "../data/images";
import "../styles/ona-redesign.css";

const storyPillars = [
  {
    label: "Origin",
    title: "Born from Zanzibar",
    text: "A contemporary address shaped by the island's light, climate, horizon and evolving urban rhythm.",
    mark: "✦",
  },
  {
    label: "Mission",
    title: "Elevate everyday living",
    text: "Thoughtful homes, meaningful amenities and a calmer, more connected way to live.",
    mark: "◌",
  },
  {
    label: "Promise",
    title: "Create lasting presence",
    text: "A complete address designed to feel relevant, desirable and enduring well beyond launch.",
    mark: "≈",
  },
];

export default function OnaIdea() {
  return (
    <>
      <section className="ona-story-hero">
        <div className="ona-story-hero-media" aria-hidden="true">
          <img src={projectImages.heroOceanView} alt="" />
        </div>

        <div className="ona-story-hero-fade" aria-hidden="true" />

        <div className="ona-section-shell ona-story-hero-inner">
          <div className="ona-story-hero-copy">
            <p className="ona-story-overline">Our Story</p>
            <span className="ona-story-rule" aria-hidden="true" />

            <p className="ona-story-script">Live above. See beyond.</p>

            <h1>
              A new address for
              <br />
              Zanzibar&apos;s next chapter.
            </h1>

            <p className="ona-story-hero-lead">
              ONA Towers is shaped by a simple ambition: create a contemporary
              address for Zanzibar that feels elevated, connected and
              unmistakably of its place. In Mazizini, two sculptural residential
              towers, ONA House and a landscaped heart come together around
              light, horizon and everyday life.
            </p>

            <a href="#origin" className="ona-story-gold-button">
              Discover the story <span aria-hidden="true">↓</span>
            </a>

            <div className="ona-story-hero-meta" aria-label="Project summary">
              <span>Mazizini · Zanzibar</span>
              <span>Two towers · ONA House · One address</span>
            </div>
          </div>
        </div>
      </section>

      <section className="ona-story-origin" id="origin">
        <div className="ona-section-shell ona-story-origin-layout">
          <div className="ona-story-origin-copy">
            <p className="ona-story-overline">The beginning</p>
            <span className="ona-story-rule" aria-hidden="true" />

            <p className="ona-story-script">Why ONA began</p>

            <h2>
              Start with place.
              <br />
              <em>Design for what comes next.</em>
            </h2>

            <p>
              ONA began with one question: how can a new residential landmark
              add to Zanzibar while creating a more elevated way to live? The
              answer became more than a building — a complete address where
              arrival, home, landscape, wellbeing and work are designed as one
              considered experience.
            </p>
          </div>

          <div className="ona-story-origin-cards">
            {storyPillars.map((pillar) => (
              <article className="ona-story-origin-card" key={pillar.label}>
                <span className="ona-story-origin-mark" aria-hidden="true">
                  {pillar.mark}
                </span>
                <span className="ona-story-origin-label">{pillar.label}</span>
                <h3>{pillar.title}</h3>
                <span className="ona-story-card-rule" aria-hidden="true" />
                <p>{pillar.text}</p>
              </article>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
