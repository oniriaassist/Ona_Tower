import React, {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  ArrowLeft,
  ArrowRight,
  Eye,
  EyeOff,
  Inbox,
  LayoutDashboard,
  LogOut,
  Menu,
  Settings,
  ShieldCheck,
  UsersRound,
  X,
} from "lucide-react";

import {
  adminLogin,
  clearAdminSession,
  getAdminToken,
  getStoredAdminUser,
  requestPasswordReset,
  verifyAdminSession,
  type AdminUser,
} from "../api/admin";

import { navigate } from "../routing";

import {
  ErrorBanner,
  PageLoader,
  inputClass,
} from "./components";

import { OverviewView } from "./views/OverviewView";
import { EnquiriesView } from "./views/EnquiriesView";
import { TeamView } from "./views/TeamView";
import { SettingsView } from "./views/SettingsView";

import "../styles/admin-premium.css";

type AdminSection =
  | "overview"
  | "enquiries"
  | "team"
  | "settings";

function sectionFromPath(
  pathname: string,
): AdminSection {
  if (
    pathname.startsWith(
      "/admin/enquiries",
    )
  ) {
    return "enquiries";
  }

  if (
    pathname.startsWith(
      "/admin/team",
    )
  ) {
    return "team";
  }

  if (
    pathname.startsWith(
      "/admin/settings",
    )
  ) {
    return "settings";
  }

  return "overview";
}

const labels: Record<
  AdminSection,
  {
    title: string;
    subtitle: string;
  }
> = {
  overview: {
    title: "Overview",
    subtitle:
      "Customer activity, enquiries and team performance in one place.",
  },

  enquiries: {
    title: "Enquiries",
    subtitle:
      "Review, assign and progress requests submitted from the customer website.",
  },

  team: {
    title: "Team",
    subtitle:
      "Manage staff accounts, responsibilities and enquiry assignment access.",
  },

  settings: {
    title: "Settings",
    subtitle:
      "Manage your profile, security and administration preferences.",
  },
};

const navItems: Array<{
  key: AdminSection;
  label: string;
  path: string;
  icon: React.ElementType;
}> = [
  {
    key: "overview",
    label: "Overview",
    path: "/admin",
    icon: LayoutDashboard,
  },

  {
    key: "enquiries",
    label: "Enquiries",
    path: "/admin/enquiries",
    icon: Inbox,
  },

  {
    key: "team",
    label: "Team",
    path: "/admin/team",
    icon: UsersRound,
  },

  {
    key: "settings",
    label: "Settings",
    path: "/admin/settings",
    icon: Settings,
  },
];

export function AdminApp({
  pathname,
}: {
  pathname: string;
}) {
  const [authState, setAuthState] =
    useState<
      | "checking"
      | "signedOut"
      | "signedIn"
    >(
      getAdminToken()
        ? "checking"
        : "signedOut",
    );

  const [user, setUser] =
    useState<AdminUser | null>(
      getStoredAdminUser(),
    );

  const [
    mobileOpen,
    setMobileOpen,
  ] = useState(false);

  const section = useMemo(
    () =>
      sectionFromPath(pathname),
    [pathname],
  );

  useEffect(() => {
    if (!getAdminToken()) {
      setAuthState("signedOut");
      return;
    }

    let active = true;

    verifyAdminSession()
      .then((result) => {
        if (!active) {
          return;
        }

        setUser(result.user);

        setAuthState(
          "signedIn",
        );
      })
      .catch(() => {
        if (!active) {
          return;
        }

        clearAdminSession();

        setUser(null);

        setAuthState(
          "signedOut",
        );
      });

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  if (
    authState === "checking"
  ) {
    return (
      <div className="ona-admin-loading">
        <div className="ona-admin-loading-inner">
          <AdminBrand />

          <PageLoader label="Preparing your administration workspace" />
        </div>
      </div>
    );
  }

  if (
    authState === "signedOut" ||
    !user
  ) {
    return (
      <AdminLogin
        onSignedIn={(
          nextUser,
        ) => {
          setUser(nextUser);

          setAuthState(
            "signedIn",
          );
        }}
      />
    );
  }

  const current =
    labels[section];

  const handleLogout = () => {
    clearAdminSession();

    setUser(null);

    setAuthState(
      "signedOut",
    );

    navigate("/admin");
  };

  return (
    <div className="ona-admin-workspace">
      <aside className="ona-admin-sidebar">
        <AdminBrand />

        <div className="ona-admin-sidebar-rule" />

        <nav
          className="ona-admin-navigation"
          aria-label="Administration navigation"
        >
          {navItems.map(
            (item) => {
              const active =
                item.key ===
                section;

              const Icon =
                item.icon;

              return (
                <button
                  type="button"
                  key={
                    item.key
                  }
                  onClick={() =>
                    navigate(
                      item.path,
                    )
                  }
                  className={[
                    "ona-admin-nav-item",
                    active
                      ? "is-active"
                      : "",
                  ].join(" ")}
                >
                  <Icon
                    size={18}
                    strokeWidth={
                      1.5
                    }
                  />

                  <span>
                    {
                      item.label
                    }
                  </span>
                </button>
              );
            },
          )}
        </nav>

        <div className="ona-admin-sidebar-account">
          <div className="ona-admin-account-card">
            <div className="ona-admin-account-person">
              <Avatar
                name={
                  user.name
                }
              />

              <div>
                <strong>
                  {
                    user.name
                  }
                </strong>

                <span>
                  {
                    user.role
                  }
                </span>
              </div>
            </div>

            <button
              type="button"
              className="ona-admin-logout"
              onClick={
                handleLogout
              }
            >
              <LogOut
                size={15}
                strokeWidth={
                  1.5
                }
              />

              <span>
                Sign out
              </span>
            </button>
          </div>
        </div>
      </aside>

      {mobileOpen ? (
        <div
          className="ona-admin-mobile-backdrop"
          onMouseDown={() =>
            setMobileOpen(
              false,
            )
          }
        >
          <aside
            className="ona-admin-mobile-drawer"
            onMouseDown={(
              event,
            ) =>
              event.stopPropagation()
            }
          >
            <div className="ona-admin-mobile-top">
              <AdminBrand />

              <button
                type="button"
                className="ona-admin-icon-button"
                onClick={() =>
                  setMobileOpen(
                    false,
                  )
                }
                aria-label="Close menu"
              >
                <X
                  size={20}
                  strokeWidth={
                    1.5
                  }
                />
              </button>
            </div>

            <div className="ona-admin-sidebar-rule" />

            <nav className="ona-admin-navigation">
              {navItems.map(
                (item) => {
                  const Icon =
                    item.icon;

                  const active =
                    item.key ===
                    section;

                  return (
                    <button
                      type="button"
                      key={
                        item.key
                      }
                      onClick={() =>
                        navigate(
                          item.path,
                        )
                      }
                      className={[
                        "ona-admin-nav-item",
                        active
                          ? "is-active"
                          : "",
                      ].join(
                        " ",
                      )}
                    >
                      <Icon
                        size={18}
                        strokeWidth={
                          1.5
                        }
                      />

                      <span>
                        {
                          item.label
                        }
                      </span>
                    </button>
                  );
                },
              )}
            </nav>

            <div className="ona-admin-mobile-account">
              <div className="ona-admin-account-card">
                <div className="ona-admin-account-person">
                  <Avatar
                    name={
                      user.name
                    }
                  />

                  <div>
                    <strong>
                      {
                        user.name
                      }
                    </strong>

                    <span>
                      {
                        user.role
                      }
                    </span>
                  </div>
                </div>

                <button
                  type="button"
                  className="ona-admin-logout"
                  onClick={
                    handleLogout
                  }
                >
                  <LogOut
                    size={15}
                    strokeWidth={
                      1.5
                    }
                  />

                  Sign out
                </button>
              </div>
            </div>
          </aside>
        </div>
      ) : null}

      <div className="ona-admin-main">
        <header className="ona-admin-topbar">
          <button
            type="button"
            className="ona-admin-menu-button"
            onClick={() =>
              setMobileOpen(
                true,
              )
            }
            aria-label="Open menu"
          >
            <Menu
              size={20}
              strokeWidth={
                1.5
              }
            />
          </button>

          <div className="ona-admin-page-title">
            <span className="ona-admin-page-kicker">
              ONA administration
            </span>

            <div className="ona-admin-page-title-row">
              <h1>
                {
                  current.title
                }
              </h1>

              {user.is_super_admin ? (
                <span className="ona-admin-role-badge">
                  Administrator
                </span>
              ) : null}
            </div>

            <p>
              {
                current.subtitle
              }
            </p>
          </div>

          <div className="ona-admin-alert-card">
            <span>
              Alerts
            </span>

            <strong>
              0
            </strong>

            <i />
          </div>
        </header>

        <main className="ona-admin-content">
          {section ===
          "overview" ? (
            <OverviewView />
          ) : null}

          {section ===
          "enquiries" ? (
            <EnquiriesView />
          ) : null}

          {section ===
          "team" ? (
            <TeamView
              currentUser={
                user
              }
            />
          ) : null}

          {section ===
          "settings" ? (
            <SettingsView
              currentUser={
                user
              }
              onUserChanged={
                setUser
              }
            />
          ) : null}
        </main>
      </div>
    </div>
  );
}

function AdminBrand() {
  return (
    <div className="ona-admin-brand-wrap">
      <button
        type="button"
        className="ona-admin-brand"
        onClick={() =>
          navigate("/admin")
        }
        aria-label="Go to administration overview"
      >
        <span className="ona-admin-brand-main">
          ÔNA
        </span>

        <span className="ona-admin-brand-sub">
          TOWERS
        </span>
      </button>
    </div>
  );
}

function Avatar({
  name,
  large = false,
}: {
  name: string;
  large?: boolean;
}) {
  const initials =
    name
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map(
        (part) =>
          part[0]?.toUpperCase(),
      )
      .join("") || "OA";

  return (
    <div
      className={[
        "ona-admin-avatar",
        large
          ? "ona-admin-avatar--large"
          : "",
      ].join(" ")}
    >
      {initials}
    </div>
  );
}

function AdminLogin({
  onSignedIn,
}: {
  onSignedIn: (
    user: AdminUser,
  ) => void;
}) {
  const [mode, setMode] =
    useState<
      "login" | "forgot"
    >("login");

  const [email, setEmail] =
    useState(
      import.meta.env
        .VITE_ADMIN_EMAIL ||
        "",
    );

  const [
    password,
    setPassword,
  ] = useState("");

  const [
    showPassword,
    setShowPassword,
  ] = useState(false);

  const [error, setError] =
    useState("");

  const [message, setMessage] =
    useState("");

  const [
    submitting,
    setSubmitting,
  ] = useState(false);

  const submit = async (
    event: React.FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    setError("");
    setMessage("");
    setSubmitting(true);

    try {
      if (
        mode === "forgot"
      ) {
        const result =
          await requestPasswordReset(
            email.trim(),
          );

        setMessage(
          result.message,
        );
      } else {
        const result =
          await adminLogin(
            email.trim(),
            password,
          );

        onSignedIn(
          result.user,
        );
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to continue.",
      );
    } finally {
      setSubmitting(false);
    }
  };

  const openForgot =
    () => {
      setMode("forgot");

      setError("");

      setMessage("");
    };

  const backToLogin =
    () => {
      setMode("login");

      setError("");

      setMessage("");
    };

  return (
    <div className="ona-admin-login-page">
      <div className="ona-admin-login-shell">
        <aside className="ona-admin-login-brand-panel">
          <div
            className="ona-admin-login-image"
            aria-hidden="true"
          >
            <img
              src="/ona-assets/hero/towers-sunset.webp"
              alt=""
            />

            <div />
          </div>

          <div className="ona-admin-login-brand-content">
            <div className="ona-admin-login-top">
              <div className="ona-admin-private-workspace">
                <span className="ona-admin-private-icon">
                  <ShieldCheck
                    size={17}
                    strokeWidth={
                      1.4
                    }
                  />
                </span>

                <span>
                  Private staff
                  workspace
                </span>
              </div>

              <button
                type="button"
                className="ona-admin-login-logo"
                onClick={() =>
                  navigate(
                    "/admin",
                  )
                }
                aria-label="Go to administration overview"
              >
                <span>
                  ÔNA
                </span>

                <small>
                  TOWERS
                </small>
              </button>
            </div>

            <div className="ona-admin-login-story">
              <p className="ona-admin-login-script">
                Live above.
                See beyond.
              </p>

              <h1>
                A focused place
                to manage every

                <em>
                  customer
                  conversation.
                </em>
              </h1>

              <p className="ona-admin-login-story-text">
                Review enquiries,
                coordinate
                follow-up and
                manage each
                customer journey
                from one private
                ONA workspace.
              </p>

              <div className="ona-admin-staff-label">
                <span />

                Staff accounts
                only
              </div>
            </div>
          </div>
        </aside>

        <main className="ona-admin-login-form-panel">
          <div className="ona-admin-login-form-inner">
            <div className="ona-admin-login-mobile-brand">
              <AdminBrand />
            </div>

            {mode ===
            "login" ? (
              <>
                <div className="ona-admin-login-access">
                  <span />

                  Staff access
                </div>

                <header className="ona-admin-login-heading">
                  <span>
                    Administration
                  </span>

                  <h2>
                    Welcome{" "}
                    <em>
                      back.
                    </em>
                  </h2>

                  <p>
                    Sign in with
                    your staff
                    email and
                    password to
                    continue to
                    the ONA
                    administration
                    workspace.
                  </p>
                </header>
              </>
            ) : (
              <>
                <button
                  type="button"
                  className="ona-admin-back-button"
                  onClick={
                    backToLogin
                  }
                >
                  <ArrowLeft
                    size={16}
                    strokeWidth={
                      1.5
                    }
                  />

                  Back to sign in
                </button>

                <div className="ona-admin-login-access">
                  <span />

                  Secure recovery
                </div>

                <header className="ona-admin-login-heading">
                  <span>
                    Account access
                  </span>

                  <h2>
                    Reset{" "}
                    <em>
                      access.
                    </em>
                  </h2>

                  <p>
                    Enter your
                    staff email to
                    request a
                    password reset
                    from an
                    administrator.
                  </p>
                </header>
              </>
            )}

            <form
              className="ona-admin-login-form"
              onSubmit={submit}
            >
              <label className="ona-admin-field">
                <span>
                  Staff email
                </span>

                <input
                  type="email"
                  required
                  autoComplete="email"
                  value={email}
                  onChange={(
                    event,
                  ) =>
                    setEmail(
                      event.target
                        .value,
                    )
                  }
                  className={
                    inputClass
                  }
                  placeholder="name@company.com"
                />
              </label>

              {mode ===
              "login" ? (
                <div className="ona-admin-field">
                  <label htmlFor="admin-password">
                    Password
                  </label>

                  <div className="ona-admin-password-wrap">
                    <input
                      id="admin-password"
                      type={
                        showPassword
                          ? "text"
                          : "password"
                      }
                      required
                      autoComplete="current-password"
                      value={
                        password
                      }
                      onChange={(
                        event,
                      ) =>
                        setPassword(
                          event
                            .target
                            .value,
                        )
                      }
                      className={
                        inputClass
                      }
                      placeholder="Enter your password"
                    />

                    <button
                      type="button"
                      className="ona-admin-password-toggle"
                      onClick={() =>
                        setShowPassword(
                          (
                            value,
                          ) =>
                            !value,
                        )
                      }
                      aria-label={
                        showPassword
                          ? "Hide password"
                          : "Show password"
                      }
                    >
                      {showPassword ? (
                        <EyeOff
                          size={
                            18
                          }
                          strokeWidth={
                            1.5
                          }
                        />
                      ) : (
                        <Eye
                          size={
                            18
                          }
                          strokeWidth={
                            1.5
                          }
                        />
                      )}
                    </button>
                  </div>

                  <div className="ona-admin-forgot-row">
                    <button
                      type="button"
                      onClick={
                        openForgot
                      }
                    >
                      Forgot
                      password?
                    </button>
                  </div>
                </div>
              ) : null}

              {error ? (
                <ErrorBanner
                  message={
                    error
                  }
                />
              ) : null}

              {message ? (
                <div className="ona-admin-success-message">
                  {
                    message
                  }
                </div>
              ) : null}

              <button
                type="submit"
                disabled={
                  submitting
                }
                className="ona-admin-primary-button"
              >
                <span>
                  {submitting
                    ? "Please wait..."
                    : mode ===
                        "login"
                      ? "Sign in"
                      : "Send reset request"}
                </span>

                {!submitting ? (
                  <ArrowRight
                    size={
                      16
                    }
                    strokeWidth={
                      1.5
                    }
                  />
                ) : null}
              </button>
            </form>

            <div className="ona-admin-security-note">
              <ShieldCheck
                size={17}
                strokeWidth={
                  1.4
                }
              />

              <p>
                Access is limited
                to active staff
                accounts created
                by an
                administrator.
                Customer pages
                remain separate
                from this private
                workspace.
              </p>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
