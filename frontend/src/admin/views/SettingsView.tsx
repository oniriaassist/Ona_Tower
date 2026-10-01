import React, { useEffect, useState } from 'react';
import {
  AlertCircle,
  CheckCircle2,
  KeyRound,
  Mail,
  Phone,
  RefreshCw,
  Save,
  Send,
  ShieldCheck,
  UserRound,
} from 'lucide-react';
import {
  changeMyPassword,
  getAdminEmailStatus,
  sendAdminEmailTest,
  updateMyProfile,
  type AdminEmailStatus,
  type AdminUser,
} from '../../api/admin';
import { ErrorBanner, FieldLabel, PageLoader, inputClass } from '../components';

type Tab = 'profile' | 'security' | 'email';

export function SettingsView({ currentUser, onUserChanged }: { currentUser: AdminUser; onUserChanged: (user: AdminUser) => void }) {
  const [tab, setTab] = useState<Tab>('profile');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(false);
  }, []);

  if (loading) return <PageLoader label="Loading settings" />;

  return (
    <div className="mx-auto max-w-[1250px] space-y-6">
      <section className="overflow-hidden rounded-[24px] border border-[#DED6CF] bg-[#FBF9F7] shadow-sm">
        <div className="border-b border-[#E5DDD6] px-5 sm:px-8">
          <nav className="flex gap-1 overflow-x-auto py-3" aria-label="Settings sections">
            <TabButton active={tab === 'profile'} onClick={() => setTab('profile')} icon={UserRound}>Profile</TabButton>
            <TabButton active={tab === 'security'} onClick={() => setTab('security')} icon={KeyRound}>Security</TabButton>
            <TabButton active={tab === 'email'} onClick={() => setTab('email')} icon={Mail}>Email</TabButton>
          </nav>
        </div>

        <div className="p-5 sm:p-8">
          {tab === 'profile' ? <ProfilePanel user={currentUser} onUserChanged={onUserChanged} /> : null}
          {tab === 'security' ? <SecurityPanel /> : null}
          {tab === 'email' ? <EmailPanel user={currentUser} /> : null}
        </div>
      </section>
    </div>
  );
}

function TabButton({ active, onClick, icon: Icon, children }: { active: boolean; onClick: () => void; icon: React.ElementType; children: React.ReactNode }) {
  return <button type="button" onClick={onClick} className={`flex shrink-0 items-center gap-2 rounded-lg px-4 py-2.5 text-xs font-semibold transition ${active ? 'bg-[#EDE5DE] text-[#493E35]' : 'text-[#82776F] hover:bg-[#F3EEE9]'}`}><Icon className="h-4 w-4" />{children}</button>;
}

function Avatar({ name }: { name: string }) {
  const initials = name.split(/\s+/).filter(Boolean).slice(0, 2).map((part) => part[0]?.toUpperCase()).join('') || 'OA';
  return <div className="grid h-14 w-14 place-items-center rounded-full border border-[#D9CFC6] bg-[#EEE6DF] text-sm font-semibold text-[#7B614E]">{initials}</div>;
}

function PanelHeading({ eyebrow, title, copy }: { eyebrow: string; title: string; copy: string }) {
  return <div className="mb-7"><p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-[#9B7F66]">{eyebrow}</p><h3 className="mt-1 font-serif text-2xl text-[#2C2723]">{title}</h3><p className="mt-2 max-w-2xl text-sm leading-6 text-[#7D736B]">{copy}</p></div>;
}

function ProfilePanel({ user, onUserChanged }: { user: AdminUser; onUserChanged: (user: AdminUser) => void }) {
  const [name, setName] = useState(user.name);
  const [email, setEmail] = useState(user.email);
  const [phone, setPhone] = useState(user.phone || '');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [saved, setSaved] = useState(false);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault(); setSaving(true); setError(''); setSaved(false);
    try {
      const updated = await updateMyProfile({ name, email, phone: phone || null });
      onUserChanged(updated); setSaved(true);
    } catch (err) { setError(err instanceof Error ? err.message : 'Unable to save profile.'); }
    finally { setSaving(false); }
  };

  return (
    <form onSubmit={submit} className="max-w-4xl">
      <div className="mb-7">
        <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-[#9B7F66]">Profile</p>
        <h3 className="mt-1 font-serif text-2xl text-[#2C2723]">Profile Settings</h3>
      </div>
      <div className="mb-6 flex flex-col gap-4 rounded-2xl border border-[#E2DAD3] bg-white p-5 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-4">
          <Avatar name={user.name} />
          <div>
            <p className="text-sm font-semibold text-[#2F2924]">{user.name}</p>
            <p className="mt-1 text-xs text-[#7D736B]">{user.is_super_admin ? 'Administrator' : 'Staff'}</p>
            <p className="mt-1 text-xs italic text-[#8D837A]">{user.email}</p>
          </div>
        </div>
      </div>
      {error ? <div className="mb-5"><ErrorBanner message={error} /></div> : null}
      {saved ? <Success message="Profile changes saved." /> : null}
      <div className="grid gap-5 sm:grid-cols-2">
        <label><FieldLabel>Full name</FieldLabel><input required className={inputClass} value={name} onChange={(e) => setName(e.target.value)} /></label>
        <label><FieldLabel>Staff email</FieldLabel><div className="relative"><Mail className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-[#9B8F86]" /><input required type="email" className={`${inputClass} pl-10`} value={email} onChange={(e) => setEmail(e.target.value)} /></div></label>
        <label><FieldLabel>Phone number</FieldLabel><div className="relative"><Phone className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-[#9B8F86]" /><input className={`${inputClass} pl-10`} value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="+255 ..." /></div></label>
        <label><FieldLabel>Job title / role</FieldLabel><input disabled className={inputClass} value={user.role} /></label>
      </div>
      <div className="mt-7 flex justify-end border-t border-[#E8E1DB] pt-5"><button type="submit" disabled={saving} className="inline-flex items-center gap-2 rounded-xl bg-[#2A241F] px-5 py-3 text-xs font-semibold uppercase tracking-[0.14em] text-white disabled:opacity-60"><Save className="h-4 w-4" />{saving ? 'Saving…' : 'Save changes'}</button></div>
    </form>
  );
}

function SecurityPanel() {
  const [current, setCurrent] = useState('');
  const [next, setNext] = useState('');
  const [confirm, setConfirm] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  const submit = async (event: React.FormEvent) => {
    event.preventDefault(); setError(''); setMessage('');
    if (next !== confirm) { setError('New password and confirmation do not match.'); return; }
    setSaving(true);
    try {
      const result = await changeMyPassword({ current_password: current, new_password: next, confirm_password: confirm });
      setMessage(result.message); setCurrent(''); setNext(''); setConfirm('');
    } catch (err) { setError(err instanceof Error ? err.message : 'Unable to update password.'); }
    finally { setSaving(false); }
  };

  return (
    <form onSubmit={submit} className="max-w-3xl">
      <PanelHeading eyebrow="Security" title="Change password" copy="Use your current password to create a new password for this staff account. Passwords are stored as secure hashes rather than plain text." />
      {error ? <div className="mb-5"><ErrorBanner message={error} /></div> : null}
      {message ? <Success message={message} /> : null}
      <div className="space-y-5">
        <label className="block"><FieldLabel>Current password</FieldLabel><input required type="password" className={inputClass} value={current} onChange={(e) => setCurrent(e.target.value)} autoComplete="current-password" /></label>
        <div className="grid gap-5 sm:grid-cols-2">
          <label><FieldLabel>New password</FieldLabel><input required type="password" minLength={8} className={inputClass} value={next} onChange={(e) => setNext(e.target.value)} autoComplete="new-password" /></label>
          <label><FieldLabel>Confirm new password</FieldLabel><input required type="password" minLength={8} className={inputClass} value={confirm} onChange={(e) => setConfirm(e.target.value)} autoComplete="new-password" /></label>
        </div>
      </div>
      <div className="mt-7 flex items-center justify-between gap-5 border-t border-[#E8E1DB] pt-5"><div className="flex items-center gap-2 text-xs text-[#82776F]"><ShieldCheck className="h-4 w-4 text-emerald-700" /> Minimum 8 characters.</div><button type="submit" disabled={saving} className="rounded-xl bg-[#2A241F] px-5 py-3 text-xs font-semibold uppercase tracking-[0.14em] text-white disabled:opacity-60">{saving ? 'Updating…' : 'Update password'}</button></div>
    </form>
  );
}


function EmailPanel({ user }: { user: AdminUser }) {
  const [status, setStatus] = useState<AdminEmailStatus | null>(null);
  const [recipient, setRecipient] = useState(user.email);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      setStatus(await getAdminEmailStatus());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load email delivery status.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void load(); }, []);

  const sendTest = async (event: React.FormEvent) => {
    event.preventDefault();
    setSending(true);
    setError('');
    setMessage('');
    try {
      const result = await sendAdminEmailTest(recipient.trim());
      setMessage(result.message);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to send the test email.');
    } finally {
      setSending(false);
    }
  };

  if (loading && !status) return <PageLoader label="Checking email delivery" />;

  return (
    <div className="max-w-4xl">
      <PanelHeading
        eyebrow="Transactional email"
        title="Customer auto-replies"
        copy="Verify the production email provider used for enquiry acknowledgements and staff notifications. Secrets remain in the server environment and are never shown here."
      />
      {error ? <div className="mb-5"><ErrorBanner message={error} /></div> : null}
      {message ? <Success message={message} /> : null}

      {status ? (
        <>
          <div className={`mb-6 rounded-2xl border p-5 ${status.ready ? 'border-emerald-200 bg-emerald-50' : 'border-amber-200 bg-amber-50'}`}>
            <div className="flex items-start gap-3">
              {status.ready ? <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-emerald-700" /> : <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-amber-700" />}
              <div>
                <p className={`text-sm font-semibold ${status.ready ? 'text-emerald-900' : 'text-amber-900'}`}>
                  {status.ready ? 'Email delivery is ready' : 'Email delivery needs configuration'}
                </p>
                <p className={`mt-1 text-xs leading-5 ${status.ready ? 'text-emerald-800' : 'text-amber-800'}`}>Provider: {status.provider}</p>
              </div>
            </div>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <StatusItem label="Delivery enabled" ok={status.enabled} />
            <StatusItem label="Sender configured" ok={status.from_configured} />
            {status.provider === 'resend' ? <StatusItem label={`Resend sender domain${status.from_domain ? ` (${status.from_domain})` : ''}`} ok={status.resend_domain_match} /> : null}
            <StatusItem label="Staff recipient configured" ok={status.staff_recipient_configured} />
            <StatusItem label="City View URL configured" ok={status.cityview_url_configured} />
          </div>

          <div className="mt-5 rounded-2xl border border-[#E2DAD3] bg-white p-5">
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-[#8C7561]">City View link</p>
            <a href={status.cityview_url} target="_blank" rel="noreferrer" className="mt-2 block break-all text-sm text-[#735B48] underline decoration-[#C6AA91] underline-offset-4">{status.cityview_url}</a>
          </div>

          {status.issues.length ? (
            <div className="mt-5 rounded-2xl border border-amber-200 bg-amber-50 p-5">
              <p className="text-xs font-semibold uppercase tracking-[0.12em] text-amber-900">Configuration notes</p>
              <ul className="mt-3 list-disc space-y-2 pl-5 text-sm leading-5 text-amber-900">
                {status.issues.map((issue) => <li key={issue}>{issue}</li>)}
              </ul>
            </div>
          ) : null}

          <form onSubmit={sendTest} className="mt-6 rounded-2xl border border-[#E2DAD3] bg-white p-5">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm font-semibold text-[#2F2924]">Send a production test email</p>
                <p className="mt-1 text-xs leading-5 text-[#7D736B]">This calls the same backend delivery transport used by customer enquiry acknowledgements.</p>
              </div>
              <button type="button" onClick={() => void load()} className="rounded-lg border border-[#DDD3CB] p-2 text-[#75695F]" aria-label="Refresh email status"><RefreshCw className="h-4 w-4" /></button>
            </div>
            <div className="mt-4 flex flex-col gap-3 sm:flex-row">
              <input required type="email" className={`${inputClass} flex-1`} value={recipient} onChange={(event) => setRecipient(event.target.value)} placeholder="you@example.com" />
              <button type="submit" disabled={sending || !status.ready || !user.is_super_admin} className="inline-flex items-center justify-center gap-2 rounded-xl bg-[#2A241F] px-5 py-3 text-xs font-semibold uppercase tracking-[0.12em] text-white disabled:cursor-not-allowed disabled:opacity-50">
                <Send className="h-4 w-4" />{sending ? 'Sending…' : 'Send test'}
              </button>
            </div>
            {!user.is_super_admin ? <p className="mt-3 text-xs text-[#8D837A]">Only an administrator can send a production test email.</p> : null}
          </form>
        </>
      ) : null}
    </div>
  );
}

function StatusItem({ label, ok }: { label: string; ok: boolean }) {
  return (
    <div className="flex items-center justify-between rounded-xl border border-[#E5DDD6] bg-[#FBF9F7] px-4 py-3">
      <span className="text-xs font-medium text-[#665E57]">{label}</span>
      <span className={`rounded-full px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.1em] ${ok ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}`}>{ok ? 'Ready' : 'Missing'}</span>
    </div>
  );
}


function Success({ message }: { message: string }) {
  return <div className="mb-5 flex items-center gap-2 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800"><CheckCircle2 className="h-4 w-4" />{message}</div>;
}
