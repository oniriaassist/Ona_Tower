import { Baby, Bell, BookOpen, Coffee, Palette, ShoppingBag, Sparkles, Users } from "lucide-react";
import { projectImages } from "../data/images";
import "../styles/ona-redesign.css";

const amenities = [
  {
    title: "Coffee & Bakery",
    description:
      "A familiar morning ritual — coffee, fresh bakery and easy moments just steps from home.",
    image: projectImages.amenities.cafe,
    icon: Coffee,
  },
  {
    title: "Social Lounge",
    description:
      "A relaxed place to meet, talk and spend unhurried time with friends, neighbours and guests.",
    image: projectImages.amenities.socialLounge,
    icon: Users,
  },
  {
    title: "Beauty Studio",
    description:
      "Personal care and everyday wellbeing brought comfortably closer to home.",
    image: projectImages.amenities.beautyStudio,
    icon: Sparkles,
  },
  {
    title: "Mini Market",
    description:
      "Daily essentials and useful convenience integrated naturally into the rhythm of the development.",
    image: projectImages.amenities.miniMarket,
    icon: ShoppingBag,
  },
  {
    title: "Art Salon",
    description:
      "A quieter cultural setting for art, ideas, conversation and moments of discovery.",
    image: projectImages.amenities.artSalon,
    icon: Palette,
  },
  {
    title: "Study Lounge",
    description:
      "A calm environment for reading, focused work and time away from the pace of the day.",
    image: projectImages.amenities.studyLounge,
    icon: BookOpen,
  },
  {
    title: "Concierge",
    description:
      "A welcoming point of assistance supporting a smoother and more considered residential experience.",
    image: projectImages.amenities.concierge,
    icon: Bell,
  },
  {
    title: "Kids' Club",
    description:
      "A dedicated place for younger residents to play, discover and feel part of the ONA community.",
    image: projectImages.amenities.kidsClub,
    icon: Baby,
  },
] as const;

export default function LifestylePage() {
  return (
    <main className="ona-life2-page">
      <section className="ona-life2-hero">
        <div className="ona-section-shell ona-life2-hero-grid">
          <div className="ona-life2-hero-copy">
            <span className="ona-life2-kicker">Life & community</span>
            <span className="ona-life2-script">A landscape made for people</span>

            <h1>
              Everyday life,
              <br />
              <em>beautifully considered.</em>
            </h1>

            <p>
              ONA brings the useful, the social and the restorative closer
              together — creating an address where everyday convenience,
              wellbeing, outdoor pause and community feel naturally connected.
            </p>

            <div className="ona-life2-highlights">
              <span>Landscape-led living</span>
              <span>Outdoor work garden</span>
              <span>Community-focused amenities</span>
            </div>
          </div>

          <div className="ona-life2-hero-media">
            <img
              src={projectImages.development.gardens}
              alt="ONA Towers outdoor work garden and landscaped lifestyle setting"
            />
            <div className="ona-life2-hero-media-overlay" />
            <div className="ona-life2-hero-caption">
              <span>Life at ONA</span>
              <strong>Landscape, shade and space for the day to unfold.</strong>
            </div>
          </div>
        </div>
      </section>

      <section className="ona-life2-amenities">
        <div className="ona-section-shell">
          <header className="ona-life2-heading">
            <div>
              <span className="ona-life2-kicker">Curated around the day</span>
              <span className="ona-life2-script">Closer to home</span>
            </div>

            <h2>
              <span className="ona-life2-title-line">Places for the moments</span>
              <em className="ona-life2-title-line">that make life feel complete.</em>
            </h2>

            <p>
              From the first coffee of the morning to focused work, personal
              care and easy conversation, ONA&apos;s community spaces are designed
              as one seamless residential experience.
            </p>
          </header>

          <div className="ona-life2-grid">
            {amenities.map((amenity) => {
              const Icon = amenity.icon;

              return (
                <article className="ona-life2-card" key={amenity.title}>
                  <div className="ona-life2-card-media">
                    <img
                      src={amenity.image}
                      alt={`ONA Towers ${amenity.title}`}
                      loading="lazy"
                    />
                    <div className="ona-life2-card-overlay" />
                  </div>

                  <div className="ona-life2-card-content">
                    <div className="ona-life2-card-icon" aria-hidden="true">
                      <Icon size={18} strokeWidth={1.4} />
                    </div>

                    <h3>{amenity.title}</h3>
                    <p>{amenity.description}</p>
                  </div>
                </article>
              );
            })}
          </div>
        </div>
      </section>
    </main>
  );
}
