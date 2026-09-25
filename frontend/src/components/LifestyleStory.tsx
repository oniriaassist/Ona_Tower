import {
  Armchair,
  Baby,
  Bell,
  BookOpen,
  Coffee,
  Palette,
  ShoppingBag,
  Sparkles,
} from "lucide-react";

import { projectImages } from "../data/images";
import { SiteLink } from "../routing";
import "../styles/ona-redesign.css";

const amenities = [
  {
    number: "01",
    title: "Coffee & Bakery",
    image: projectImages.amenities.cafe,
    icon: Coffee,
    text: "A familiar morning ritual — coffee, fresh bakery and easy moments just steps from home.",
  },
  {
    number: "02",
    title: "Social Lounge",
    image: projectImages.amenities.socialLounge,
    icon: Armchair,
    text: "A relaxed setting for conversation, informal meetings and time shared with friends and neighbours.",
  },
  {
    number: "03",
    title: "Beauty Studio",
    image: projectImages.amenities.beautyStudio,
    icon: Sparkles,
    text: "Personal care and everyday wellbeing brought comfortably closer to home.",
  },
  {
    number: "04",
    title: "Mini Market",
    image: projectImages.amenities.miniMarket,
    icon: ShoppingBag,
    text: "Daily essentials and useful convenience integrated into the rhythm of the development.",
  },
  {
    number: "05",
    title: "Art Salon",
    image: projectImages.amenities.artSalon,
    icon: Palette,
    text: "A quieter cultural space for art, ideas, conversation and moments of discovery.",
  },
  {
    number: "06",
    title: "Study Lounge",
    image: projectImages.amenities.studyLounge,
    icon: BookOpen,
    text: "A calm place to read, focus, work or simply step away from the pace of the day.",
  },
  {
    number: "07",
    title: "Concierge",
    image: projectImages.amenities.concierge,
    icon: Bell,
    text: "A welcoming point of assistance supporting a smoother, more considered residential experience.",
  },
  {
    number: "08",
    title: "Kids’ Club",
    image: null,
    icon: Baby,
    text: "A dedicated place for younger residents to play, discover and feel part of the ONA community.",
  },
] as const;

export default function LifestyleStory() {
  return (
    <>
      <section className="ona-life-hero">
        <img
          className="ona-life-hero-image"
          src={projectImages.amenities.pool}
          alt="ONA Towers lifestyle pool and outdoor setting"
        />
        <div className="ona-life-hero-overlay" />

        <div className="ona-section-shell ona-life-hero-inner">
          <div className="ona-life-hero-copy">
            <p className="ona-eyebrow">Life & community</p>
            <p className="ona-script-label">A landscape made for people</p>

            <h1>
              Everyday life,
              <br />
              <em>elevated.</em>
            </h1>

            <p>
              From morning coffee to sunset conversations, ONA brings the useful,
              the social and the restorative closer together — creating more room
              to enjoy everyday life in Zanzibar.
            </p>

            <div className="ona-life-hero-notes" aria-label="Lifestyle highlights">
              <span>8 curated community spaces</span>
              <span>Landscape-led living</span>
              <span>Everyday convenience</span>
            </div>
          </div>
        </div>
      </section>

      <section className="ona-life-amenities">
        <div className="ona-section-shell">
          <header className="ona-life-section-heading">
            <div>
              <p className="ona-eyebrow">Curated around the day</p>
              <p className="ona-script-label">Closer to home</p>
            </div>

            <h2>
              Places for the moments
              <br />
              <em>that make life feel complete.</em>
            </h2>

            <p>
              ONA combines everyday convenience with places to gather, focus,
              recharge and connect — each one designed as part of a single
              residential experience.
            </p>
          </header>

          <div className="ona-life-amenity-grid">
            {amenities.map((amenity, index) => {
              const Icon = amenity.icon;
              const featured = index === 0 || index === 1 || index === 6;

              return (
                <article
                  className={`ona-life-amenity-card${
                    featured ? " ona-life-amenity-card--featured" : ""
                  }${!amenity.image ? " ona-life-amenity-card--text" : ""}`}
                  key={amenity.number}
                >
                  {amenity.image && (
                    <div className="ona-life-amenity-media">
                      <img
                        src={amenity.image}
                        alt={`ONA Towers ${amenity.title}`}
                        loading="lazy"
                      />
                      <div className="ona-life-amenity-media-overlay" />
                    </div>
                  )}

                  <div className="ona-life-amenity-content">
                    <div className="ona-life-amenity-meta">
                      <span>{amenity.number}</span>
                      <Icon size={18} strokeWidth={1.4} aria-hidden="true" />
                    </div>

                    <h3>{amenity.title}</h3>
                    <p>{amenity.text}</p>
                  </div>
                </article>
              );
            })}
          </div>
        </div>
      </section>

      <section className="ona-life-landscape-premium">
        <img
          src={projectImages.development.landscape}
          alt="ONA Towers landscaped arrival and outdoor setting"
          loading="lazy"
        />
        <div className="ona-life-landscape-premium-overlay" />

        <div className="ona-section-shell ona-life-landscape-premium-inner">
          <div className="ona-life-landscape-premium-copy">
            <p className="ona-eyebrow">Between the buildings</p>
            <p className="ona-script-label">Green by design. Calm by nature.</p>

            <h2>
              More room
              <br />
              <em>for life outdoors.</em>
            </h2>

            <p>
              Shaded movement, planted edges and welcoming outdoor places make
              landscape part of the everyday experience — not simply something
              viewed from above.
            </p>

            <div className="ona-life-landscape-actions">
              <SiteLink to="/residences" className="ona-button ona-button--sand">
                Discover residences <span aria-hidden="true">→</span>
              </SiteLink>

              <SiteLink to="/enquire" className="ona-button ona-button--glass">
                Register interest <span aria-hidden="true">→</span>
              </SiteLink>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
