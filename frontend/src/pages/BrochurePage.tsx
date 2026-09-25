import { useEffect, useRef, useState } from 'react';
import { ArrowUpRight, Download, FileText, X } from 'lucide-react';
import { SiteLink } from '../routing';
import '../styles/brochure-page.css';

const BROCHURE_URL = '/documents/ONA-Towers-Brochure-Web.pdf';

export default function BrochurePage() {
  const [viewerOpen, setViewerOpen] = useState(false);
  const dialog = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    if (!viewerOpen) return;

    const previousOverflow = document.body.style.overflow;
    const trigger = document.activeElement as HTMLElement | null;

    dialog.current?.showModal();
    document.body.style.overflow = 'hidden';

    return () => {
      document.body.style.overflow = previousOverflow;
      trigger?.focus();
    };
  }, [viewerOpen]);

  function openBrochure() {
    if (window.matchMedia('(max-width: 760px)').matches) {
      window.open(BROCHURE_URL, '_blank', 'noopener,noreferrer');
    } else {
      setViewerOpen(true);
    }
  }

  return (
    <div className="ona-brochure-page">
      <section
        className="ona-brochure-hero"
        aria-labelledby="brochure-title"
      >
        <img
          className="ona-brochure-image"
          src="/ona-assets/brochure/cover-official.png"
          alt="ONA Towers overlooking the Indian Ocean in Zanzibar"
          fetchPriority="high"
        />

        <div className="ona-brochure-shade" />

        <div className="ona-brochure-shell ona-brochure-intro">
          <p className="ona-brochure-eyebrow">Brochure </p>

          <h1 id="brochure-title">
            ONA Towers
            <span>A new perspective on island living.</span>
          </h1>

          <p className="ona-brochure-lead">
            Explore the residences, signature penthouses and shared spaces that
            bring the ONA address to life.
          </p>

          <div className="ona-brochure-actions">
            <button
              className="ona-brochure-action ona-brochure-primary"
              onClick={openBrochure}
              type="button"
            >
              <FileText size={18} />
              Read brochure
              <ArrowUpRight size={18} />
            </button>

            <a
              className="ona-brochure-action ona-brochure-download"
              href={BROCHURE_URL}
              download
            >
              <Download size={18} />
              Download PDF
            </a>
          </div>
        </div>
      </section>

      <section
        className="ona-brochure-overview"
        aria-labelledby="inside-title"
      >
        <div className="ona-brochure-shell">
          <div className="ona-brochure-section-heading">
            <div>
              <p className="ona-brochure-eyebrow">Inside ONA</p>
              <h2 id="inside-title">Consider every detail.</h2>
            </div>

            <SiteLink
              to="/residences"
              className="ona-brochure-text-link"
            >
              Explore residences
              <ArrowUpRight size={18} />
            </SiteLink>
          </div>

          <div className="ona-brochure-facts">
            <div>
              <span>Architecture</span>
              <h3>Two sculptural towers</h3>
              <p>A distinctive addition to the Zanzibar skyline.</p>
            </div>

            <div>
              <span>Residences</span>
              <h3>2 &amp; 3 bedrooms</h3>
              <p>Explore the layouts and find your preferred residence.</p>
            </div>

            <div>
              <span>Lifestyle</span>
              <h3>Space for everyday life</h3>
              <p>Discover the development&apos;s shared amenities.</p>
            </div>

            <div>
              <span>Signature</span>
              <h3>Penthouse collection</h3>
              <p>A closer look at ONA&apos;s signature residences.</p>
            </div>
          </div>
        </div>
      </section>

      {viewerOpen && (
        <dialog
          ref={dialog}
          className="ona-brochure-dialog"
          aria-label="ONA Towers project brochure"
          onCancel={() => setViewerOpen(false)}
          onClose={() => setViewerOpen(false)}
        >
          <header>
            <strong>ONA Towers / Project brochure</strong>

            <div>
              <a
                href={BROCHURE_URL}
                download
                aria-label="Download brochure"
                title="Download brochure"
              >
                <Download size={20} />
              </a>

              <a
                href={BROCHURE_URL}
                target="_blank"
                rel="noreferrer"
                aria-label="Open PDF in a new tab"
                title="Open PDF in a new tab"
              >
                <ArrowUpRight size={20} />
              </a>

              <button
                type="button"
                autoFocus
                onClick={() => setViewerOpen(false)}
                aria-label="Close brochure"
                title="Close brochure"
              >
                <X size={22} />
              </button>
            </div>
          </header>

          <object
            data={`${BROCHURE_URL}#view=FitH`}
            type="application/pdf"
            aria-label="Project brochure PDF"
          >
            <p>
              <a
                href={BROCHURE_URL}
                target="_blank"
                rel="noreferrer"
              >
                Open the brochure in a new tab
              </a>
            </p>
          </object>
        </dialog>
      )}
    </div>
  );
}
