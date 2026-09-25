import { useMemo, useState } from "react";

import { residences, type ResidenceVariant } from "../data/residences";
import { SiteLink } from "../routing";
import "../styles/ona-redesign.css";

export function ResidenceSelector() {
  const [selectedResidenceId, setSelectedResidenceId] = useState(residences[0].id);

  const selectedResidence = useMemo(() => {
    return residences.find((residence) => residence.id === selectedResidenceId) ?? residences[0];
  }, [selectedResidenceId]);

  const [selectedVariantId, setSelectedVariantId] = useState(residences[0].variants[0].id);

  const selectedVariant: ResidenceVariant = useMemo(() => {
    return (
      selectedResidence.variants.find((variant) => variant.id === selectedVariantId) ??
      selectedResidence.variants[0]
    );
  }, [selectedResidence, selectedVariantId]);

  const handleResidenceChange = (residenceId: string) => {
    const nextResidence = residences.find((residence) => residence.id === residenceId) ?? residences[0];
    setSelectedResidenceId(nextResidence.id);
    setSelectedVariantId(nextResidence.variants[0].id);
  };

  return (
    <section className="ona-residence-selector" id="residence-portfolio">
      <div className="ona-section-shell">
        <header className="ona-residence-selector-heading">
          <div>
            <p className="ona-eyebrow">Residence portfolio</p>
            <p className="ona-script-label">Designed for elevated living</p>
          </div>

          <h2>
            Choose your
            <br />
            <em>residence.</em>
          </h2>

          <p>
            Compare the ONA Towers residence collections, orientations and
            floor-plan dimensions, then speak with the sales team about the home
            that fits the way you want to live.
          </p>
        </header>

        <div className="ona-residence-type-tabs" role="tablist" aria-label="Residence types">
          {residences.map((residence) => (
            <button
              key={residence.id}
              type="button"
              className={residence.id === selectedResidence.id ? "is-active" : ""}
              onClick={() => handleResidenceChange(residence.id)}
            >
              <span>{residence.shortLabel}</span>
              <small>{residence.range}</small>
            </button>
          ))}
        </div>

        <div className="ona-residence-selector-layout">
          <div className="ona-residence-selector-copy">
            <p className="ona-residence-product-label">Selected residence</p>
            <span className="ona-residence-range">{selectedResidence.range}</span>

            <h3>{selectedResidence.label}</h3>
            <p>{selectedResidence.description}</p>

            <div className="ona-residence-variant-tabs">
              {selectedResidence.variants.map((variant) => (
                <button
                  key={variant.id}
                  type="button"
                  className={variant.id === selectedVariant.id ? "is-active" : ""}
                  onClick={() => setSelectedVariantId(variant.id)}
                >
                  <strong>{variant.tower}</strong>
                  <span>{variant.orientation}</span>
                </button>
              ))}
            </div>

            <dl className="ona-residence-specs">
              <div>
                <dt>Total area</dt>
                <dd>{selectedVariant.totalArea} sqm</dd>
              </div>
              <div>
                <dt>Internal area</dt>
                <dd>{selectedVariant.suiteArea} sqm</dd>
              </div>
              <div>
                <dt>Terrace / balcony</dt>
                <dd>{selectedVariant.balconyArea} sqm</dd>
              </div>
            </dl>

            <SiteLink to="/enquire" className="ona-residence-sales-link">
              Request Interest <span aria-hidden="true">→</span>
            </SiteLink>
          </div>

          <div className="ona-residence-plan">
            <div className="ona-residence-plan-toolbar">
              <span>Brochure floor plan</span>
              <span>
                {selectedVariant.tower} · {selectedVariant.orientation}
              </span>
            </div>

            <img
              src={selectedVariant.floorPlan}
              alt={`${selectedResidence.label} floor plan from the official ONA Towers brochure`}
            />
          </div>
        </div>
        <p className="ona-residence-plan-note">
          Brochure layouts are shown by residence type. Layouts and areas vary by
          tower and orientation; confirm the selected residence plan and dimensions
          with our sales team.
        </p>
      </div>
    </section>
  );
}

export default ResidenceSelector;
