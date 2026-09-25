import { useEffect, useState } from "react";
import { SiteLink, usePathname } from "../routing";
import { projectFacts } from "../data/projectFacts";
import "../styles/ona-redesign.css";

const leftLinks = [
    {
    label: "Our Story",
    to: "/development",
  },
  {
    label: "Life & Community",
    to: "/lifestyle",
  },
  {
    label: "Location",
    to: "/location",
  },
];

const rightLinks = [
  {
    label: "Residences",
    to: "/residences",
  },
  {
    label: "Brochure",
    to: "/brochure",
  },
  {
    label: "Contact",
    to: "/enquire",
  },
];

type NavigationItem = {
  label: string;
  to: string;
  external?: boolean;
};

export default function Header() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  const pathname = usePathname();

  useEffect(() => {
    setMenuOpen(false);
  }, [pathname]);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 35);
    };

    handleScroll();

    window.addEventListener("scroll", handleScroll, {
      passive: true,
    });

    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, []);

  const transparentHomepage =
    pathname === "/" && !scrolled && !menuOpen;

  const renderLink = (
    item: NavigationItem,
    mobile = false,
  ) => {
    const className = mobile
      ? "ona-mobile-link"
      : "ona-nav-link";

    if (item.external) {
      return (
        <a
          key={item.label}
          href={item.to}
          target="_blank"
          rel="noopener noreferrer"
          className={className}
        >
          {item.label}
        </a>
      );
    }

    return (
      <SiteLink
        key={item.label}
        to={item.to}
        className={className}
      >
        {item.label}
      </SiteLink>
    );
  };

  return (
    <>
      <header
        className={[
          "ona-header",
          transparentHomepage
            ? "ona-header--transparent"
            : "ona-header--solid",
        ].join(" ")}
      >
        <div className="ona-header-inner">
          <nav
            className="ona-header-nav ona-header-nav--left"
            aria-label="Residences and sales navigation"
          >
            {leftLinks.map((item) => renderLink(item))}
          </nav>

          <SiteLink
            className="ona-header-logo"
            to="/"
            aria-label="ONA Towers home"
          >
            <span className="ona-header-logo-main">
              ÔNA
            </span>

            <span className="ona-header-logo-sub">
              TOWERS
            </span>
          </SiteLink>

          <nav
            className="ona-header-nav ona-header-nav--right"
            aria-label="Project navigation"
          >
            {rightLinks.map((item) => renderLink(item))}
          </nav>

          <button
            type="button"
            className={[
              "ona-menu-toggle",
              menuOpen ? "is-open" : "",
            ].join(" ")}
            aria-label="Toggle navigation"
            aria-expanded={menuOpen}
            onClick={() =>
              setMenuOpen((current) => !current)
            }
          >
            <span />
            <span />
          </button>
        </div>
      </header>

      <div
        className={[
          "ona-mobile-menu",
          menuOpen ? "is-open" : "",
        ].join(" ")}
      >
        <div className="ona-mobile-menu-inner">
          <p className="ona-eyebrow">
            {projectFacts.shortLocation}
          </p>

          <nav>
            {[...leftLinks, ...rightLinks].map(
              (item) => renderLink(item, true),
            )}
          </nav>

          <div className="ona-mobile-menu-footer">
            <span>{projectFacts.tagline}</span>
            <span>ONA Towers Limited</span>
          </div>
        </div>
      </div>
    </>
  );
}