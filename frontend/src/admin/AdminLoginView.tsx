import type {
  FormEvent,
} from "react";

import {
  ArrowRight,
  Eye,
  EyeOff,
  LockKeyhole,
  ShieldCheck,
} from "lucide-react";

type AdminLoginViewProps = {
  email: string;
  password: string;
  showPassword: boolean;
  loading: boolean;
  error?: string | null;

  onEmailChange: (
    value: string,
  ) => void;

  onPasswordChange: (
    value: string,
  ) => void;

  onTogglePassword: () => void;

  onSubmit: (
    event: FormEvent<HTMLFormElement>,
  ) => void;

  onForgotPassword: () => void;
};

export default function AdminLoginView({
  email,
  password,
  showPassword,
  loading,
  error,
  onEmailChange,
  onPasswordChange,
  onTogglePassword,
  onSubmit,
  onForgotPassword,
}: AdminLoginViewProps) {
  return (
    <section className="ona-admin-login">
      <div
        className="ona-admin-login-background"
        aria-hidden="true"
      >
        <img
          src="/ona-assets/hero/towers-sunset.webp"
          alt=""
        />

        <div className="ona-admin-login-background-overlay" />

        <div className="ona-admin-login-background-glow" />
      </div>

      <div className="ona-admin-login-frame">
        <aside className="ona-admin-login-story">
          <div className="ona-admin-login-story-top">
            <div className="ona-admin-private-label">
              <span className="ona-admin-private-icon">
                <ShieldCheck
                  size={17}
                  strokeWidth={1.45}
                />
              </span>

              <span>
                Private staff workspace
              </span>
            </div>

            <a
              href="/"
              className="ona-admin-brand"
              aria-label="ONA Towers home"
            >
              <span className="ona-admin-brand-main">
                ÔNA
              </span>

              <span className="ona-admin-brand-sub">
                TOWERS
              </span>
            </a>
          </div>

          <div className="ona-admin-login-story-copy">
            <p className="ona-admin-script">
              Live above. See beyond.
            </p>

            <h1>
              A composed space
              <br />
              to manage every
              <br />
              <em>
                customer conversation.
              </em>
            </h1>

            <p className="ona-admin-story-description">
              Secure access for the ONA team
              to review enquiries, coordinate
              follow-up and manage the customer
              journey from one private workspace.
            </p>
          </div>

          <div className="ona-admin-staff-only">
            <span className="ona-admin-staff-dot" />

            <span>
              Staff accounts only
            </span>
          </div>
        </aside>

        <section className="ona-admin-login-panel">
          <div className="ona-admin-login-panel-inner">
            <div className="ona-admin-access-pill">
              <span className="ona-admin-access-dot" />

              <span>
                Staff access
              </span>
            </div>

            <header className="ona-admin-login-heading">
              <span>
                Administration
              </span>

              <h2>
                Welcome
                <br />
                <em>back.</em>
              </h2>

              <p>
                Sign in with your staff email
                and password to continue to the
                ONA administration workspace.
              </p>
            </header>

            <form
              className="ona-admin-login-form"
              onSubmit={onSubmit}
            >
              <div className="ona-admin-login-field">
                <label htmlFor="adminEmail">
                  Staff email
                </label>

                <input
                  id="adminEmail"
                  type="email"
                  value={email}
                  onChange={(event) =>
                    onEmailChange(
                      event.target.value,
                    )
                  }
                  autoComplete="email"
                  required
                  placeholder="name@company.com"
                />
              </div>

              <div className="ona-admin-login-field">
                <label htmlFor="adminPassword">
                  Password
                </label>

                <div className="ona-admin-password-control">
                  <input
                    id="adminPassword"
                    type={
                      showPassword
                        ? "text"
                        : "password"
                    }
                    value={password}
                    onChange={(event) =>
                      onPasswordChange(
                        event.target.value,
                      )
                    }
                    autoComplete="current-password"
                    required
                    placeholder="Enter your password"
                  />

                  <button
                    type="button"
                    className="ona-admin-password-toggle"
                    onClick={
                      onTogglePassword
                    }
                    aria-label={
                      showPassword
                        ? "Hide password"
                        : "Show password"
                    }
                  >
                    {showPassword ? (
                      <EyeOff
                        size={19}
                        strokeWidth={1.5}
                      />
                    ) : (
                      <Eye
                        size={19}
                        strokeWidth={1.5}
                      />
                    )}
                  </button>
                </div>

                <div className="ona-admin-forgot-row">
                  <button
                    type="button"
                    className="ona-admin-forgot-link"
                    onClick={
                      onForgotPassword
                    }
                  >
                    Forgot password?
                  </button>
                </div>
              </div>

              {error && (
                <div
                  className="ona-admin-login-error"
                  role="alert"
                >
                  {error}
                </div>
              )}

              <button
                type="submit"
                className="ona-admin-signin-button"
                disabled={loading}
              >
                <span>
                  {loading
                    ? "Signing in..."
                    : "Sign in"}
                </span>

                <ArrowRight
                  size={17}
                  strokeWidth={1.5}
                  aria-hidden="true"
                />
              </button>
            </form>

            <div className="ona-admin-security-note">
              <span className="ona-admin-security-icon">
                <LockKeyhole
                  size={18}
                  strokeWidth={1.45}
                />
              </span>

              <p>
                Access is limited to active
                staff accounts created by an
                administrator. Customer pages
                remain separate from this
                private workspace.
              </p>
            </div>
          </div>
        </section>
      </div>
    </section>
  );
}