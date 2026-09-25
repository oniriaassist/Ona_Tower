import { createElement, useEffect, useRef, useState } from "react";
import { ExternalLink, MapPin } from "lucide-react";

import { projectFacts } from "../data/projectFacts";
import "../styles/ona-redesign.css";

const MAPS_3D_SCRIPT_ID = "ona-google-maps-3d-script";

type MapState = "loading" | "ready" | "missing-key" | "error";

function loadGoogleMaps3D(apiKey: string) {
  return new Promise<void>((resolve, reject) => {
    if (customElements.get("gmp-map-3d")) {
      resolve();
      return;
    }

    const existingScript = document.getElementById(
      MAPS_3D_SCRIPT_ID,
    ) as HTMLScriptElement | null;

    if (existingScript) {
      customElements.whenDefined("gmp-map-3d").then(() => resolve()).catch(reject);
      return;
    }

    const script = document.createElement("script");
    script.id = MAPS_3D_SCRIPT_ID;
    script.async = true;
    script.src = `https://maps.googleapis.com/maps/api/js?loading=async&key=${encodeURIComponent(
      apiKey,
    )}&libraries=maps3d&v=weekly`;

    script.addEventListener("error", () => {
      reject(new Error("Unable to load Google Maps 3D."));
    });

    document.head.appendChild(script);

    customElements.whenDefined("gmp-map-3d").then(() => resolve()).catch(reject);
  });
}

export default function LocationSection() {
  const mapRef = useRef<HTMLElement | null>(null);
  const apiKey = (import.meta.env.VITE_GOOGLE_MAPS_API_KEY ?? "").trim();
  const [mapState, setMapState] = useState<MapState>(
    apiKey ? "loading" : "missing-key",
  );

  useEffect(() => {
    if (!apiKey) {
      setMapState("missing-key");
      return;
    }

    let cancelled = false;
    let readyTimer: number | undefined;

    loadGoogleMaps3D(apiKey)
      .then(() => {
        if (cancelled) return;

        const mapElement = mapRef.current;

        const markReady = () => {
          if (!cancelled) setMapState("ready");
        };

        mapElement?.addEventListener("gmp-steadystate", markReady, {
          once: true,
        });

        // The component is usable as soon as the custom element is defined.
        // Keep a small fallback timer because some browser/GPU combinations
        // do not dispatch gmp-steadystate immediately.
        readyTimer = window.setTimeout(markReady, 1400);
      })
      .catch(() => {
        if (!cancelled) setMapState("error");
      });

    return () => {
      cancelled = true;
      if (readyTimer) window.clearTimeout(readyTimer);
    };
  }, [apiKey]);

  const { latitude, longitude, altitude, range, tilt, heading } =
    projectFacts.locationMap;

  const map3d = apiKey
    ? createElement(
        "gmp-map-3d",
        {
          ref: (node: HTMLElement | null) => {
            mapRef.current = node;
          },
          center: `${latitude},${longitude},${altitude}`,
          range: String(range),
          tilt: String(tilt),
          heading: String(heading),
          mode: "satellite",
          "gesture-handling": "cooperative",
          description: "Satellite 3D view of Mazizini, Zanzibar",
        } as any,
        createElement("gmp-marker-3d", {
          position: `${latitude},${longitude},24`,
          label: "ONA Towers · Mazizini",
          "size-preserved": true,
          "draws-when-occluded": true,
        } as any),
      )
    : null;

  return (
    <main className="ona-location2-page">
      <section className="ona-location2-map-shell">
        <div className="ona-location2-map" aria-label="3D satellite map of Mazizini, Zanzibar">
          {map3d}

          <div className="ona-location2-map-shade" aria-hidden="true" />

          {mapState !== "ready" && (
            <div className="ona-location2-loader" role="status">
              {mapState === "loading" && (
                <>
                  <span className="ona-location2-loader-ring" aria-hidden="true" />
                  <span>Loading satellite view</span>
                </>
              )}

              {mapState === "missing-key" && (
                <div className="ona-location2-map-message">
                  <MapPin size={20} strokeWidth={1.5} aria-hidden="true" />
                  <strong>3D satellite map ready to connect.</strong>
                  <p>
                    Add <code>VITE_GOOGLE_MAPS_API_KEY</code> to the frontend
                    environment to enable the live Google 3D map.
                  </p>
                </div>
              )}

              {mapState === "error" && (
                <div className="ona-location2-map-message">
                  <MapPin size={20} strokeWidth={1.5} aria-hidden="true" />
                  <strong>Satellite view could not load.</strong>
                  <p>
                    You can still open the supplied Google Earth view using the
                    button below.
                  </p>
                </div>
              )}
            </div>
          )}

          <div className="ona-section-shell ona-location2-content">
            <div className="ona-location2-copy">
              <span className="ona-location2-kicker">The location</span>

              <h1>
                At the heart of
                <br />
                <em>Zanzibar.</em>
              </h1>

              <p>
                ONA Towers is set in Mazizini — an urban Zanzibar address that
                keeps home connected to the city, the coast and the wider island.
              </p>

              <div className="ona-location2-place">
                <MapPin size={16} strokeWidth={1.6} aria-hidden="true" />
                <span>Mazizini · Zanzibar</span>
              </div>

              <a
                className="ona-location2-earth-link"
                href={projectFacts.googleEarthUrl}
                target="_blank"
                rel="noopener noreferrer"
              >
                <span>Open in Google Earth</span>
                <ExternalLink size={15} strokeWidth={1.6} aria-hidden="true" />
              </a>
            </div>
          </div>

          <div className="ona-location2-coordinate" aria-hidden="true">
            <span>06°11′29″ S</span>
            <span>39°12′46″ E</span>
          </div>
        </div>
      </section>
    </main>
  );
}
