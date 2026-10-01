import { useEffect, useMemo, useState } from 'react';
import {
  Building2,
  CheckCircle2,
  Clock3,
  ExternalLink,
  FileText,
  House,
  Search,
  UserRound,
  ChevronDown,
} from 'lucide-react';

import {
  getAdminCityView,
  getAdminEnquiries,
  updateAdminCityViewUnit,
  type AdminEnquiry,
} from '../../api/admin';
import type { CityViewStatus, CityViewUnit } from '../../api/cityview';
import { ErrorBanner, PageLoader } from '../components';
import { formatAdminDate, humanize } from '../format';
import '../../styles/admin-cityview.css';

const statusLabels: Record<CityViewStatus, string> = {
  available: 'Available',
  on_hold: 'On Hold',
  reserved: 'Reserved',
  sold: 'Sold',
};

function statusClass(status: CityViewStatus) {
  return `ona-inventory-status-${status.replace('_', '-')}`;
}

function fallbackPlanFor(unit: CityViewUnit) {
  if (unit.residence_type.includes('Penthouse')) {
    return unit.bedrooms === 4 ? '/ona-assets/floorplans/brochure-penthouse-4br.png' : '/ona-assets/floorplans/brochure-penthouse-3br.png';
  }
  return unit.bedrooms === 2 ? '/ona-assets/cityview/floorplans/tower-a-2-ocean.jpg' : '/ona-assets/floorplans/brochure-3br.png';
}

export function InventoryView() {
  const [units, setUnits] = useState<CityViewUnit[]>([]);
  const [leads, setLeads] = useState<AdminEnquiry[]>([]);
  const [selectedCode, setSelectedCode] = useState('A-701');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [savingCode, setSavingCode] = useState('');
  const [search, setSearch] = useState('');
  const [tower, setTower] = useState('all');
  const [status, setStatus] = useState('all');
  const [floor, setFloor] = useState('all');
  const [type, setType] = useState('all');
  const [view, setView] = useState('all');

  useEffect(() => {
    let active = true;
    Promise.all([
      getAdminCityView(),
      getAdminEnquiries({ pageSize: 100 }),
    ])
      .then(([inventory, enquiryResult]) => {
        if (!active) return;
        setUnits(inventory.units);
        const cityViewLeads = enquiryResult.items.filter((item) => item.source.startsWith('cityview'));
        setLeads(cityViewLeads);
        const latestLeadCode = cityViewLeads[0]?.residence_interest?.split('|')[0]?.trim();
        const preferred = inventory.units.find((item) => item.unit_code === latestLeadCode)
          ?? inventory.units.find((item) => item.unit_code === 'A-701')
          ?? inventory.units[0];
        if (preferred) setSelectedCode(preferred.unit_code);
      })
      .catch((err) => {
        if (active) setError(err instanceof Error ? err.message : 'Unable to load City View inventory.');
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => { active = false; };
  }, []);

  const selectedUnit = useMemo(
    () => units.find((unit) => unit.unit_code === selectedCode) ?? units[0] ?? null,
    [selectedCode, units],
  );

  const selectedLead = useMemo(() => {
    if (!selectedUnit) return null;
    return leads.find((lead) => lead.residence_interest?.startsWith(selectedUnit.unit_code)) ?? null;
  }, [leads, selectedUnit]);

  const counts = useMemo(() => {
    const next: Record<CityViewStatus, number> = { available: 0, on_hold: 0, reserved: 0, sold: 0 };
    units.forEach((unit) => { next[unit.status] += 1; });
    return next;
  }, [units]);

  const floorOptions = useMemo(
    () => Array.from(new Set(units.map((unit) => unit.floor_number === null ? 'Penthouse' : String(unit.floor_number)))).sort((a, b) => {
      if (a === 'Penthouse') return -1;
      if (b === 'Penthouse') return 1;
      return Number(b) - Number(a);
    }),
    [units],
  );

  const typeOptions = useMemo(() => Array.from(new Set(units.map((unit) => unit.residence_type))).sort(), [units]);
  const viewOptions = useMemo(() => Array.from(new Set(units.map((unit) => unit.view))).sort(), [units]);

  const filteredUnits = useMemo(() => {
    const term = search.trim().toLowerCase();
    return units.filter((unit) => {
      if (term && !`${unit.unit_code} ${unit.tower} ${unit.residence_type} ${unit.view}`.toLowerCase().includes(term)) return false;
      if (tower !== 'all' && unit.tower !== tower) return false;
      if (status !== 'all' && unit.status !== status) return false;
      if (type !== 'all' && unit.residence_type !== type) return false;
      if (view !== 'all' && unit.view !== view) return false;
      if (floor !== 'all') {
        const label = unit.floor_number === null ? 'Penthouse' : String(unit.floor_number);
        if (label !== floor) return false;
      }
      return true;
    });
  }, [floor, search, status, tower, type, units, view]);

  const changeStatus = async (unit: CityViewUnit, nextStatus: CityViewStatus) => {
    if (nextStatus === unit.status) return;
    setSavingCode(unit.unit_code);
    setError('');
    try {
      const updated = await updateAdminCityViewUnit(unit.unit_code, nextStatus);
      setUnits((current) => current.map((item) => item.unit_code === updated.unit_code ? updated : item));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to update residence status.');
    } finally {
      setSavingCode('');
    }
  };

  if (loading) return <PageLoader label="Loading residence inventory" />;
  if (error && units.length === 0) return <ErrorBanner message={error} />;

  const metrics = [
    { label: 'Available Units', value: counts.available, note: `${Math.round((counts.available / Math.max(units.length, 1)) * 100)}% of total`, icon: Building2, status: 'available' as CityViewStatus },
    { label: 'On Hold', value: counts.on_hold, note: 'Awaiting next action', icon: Clock3, status: 'on_hold' as CityViewStatus },
    { label: 'Reserved', value: counts.reserved, note: 'Buyer reserved', icon: FileText, status: 'reserved' as CityViewStatus },
    { label: 'Sold', value: counts.sold, note: 'Completed sales', icon: CheckCircle2, status: 'sold' as CityViewStatus },
  ];

  return (
    <div className="ona-inventory-page">
      {error ? <ErrorBanner message={error} /> : null}

      <div className="ona-inventory-toolbar">
        <div>
          <p className="ona-inventory-kicker">ONA Towers live sales inventory</p>
          <h2>Residence inventory</h2>
          <p>Manage City View availability and review buyer interest without exposing the admin workspace to customers.</p>
        </div>
        <a href="/cityview" target="_blank" rel="noreferrer">Open City View <ExternalLink size={15} /></a>
      </div>

      <section className="ona-inventory-metrics">
        {metrics.map((metric) => {
          const Icon = metric.icon;
          return (
            <article key={metric.label}>
              <div className={`ona-inventory-metric-icon ${statusClass(metric.status)}`}><Icon size={22} strokeWidth={1.5} /></div>
              <div><span>{metric.label}</span><strong>{metric.value}</strong><small>{metric.note}</small></div>
            </article>
          );
        })}
        <article>
          <div className="ona-inventory-metric-icon ona-inventory-leads"><UserRound size={22} strokeWidth={1.5} /></div>
          <div><span>City View Leads</span><strong>{leads.length}</strong><small>Submitted from /cityview</small></div>
        </article>
      </section>

      <div className="ona-inventory-layout">
        <section className="ona-inventory-table-card">
          <div className="ona-inventory-card-heading">
            <div><h3>Live Inventory</h3><p>View and manage all verified ONA residence units.</p></div>
          </div>

          <div className="ona-inventory-filters">
            <label className="ona-inventory-search"><Search size={15} /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search unit" /></label>
            <select value={tower} onChange={(event) => setTower(event.target.value)}><option value="all">All Towers</option><option value="Tower A">Tower A</option><option value="Tower B">Tower B</option></select>
            <select value={floor} onChange={(event) => setFloor(event.target.value)}><option value="all">All Floors</option>{floorOptions.map((item) => <option key={item} value={item}>{item}</option>)}</select>
            <select value={type} onChange={(event) => setType(event.target.value)}><option value="all">All Types</option>{typeOptions.map((item) => <option key={item} value={item}>{item}</option>)}</select>
            <select value={view} onChange={(event) => setView(event.target.value)}><option value="all">All Views</option>{viewOptions.map((item) => <option key={item} value={item}>{item}</option>)}</select>
            <select value={status} onChange={(event) => setStatus(event.target.value)}><option value="all">All Statuses</option>{(Object.keys(statusLabels) as CityViewStatus[]).map((item) => <option key={item} value={item}>{statusLabels[item]}</option>)}</select>
          </div>

          <div className="ona-inventory-table-wrap">
            <table>
              <thead><tr><th>Unit</th><th>Tower</th><th>Floor</th><th>Type</th><th>View</th><th>Area</th><th>Status</th></tr></thead>
              <tbody>
                {filteredUnits.map((unit) => (
                  <tr key={unit.unit_code} className={selectedUnit?.unit_code === unit.unit_code ? 'is-selected' : ''} onClick={() => setSelectedCode(unit.unit_code)}>
                    <td><strong>{unit.unit_code}</strong></td>
                    <td>{unit.tower.replace('Tower ', '')}</td>
                    <td>{unit.floor_number === null ? 'PH' : unit.floor_number}</td>
                    <td>{unit.residence_type}</td>
                    <td>{unit.view}</td>
                    <td>{unit.total_area_sqm} sqm</td>
                    <td onClick={(event) => event.stopPropagation()}>
                      <div className={`ona-inventory-status-control ${statusClass(unit.status)}`}>
                        <select
                          className={`ona-inventory-status-select ${statusClass(unit.status)}`}
                          value={unit.status}
                          disabled={savingCode === unit.unit_code}
                          onChange={(event) => void changeStatus(unit, event.target.value as CityViewStatus)}
                        >
                          {(Object.keys(statusLabels) as CityViewStatus[]).map((item) => <option key={item} value={item}>{statusLabels[item]}</option>)}
                        </select>
                        <ChevronDown size={16} />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="ona-inventory-table-footer">Showing {filteredUnits.length} of {units.length} residences</div>
        </section>

        <aside className="ona-inventory-detail-card">
          {selectedUnit ? (
            <>
              <div className="ona-inventory-detail-heading">
                <div><span>Selected residence</span><h3>{selectedUnit.unit_code}</h3><p>{selectedUnit.residence_type}</p></div>
                <span className={`ona-inventory-status-pill ${statusClass(selectedUnit.status)}`}>{statusLabels[selectedUnit.status]}</span>
              </div>
              <img className="ona-inventory-plan" src={selectedUnit.floor_plan_url} alt={`${selectedUnit.unit_code} floor plan`} onError={(event) => { event.currentTarget.onerror = null; event.currentTarget.src = fallbackPlanFor(selectedUnit); }} />
              <div className="ona-inventory-detail-grid">
                <div><span>Tower</span><strong>{selectedUnit.tower}</strong></div>
                <div><span>Floor</span><strong>{selectedUnit.floor_number === null ? 'Penthouse' : selectedUnit.floor_number}</strong></div>
                <div><span>Total area</span><strong>{selectedUnit.total_area_sqm} sqm</strong></div>
                <div><span>View</span><strong>{selectedUnit.view}</strong></div>
              </div>

              <div className="ona-inventory-lead-panel">
                <div className="ona-inventory-lead-title"><span>Buyer Information</span>{selectedLead ? <small>{formatAdminDate(selectedLead.created_at)}</small> : null}</div>
                {selectedLead ? (
                  <>
                    <h4>{selectedLead.name}</h4>
                    <dl>
                      <div><dt>Phone</dt><dd>{selectedLead.phone}</dd></div>
                      <div><dt>Email</dt><dd>{selectedLead.email || 'Not provided'}</dd></div>
                      <div><dt>Request</dt><dd>{humanize(selectedLead.source.replace('cityview_', ''))}</dd></div>
                      <div><dt>Lead status</dt><dd>{humanize(selectedLead.status)}</dd></div>
                    </dl>
                    <button type="button" onClick={() => { window.history.pushState({}, '', `/admin/enquiries`); window.dispatchEvent(new Event('ona:navigate')); }}>Open buyer enquiry</button>
                  </>
                ) : (
                  <div className="ona-inventory-empty-lead"><House size={26} strokeWidth={1.4} /><p>No City View buyer has submitted interest for this residence yet.</p></div>
                )}
              </div>
            </>
          ) : null}
        </aside>
      </div>
    </div>
  );
}
