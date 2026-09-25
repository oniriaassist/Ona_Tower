import {
  Building2,
  MapPin,
} from "lucide-react";

import "../styles/location-kml.css";

const ONA_MAP_EMBED =
  "https://www.google.com/maps/d/embed?mid=13U2vK-wYa5eoj-2tfuLP5WS-qZRn55I&ehbc=2E312F&noprof=1";

export default function LocationSection() {
  return (
    <main className="ona-location-premium-page">
      <section className="ona-location-premium-intro">
        <div className="ona-section-shell">
          <div className="ona-location-premium-heading">
            <span className="ona-location-premium-kicker">
              Location
            </span>

            <p className="ona-location-premium-script">
              Mazizini · Zanzibar
            </p>

            <div className="ona-location-premium-highlights">
              <span>
                <Building2
                  size={15}
                  strokeWidth={1.4}
                  aria-hidden="true"
                />

                Two residential towers
              </span>

              <span>
                <Building2
                  size={15}
                  strokeWidth={1.4}
                  aria-hidden="true"
                />

                ONA House
              </span>

              <span>
                <MapPin
                  size={15}
                  strokeWidth={1.4}
                  aria-hidden="true"
                />

                Mazizini · Zanzibar
              </span>
            </div>
          </div>
        </div>
      </section>

      <section className="ona-location-premium-map-section">

        <div className="ona-location-premium-map">
          <div className="ona-location-google-crop">
            <iframe
              className="ona-location-google-map"
              src={ONA_MAP_EMBED}
              title="ONA Towers location in Mazizini, Zanzibar"
              loading="eager"
              allowFullScreen
              referrerPolicy="no-referrer-when-downgrade"
            />
          </div>

          <div
            className="ona-location-map-brand"
            aria-hidden="true"
          >
            <span>
              ONA Towers
            </span>

            <strong>
              Mazizini · Zanzibar
            </strong>
          </div>
        </div>
      </section>
    </main>
  );
}