import { projectImages } from "../data/images";
import "../styles/ona-redesign.css";

const values = [
  {
    number: "01",
    title: "Belong to place",
    text: "Architecture shaped by Zanzibar's light, climate, landscape and outward-looking character.",
  },
  {
    number: "02",
    title: "Design life as one experience",
    text: "Homes, arrival, landscape, amenities and ONA House are planned as one connected address.",
  },
  {
    number: "03",
    title: "Think beyond launch",
    text: "A place designed to remain relevant, desirable and valuable through the way it lives over time.",
  },
];

const partners = [
  {
    eyebrow: "Project vision",
    name: "ONIRIA Investments",
    text: "A Zanzibar-born investment and development platform creating distinctive places, experiences and new ways of living.",
    href: "https://oniriainvestments.com/",
    logo: "/ona-assets/partners/oniria-investments.png",
    logoClass: "ona-story-partner-logo--oniria",
  },
  {
    eyebrow: "Wider business ecosystem",
    name: "Vigor Group of Companies",
    text: "A diversified Tanzanian business group rooted in Zanzibar, bringing decades of operating experience across multiple sectors.",
    href: "https://turkysgroup.co.tz/",
    logo: "/ona-assets/partners/vigor-group.png",
    logoClass: "ona-story-partner-logo--vigor",
  },
  {
    eyebrow: "Housing-sector institution",
    name: "Zanzibar Housing Corporation",
    text: "A public institution responsible for managing and developing Zanzibar's housing sector and supporting its continued evolution.",
    href: "http://www.zhc.go.tz/about/about_us",
    logo: "/ona-assets/partners/zanzibar-housing-corporation.png",
    logoClass: "ona-story-partner-logo--zhc",
  },
];

export default function Development() {
  return (
    <>
      <section className="ona-story-values">
        <div className="ona-story-values-image" aria-hidden="true">
          <img
            src="/ona-assets/development/landscape-gardens.webp"
            alt=""
            loading="lazy"
          />
        </div>
        <div className="ona-story-values-wash" aria-hidden="true" />

        <div className="ona-section-shell ona-story-values-inner">
          <div className="ona-story-values-copy">
            <p className="ona-story-overline">What we stand for</p>
            <span className="ona-story-rule" aria-hidden="true" />
            <p className="ona-story-script">Purpose before spectacle</p>

            <h2>
              A home should feel
              <br />
              <em>right for its place.</em>
            </h2>

            <p>
              ONA is designed around what makes daily life feel better:
              thoughtful architecture, useful spaces, strong connections and a
              sense of calm that belongs naturally to Zanzibar.
            </p>
          </div>

          <div className="ona-story-values-grid">
            {values.map((value) => (
              <article className="ona-story-value-card" key={value.number}>
                <span className="ona-story-value-number">{value.number}</span>
                <h3>{value.title}</h3>
                <span className="ona-story-card-rule" aria-hidden="true" />
                <p>{value.text}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="ona-story-people">
        <div className="ona-story-people-image">
          <img
            src={projectImages.story.peopleRelationships}
            alt="People collaborating in an ONA Towers ocean-view meeting setting"
            loading="lazy"
          />
        </div>

        <div className="ona-story-people-copy">
          <div>
            <p className="ona-story-overline">People &amp; relationships</p>
            <span className="ona-story-rule" aria-hidden="true" />

            <h2>
              A Zanzibar idea,
              <br />
              <em>built through collaboration.</em>
            </h2>

            <p>
              Places of lasting value are never created in isolation. ONA sits
              within a wider network of investment, business experience and the
              institutions helping shape Zanzibar&apos;s built environment.
            </p>

            <p>
              What connects those relationships is a long-term view: create an
              address that feels relevant to Zanzibar today and continues to
              matter to the people who live, work and invest here tomorrow.
            </p>
          </div>
        </div>
      </section>

      <section className="ona-story-partners">
        <div className="ona-section-shell">
          <header className="ona-story-partners-heading">
            <div>
              <p className="ona-story-overline">Partners</p>
              <h2>Connected by a shared long-term view.</h2>
            </div>
            <span aria-hidden="true" />
          </header>

          <div className="ona-story-partners-list">
            {partners.map((partner) => (
              <a
                key={partner.name}
                className="ona-story-partner-row"
                href={partner.href}
                target="_blank"
                rel="noreferrer"
              >
                <div className="ona-story-partner-logo-wrap">
                  <img
                    src={partner.logo}
                    alt={`${partner.name} logo`}
                    className={`ona-story-partner-logo ${partner.logoClass}`}
                    loading="lazy"
                  />
                </div>

                <div className="ona-story-partner-copy">
                  <span>{partner.eyebrow}</span>
                  <h3>{partner.name}</h3>
                  <p>{partner.text}</p>
                </div>

                <span className="ona-story-partner-link">
                  Visit website <span aria-hidden="true">↗</span>
                </span>
              </a>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
