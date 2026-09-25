import { SiteLink } from "../routing";

import {
  projectImages,
} from "../data/images";

import "../styles/ona-redesign.css";

export function CommercialStory() {
  return (
    <>
      <section className="ona-commercial-hero">
        <div className="ona-section-shell ona-commercial-hero-inner">
          <div>
            <p className="ona-eyebrow">
              ONA House
            </p>

            <p className="ona-script-label">
              Work. Meet. Connect.
            </p>
          </div>

          <h1>
            WORK
            <br />

            <span>
              AT ONA.
            </span>
          </h1>

          <p>
            A contemporary commercial
            address designed for flexible
            work, meetings, everyday
            services and convenience
            within ONA.
          </p>
        </div>
      </section>

      <section className="ona-commercial-plan">
        <div className="ona-section-shell ona-commercial-plan-layout">
          <div className="ona-commercial-plan-image">
            <img
              src={
                projectImages
                  .commercial
                  .officePlan
              }
              alt="ONA House office floor plan"
              loading="lazy"
            />
          </div>

          <div className="ona-commercial-plan-copy">
            <p className="ona-eyebrow">
              01 / Office level
            </p>

            <h2>
              Space made for
              <br />

              <em>
                productive work.
              </em>
            </h2>

            <p>
              Flexible office suites are
              supported by reception,
              waiting, lounge, meeting,
              boardroom and service
              spaces.
            </p>

            <div className="ona-commercial-points">
              <span>
                Flexible office suites
              </span>

              <span>
                Reception & waiting lounge
              </span>

              <span>
                Boardroom
              </span>

              <span>
                Shared lounge
              </span>

              <span>
                Kitchen & services
              </span>
            </div>
          </div>
        </div>
      </section>

      <section className="ona-commercial-service">
        <div className="ona-section-shell">
          <p className="ona-eyebrow">
            Everyday convenience
          </p>

          <h2>
            Services
            <br />

            <em>
              close to home.
            </em>
          </h2>

          <p>
            Ground-floor retail and
            convenience functions support
            residents, visitors and the
            wider ONA community.
          </p>

          <SiteLink
            to="/enquire"
            className="ona-inline-button"
          >
            Enquire about ONA House

            <span
              aria-hidden="true"
            >
              →
            </span>
          </SiteLink>
        </div>
      </section>
    </>
  );
}

export default CommercialStory;