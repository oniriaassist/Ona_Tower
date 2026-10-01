import { FormEvent, useEffect, useMemo, useState, type ElementType, type ReactNode } from 'react';
import {
  ArrowRight,
  BedDouble,
  Building2,
  CheckCircle2,
  Download,
  Expand,
  Home,
  ImageOff,
  Layers3,
  MessageCircle,
  RotateCcw,
  Ruler,
  Send,
  X,
} from 'lucide-react';

import {
  getCityViewInventory,
  type CityViewStatus,
  type CityViewUnit,
} from '../api/cityview';
import { submitEnquiry } from '../api/enquiries';
import '../styles/cityview.css';

type LeadAction = 'reserve' | 'advisor';
type ResidenceFilter = 'all' | '2-bedroom' | '3-bedroom' | 'penthouse';
type FloorFilter = 'all' | 'penthouse' | number;

type LeadForm = {
  name: string;
  phone: string;
  email: string;
  note: string;
  consent: boolean;
};

const emptyLeadForm: LeadForm = {
  name: '',
  phone: '',
  email: '',
  note: '',
  consent: false,
};

const STATUS_LABELS: Record<CityViewStatus, string> = {
  available: 'Available',
  on_hold: 'On Hold',
  reserved: 'Reserved',
  sold: 'Sold',
};

const statusOrder: CityViewStatus[] = ['available', 'on_hold', 'reserved', 'sold'];

function statusClass(status: CityViewStatus) {
  return `cityview-status-${status.replace('_', '-')}`;
}

function floorSort(a: CityViewUnit, b: CityViewUnit) {
  if (a.floor_number === null && b.floor_number !== null) return -1;
  if (a.floor_number !== null && b.floor_number === null) return 1;
  return (b.floor_number ?? 99) - (a.floor_number ?? 99) || a.unit_code.localeCompare(b.unit_code);
}

function matchesResidence(unit: CityViewUnit, filter: ResidenceFilter) {
  if (filter === 'all') return true;
  if (filter === 'penthouse') return unit.residence_type.includes('Penthouse');
  if (filter === '2-bedroom') return unit.bedrooms === 2 && !unit.residence_type.includes('Penthouse');
  return unit.bedrooms === 3 && !unit.residence_type.includes('Penthouse');
}

function formatFloor(unit: CityViewUnit) {
  return unit.floor_number === null ? 'Penthouse' : `Floor ${unit.floor_number}`;
}

function compactFloor(unit: CityViewUnit) {
  return unit.floor_number === null ? 'PH' : String(unit.floor_number).padStart(2, '0');
}

function normalizeAssetUrl(url: string) {
  if (!url) return url;
  return url.startsWith('/') ? url : `/${url}`;
}

function fallbackPlanFor(unit: CityViewUnit) {
  if (unit.residence_type.includes('Penthouse')) {
    return unit.bedrooms === 4
      ? '/ona-assets/floorplans/brochure-penthouse-4br.png'
      : '/ona-assets/floorplans/brochure-penthouse-3br.png';
  }
  return unit.bedrooms === 2
    ? '/ona-assets/floorplans/brochure-2br.png'
    : '/ona-assets/floorplans/brochure-3br.png';
}

export default function CityViewPage() {
  useEffect(() => {
    document.documentElement.classList.add('cityview-route-active');
    document.body.classList.add('cityview-route-active');
    return () => {
      document.documentElement.classList.remove('cityview-route-active');
      document.body.classList.remove('cityview-route-active');
    };
  }, []);

  const [units, setUnits] = useState<CityViewUnit[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState('');
  const [selectedCode, setSelectedCode] = useState('A-701');

  const [residenceFilter, setResidenceFilter] = useState<ResidenceFilter>('3-bedroom');
  const [towerFilter, setTowerFilter] = useState<'Tower A' | 'Tower B'>('Tower A');
  const [viewFilter, setViewFilter] = useState('Ocean View');
  const [floorFilter, setFloorFilter] = useState<FloorFilter>(7);

  const [leadAction, setLeadAction] = useState<LeadAction | null>(null);
  const [leadForm, setLeadForm] = useState<LeadForm>(emptyLeadForm);
  const [leadState, setLeadState] = useState<'idle' | 'submitting' | 'success' | 'error'>('idle');
  const [leadFeedback, setLeadFeedback] = useState('');
  const [planOpen, setPlanOpen] = useState(false);

  useEffect(() => {
    let active = true;
    getCityViewInventory()
      .then((result) => {
        if (!active) return;
        setUnits(result.units);
        const preferred = result.units.find((unit) => unit.unit_code === 'A-701') ?? result.units[0];
        if (preferred) setSelectedCode(preferred.unit_code);
      })
      .catch((error) => {
        if (!active) return;
        setLoadError(error instanceof Error ? error.message : 'Unable to load City View availability.');
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  const selectedUnit = useMemo(
    () => units.find((unit) => unit.unit_code === selectedCode) ?? units[0] ?? null,
    [selectedCode, units],
  );

  const floorOptions = useMemo(
    () => Array.from(new Set(units.filter((unit) => unit.floor_number !== null).map((unit) => unit.floor_number as number))).sort((a, b) => a - b),
    [units],
  );

  const viewOptions = useMemo(
    () => Array.from(new Set(units.map((unit) => unit.view))),
    [units],
  );

  const filteredCodes = useMemo(() => {
    return new Set(
      units
        .filter((unit) => matchesResidence(unit, residenceFilter))
        .filter((unit) => unit.tower === towerFilter)
        .filter((unit) => viewFilter === 'all' || unit.view === viewFilter)
        .filter((unit) => {
          if (floorFilter === 'all') return true;
          if (floorFilter === 'penthouse') return unit.floor_number === null;
          return unit.floor_number === floorFilter;
        })
        .map((unit) => unit.unit_code),
    );
  }, [floorFilter, residenceFilter, towerFilter, units, viewFilter]);

  useEffect(() => {
    if (!units.length || filteredCodes.has(selectedCode)) return;
    const nextCode = units.find((unit) => filteredCodes.has(unit.unit_code))?.unit_code;
    if (nextCode) {
      setSelectedCode(nextCode);
      return;
    }

    const compatible = units.find(
      (unit) => matchesResidence(unit, residenceFilter)
        && unit.tower === towerFilter
        && (viewFilter === 'all' || unit.view === viewFilter),
    );
    if (!compatible) return;
    setFloorFilter(compatible.floor_number === null ? 'penthouse' : compatible.floor_number);
    setSelectedCode(compatible.unit_code);
  }, [filteredCodes, residenceFilter, selectedCode, towerFilter, units, viewFilter]);

  useEffect(() => {
    const selectedViewStillAvailable = units.some(
      (unit) => unit.tower === towerFilter && matchesResidence(unit, residenceFilter) && unit.view === viewFilter,
    );
    if (!selectedViewStillAvailable) {
      const nextView = units.find((unit) => unit.tower === towerFilter && matchesResidence(unit, residenceFilter))?.view;
      if (nextView) setViewFilter(nextView);
    }
  }, [residenceFilter, towerFilter, units, viewFilter]);

  const counts = useMemo(() => {
    const next: Record<CityViewStatus, number> = { available: 0, on_hold: 0, reserved: 0, sold: 0 };
    units.forEach((unit) => {
      next[unit.status] += 1;
    });
    return next;
  }, [units]);

  const filteredViewOptions = useMemo(
    () => Array.from(new Set(units.filter((unit) => unit.tower === towerFilter && matchesResidence(unit, residenceFilter)).map((unit) => unit.view))),
    [residenceFilter, towerFilter, units],
  );

  const compatibleFloors = useMemo(() => {
    return new Set(
      units
        .filter((unit) => matchesResidence(unit, residenceFilter))
        .filter((unit) => unit.tower === towerFilter)
        .filter((unit) => viewFilter === 'all' || unit.view === viewFilter)
        .map((unit) => unit.floor_number === null ? 'penthouse' : unit.floor_number),
    );
  }, [residenceFilter, towerFilter, units, viewFilter]);

  const resetFilters = () => {
    setResidenceFilter('3-bedroom');
    setTowerFilter('Tower A');
    setViewFilter('Ocean View');
    setFloorFilter(7);
  };

  const openLead = (action: LeadAction) => {
    setLeadAction(action);
    setLeadForm(emptyLeadForm);
    setLeadState('idle');
    setLeadFeedback('');
  };

  const submitLead = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selectedUnit || !leadAction) return;
    if (!leadForm.consent) {
      setLeadState('error');
      setLeadFeedback('Please confirm that ONA Towers may use your details to respond to this request.');
      return;
    }

    setLeadState('submitting');
    setLeadFeedback('');
    const actionLabel = leadAction === 'reserve' ? 'Reserve residence' : 'Speak to an advisor';
    const structuredMessage = [
      'City View residence selection',
      `Unit: ${selectedUnit.unit_code}`,
      `Tower: ${selectedUnit.tower}`,
      `Floor: ${formatFloor(selectedUnit)}`,
      `Residence: ${selectedUnit.residence_type}`,
      `View: ${selectedUnit.view}`,
      `Total area: ${selectedUnit.total_area_sqm} sqm`,
      `Action: ${actionLabel}`,
      leadForm.note.trim() ? `Customer note: ${leadForm.note.trim()}` : '',
    ]
      .filter(Boolean)
      .join('\n');

    try {
      const response = await submitEnquiry({
        name: leadForm.name,
        phone: leadForm.phone,
        email: leadForm.email || undefined,
        residence_interest: `${selectedUnit.unit_code} | ${selectedUnit.residence_type} | ${selectedUnit.view}`,
        enquiry_type: leadAction === 'reserve' ? 'enquire_about_residence' : 'talk_to_sales',
        message: structuredMessage,
        consent: true,
        source: leadAction === 'reserve' ? 'cityview_reserve' : 'cityview_advisor',
        company_website: '',
      });
      setLeadState('success');
      setLeadFeedback(`Your request has been sent to the ONA Towers sales team. Reference: ${response.reference_number}`);
    } catch (error) {
      setLeadState('error');
      setLeadFeedback(error instanceof Error ? error.message : 'Unable to submit your request. Please try again.');
    }
  };

  return (
    <div className="cityview-page">
      <section className="cityview-hero">
        <img className="cityview-hero-image" src="/ona-assets/hero/ona-home-vision-premium.png" alt="ONA Towers in Zanzibar" />
        <div className="cityview-hero-shade" />
        <div className="cityview-hero-content">
          <div className="cityview-hero-copy">
            <p className="cityview-eyebrow">Luxury residences in Zanzibar</p>
            <h1>Find Your<br />Residence</h1>
            <p className="cityview-hero-intro">Select your tower, residence type, view and preferred floor.</p>
            <span className="cityview-hero-rule" />
          </div>
          <div className="cityview-hero-signature">
            <p>Live above<br />See beyond</p>
            <small>Zanzibar, Tanzania</small>
          </div>
        </div>
      </section>

      <main className="cityview-main">
        <section className="cityview-explorer-shell">
          <aside className="cityview-filters">
            <div className="cityview-panel-label">Refine your search</div>

            <FilterGroup label="Residence Type">
              <div className="cityview-filter-grid cityview-filter-grid-3">
                {([
                  ['2-bedroom', '2 Bedroom'],
                  ['3-bedroom', '3 Bedroom'],
                  ['penthouse', 'Penthouse'],
                ] as Array<[ResidenceFilter, string]>).map(([value, label]) => (
                  <button key={value} type="button" className={residenceFilter === value ? 'is-active' : ''} onClick={() => setResidenceFilter(value)}>
                    {label}
                  </button>
                ))}
              </div>
            </FilterGroup>

            <FilterGroup label="Tower">
              <div className="cityview-filter-grid cityview-filter-grid-2">
                {(['Tower A', 'Tower B'] as const).map((tower) => (
                  <button key={tower} type="button" className={towerFilter === tower ? 'is-active' : ''} onClick={() => setTowerFilter(tower)}>
                    {tower}
                  </button>
                ))}
              </div>
            </FilterGroup>

            <FilterGroup label="View">
              <div className="cityview-filter-grid cityview-filter-grid-2">
                {filteredViewOptions.length ? filteredViewOptions.map((view) => (
                  <button key={view} type="button" className={viewFilter === view ? 'is-active' : ''} onClick={() => setViewFilter(view)}>
                    {view}
                  </button>
                )) : (
                  <button type="button" className="is-active">{viewFilter}</button>
                )}
              </div>
            </FilterGroup>

            <FilterGroup label="Floor">
              <div className="cityview-floor-grid">
                {floorOptions.map((floor) => (
                  <button
                    key={floor}
                    type="button"
                    disabled={!compatibleFloors.has(floor)}
                    className={floorFilter === floor ? 'is-active' : ''}
                    onClick={() => setFloorFilter(floor)}
                  >
                    {String(floor).padStart(2, '0')}
                  </button>
                ))}
                <button
                  type="button"
                  disabled={!compatibleFloors.has('penthouse')}
                  className={floorFilter === 'penthouse' ? 'is-active' : ''}
                  onClick={() => setFloorFilter('penthouse')}
                >PH</button>
              </div>
            </FilterGroup>

            <button type="button" className="cityview-reset" onClick={resetFilters}>
              <RotateCcw size={15} /> Reset filters
            </button>
          </aside>

          <div className="cityview-availability">
            <div className="cityview-availability-top">
              <div className="cityview-panel-label">Availability explorer</div>
              <div className="cityview-legend" aria-label="Residence availability legend">
                {statusOrder.map((status) => (
                  <span key={status}>
                    <i className={statusClass(status)} />
                    {STATUS_LABELS[status]}
                    <b>{counts[status]}</b>
                  </span>
                ))}
              </div>
            </div>

            {loading ? (
              <div className="cityview-loading">Loading residence availability…</div>
            ) : loadError ? (
              <div className="cityview-error"><strong>City View is temporarily unavailable.</strong><span>{loadError}</span></div>
            ) : (
              <div className="cityview-towers">
                <TowerMatrix
                  tower="Tower A"
                  units={units}
                  filteredCodes={filteredCodes}
                  selectedCode={selectedUnit?.unit_code ?? ''}
                  onSelect={setSelectedCode}
                />
                <TowerMatrix
                  tower="Tower B"
                  units={units}
                  filteredCodes={filteredCodes}
                  selectedCode={selectedUnit?.unit_code ?? ''}
                  onSelect={setSelectedCode}
                />
              </div>
            )}
          </div>
        </section>

        {selectedUnit ? (
          <section className="cityview-selection-card" aria-live="polite">
            <div className="cityview-selection-copy">
              <div className="cityview-selection-title-row">
                <h2>{selectedUnit.unit_code}</h2>
                <span className={`cityview-selection-status ${statusClass(selectedUnit.status)}`}>{STATUS_LABELS[selectedUnit.status]}</span>
              </div>
              <p className="cityview-selection-meta">
                {selectedUnit.tower}
                <span />
                {formatFloor(selectedUnit)}
                <span />
                {selectedUnit.residence_type}
              </p>
              <p className="cityview-selection-view">{selectedUnit.view}</p>

              <div className="cityview-specs">
                <Spec icon={Ruler} value={`${selectedUnit.total_area_sqm} SQM`} label="Total Area" />
                <Spec icon={BedDouble} value={String(selectedUnit.bedrooms)} label="Bedrooms" />
                <Spec icon={Building2} value={selectedUnit.tower.replace('Tower ', '')} label="Tower" />
                <Spec icon={Layers3} value={compactFloor(selectedUnit)} label="Floor" />
              </div>
            </div>

            <button type="button" className="cityview-plan-preview" onClick={() => setPlanOpen(true)} aria-label={`Open floor plan for ${selectedUnit.unit_code}`}>
              <FloorPlanPreview unit={selectedUnit} />
              <span><Expand size={18} /></span>
            </button>

            <div className="cityview-actions">
              <button type="button" className="cityview-action-primary" onClick={() => setPlanOpen(true)}>
                View residence <ArrowRight size={17} />
              </button>
              <button
                type="button"
                className="cityview-action-secondary"
                onClick={() => openLead('reserve')}
                disabled={selectedUnit.status === 'sold'}
              >
                Reserve residence
              </button>
              <button type="button" className="cityview-action-secondary" onClick={() => openLead('advisor')}>
                <MessageCircle size={17} /> Speak to an advisor
              </button>
              <a className="cityview-action-secondary" href={normalizeAssetUrl(selectedUnit.floor_plan_url)} download={`${selectedUnit.unit_code}-floor-plan.jpg`}>
                <Download size={17} /> Download floor plan
              </a>
            </div>
          </section>
        ) : null}

      </main>

      {leadAction && selectedUnit ? (
        <div className="cityview-modal-backdrop" onMouseDown={() => setLeadAction(null)}>
          <div className="cityview-lead-modal" role="dialog" aria-modal="true" aria-labelledby="cityview-lead-title" onMouseDown={(event) => event.stopPropagation()}>
            <button type="button" className="cityview-modal-close" onClick={() => setLeadAction(null)} aria-label="Close request form"><X size={20} /></button>
            {leadState === 'success' ? (
              <div className="cityview-success">
                <CheckCircle2 size={42} />
                <p className="cityview-panel-label">Request received</p>
                <h2>Thank you.</h2>
                <p>{leadFeedback}</p>
                <button type="button" onClick={() => setLeadAction(null)}>Close</button>
              </div>
            ) : (
              <>
                <p className="cityview-panel-label">{leadAction === 'reserve' ? 'Residence request' : 'Private sales'}</p>
                <h2 id="cityview-lead-title">{leadAction === 'reserve' ? `Reserve ${selectedUnit.unit_code}` : 'Speak to an advisor'}</h2>
                <p className="cityview-modal-unit">{selectedUnit.tower} · {formatFloor(selectedUnit)} · {selectedUnit.residence_type} · {selectedUnit.view}</p>
                <form onSubmit={submitLead}>
                  <label>Full name *<input required autoComplete="name" value={leadForm.name} onChange={(event) => setLeadForm({ ...leadForm, name: event.target.value })} placeholder="Your name" /></label>
                  <div className="cityview-modal-fields">
                    <label>Phone / WhatsApp *<input required autoComplete="tel" value={leadForm.phone} onChange={(event) => setLeadForm({ ...leadForm, phone: event.target.value })} placeholder="+255 7XX XXX XXX" /></label>
                    <label>Email<input type="email" autoComplete="email" value={leadForm.email} onChange={(event) => setLeadForm({ ...leadForm, email: event.target.value })} placeholder="name@example.com" /></label>
                  </div>
                  <label>Message<textarea rows={3} value={leadForm.note} onChange={(event) => setLeadForm({ ...leadForm, note: event.target.value })} placeholder="Optional note for the sales advisor" /></label>
                  <label className="cityview-consent"><input type="checkbox" checked={leadForm.consent} onChange={(event) => setLeadForm({ ...leadForm, consent: event.target.checked })} /><span>I consent to ONA Towers using these details to respond to this residence request.</span></label>
                  {leadState === 'error' ? <div className="cityview-form-error">{leadFeedback}</div> : null}
                  <button className="cityview-submit" type="submit" disabled={leadState === 'submitting'}>
                    {leadState === 'submitting' ? 'Sending…' : 'Send to sales'} <Send size={16} />
                  </button>
                </form>
              </>
            )}
          </div>
        </div>
      ) : null}

      {planOpen && selectedUnit ? (
        <div className="cityview-modal-backdrop cityview-plan-backdrop" onMouseDown={() => setPlanOpen(false)}>
          <div className="cityview-plan-modal" role="dialog" aria-modal="true" aria-label={`Floor plan for ${selectedUnit.unit_code}`} onMouseDown={(event) => event.stopPropagation()}>
            <button type="button" className="cityview-modal-close" onClick={() => setPlanOpen(false)} aria-label="Close floor plan"><X size={20} /></button>
            <div className="cityview-plan-modal-copy">
              <p className="cityview-panel-label">{selectedUnit.tower} · {formatFloor(selectedUnit)}</p>
              <h2>{selectedUnit.unit_code}</h2>
              <p>{selectedUnit.residence_type} · {selectedUnit.view}</p>
              <dl>
                <div><dt>Suite</dt><dd>{selectedUnit.suite_area_sqm} sqm</dd></div>
                <div><dt>Balcony</dt><dd>{selectedUnit.balcony_area_sqm} sqm</dd></div>
                <div><dt>Total</dt><dd>{selectedUnit.total_area_sqm} sqm</dd></div>
              </dl>
              <button type="button" onClick={() => { setPlanOpen(false); openLead('advisor'); }}><MessageCircle size={16} /> Speak to an advisor</button>
            </div>
            <div className="cityview-plan-modal-image">
              <FloorPlanImage unit={selectedUnit} />
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

function FilterGroup({ label, children }: { label: string; children: ReactNode }) {
  return <div className="cityview-filter-group"><label>{label}</label>{children}</div>;
}

function Spec({ icon: Icon, value, label }: { icon: ElementType; value: string; label: string }) {
  return <div className="cityview-spec"><Icon size={19} strokeWidth={1.4} /><div><strong>{value}</strong><span>{label}</span></div></div>;
}

function FloorPlanPreview({ unit }: { unit: CityViewUnit }) {
  return (
    <div className="cityview-plan-preview-frame">
      <FloorPlanImage unit={unit} compact />
    </div>
  );
}

function FloorPlanImage({ unit, compact = false }: { unit: CityViewUnit; compact?: boolean }) {
  const sources = useMemo(
    () => Array.from(new Set([normalizeAssetUrl(unit.floor_plan_url), fallbackPlanFor(unit)].filter(Boolean))),
    [unit],
  );
  const [sourceIndex, setSourceIndex] = useState(0);

  useEffect(() => {
    setSourceIndex(0);
  }, [unit.unit_code, unit.floor_plan_url]);

  if (sourceIndex >= sources.length) {
    return (
      <div className={`cityview-plan-fallback ${compact ? 'is-compact' : ''}`}>
        <ImageOff size={compact ? 22 : 32} />
        <strong>{unit.unit_code} floor plan</strong>
        <span>Floor plan preview unavailable.</span>
      </div>
    );
  }

  return (
    <img
      src={sources[sourceIndex]}
      alt={`${unit.unit_code} floor plan`}
      loading="eager"
      decoding="async"
      onError={() => setSourceIndex((current) => current + 1)}
    />
  );
}

function TowerMatrix({
  tower,
  units,
  filteredCodes,
  selectedCode,
  onSelect,
}: {
  tower: 'Tower A' | 'Tower B';
  units: CityViewUnit[];
  filteredCodes: Set<string>;
  selectedCode: string;
  onSelect: (code: string) => void;
}) {
  const towerUnits = units.filter((unit) => unit.tower === tower);
  const floors = Array.from(new Set(towerUnits.filter((unit) => unit.floor_number !== null).map((unit) => unit.floor_number as number))).sort((a, b) => b - a);
  const penthouses = towerUnits.filter((unit) => unit.floor_number === null).sort(floorSort);

  return (
    <section className="cityview-tower">
      <h3>{tower}</h3>
      <div className="cityview-tower-body">
        <div className={`cityview-tower-render ${tower === 'Tower B' ? 'is-b' : ''}`}>
          <img
            src={tower === 'Tower A' ? '/ona-assets/cityview/tower-a-portrait.webp' : '/ona-assets/cityview/tower-b-portrait.webp'}
            alt={`${tower} architectural view`}
            onError={(event) => {
              event.currentTarget.onerror = null;
              event.currentTarget.src = '/ona-assets/hero/ona-home-vision-premium.png';
            }}
          />
        </div>
        <div className="cityview-unit-matrix">
          {penthouses.length ? (
            <div className="cityview-unit-row cityview-unit-row-penthouse">
              <span>PH</span>
              <div className="cityview-unit-cells">
                {penthouses.map((unit) => <UnitButton key={unit.unit_code} unit={unit} matches={filteredCodes.has(unit.unit_code)} selected={selectedCode === unit.unit_code} onSelect={onSelect} />)}
              </div>
            </div>
          ) : null}
          {floors.map((floor) => {
            const floorUnits = towerUnits.filter((unit) => unit.floor_number === floor).sort((a, b) => a.unit_code.localeCompare(b.unit_code));
            return (
              <div className="cityview-unit-row" key={floor}>
                <span>{String(floor).padStart(2, '0')}</span>
                <div className="cityview-unit-cells">
                  {floorUnits.map((unit) => <UnitButton key={unit.unit_code} unit={unit} matches={filteredCodes.has(unit.unit_code)} selected={selectedCode === unit.unit_code} onSelect={onSelect} />)}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

function UnitButton({ unit, matches, selected, onSelect }: { unit: CityViewUnit; matches: boolean; selected: boolean; onSelect: (code: string) => void }) {
  return (
    <button
      type="button"
      className={[
        'cityview-unit-button',
        statusClass(unit.status),
        matches ? 'is-match' : 'is-filtered',
        selected ? 'is-selected' : '',
      ].join(' ')}
      onClick={() => onSelect(unit.unit_code)}
      title={`${unit.unit_code} · ${unit.residence_type} · ${unit.view} · ${STATUS_LABELS[unit.status]}`}
    >
      {unit.unit_code}
    </button>
  );
}
