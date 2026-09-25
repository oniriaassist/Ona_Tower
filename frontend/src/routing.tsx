import React, { useEffect, useState } from 'react';

export type SitePath =
  | '/'
  | '/residences'
  | '/development'
  | '/lifestyle'
  | '/commercial'
  | '/location'
  | '/brochure'
  | '/enquire';

const NAVIGATE_EVENT = 'ona:navigate';

export function normalizePath(pathname: string): string {
  if (!pathname || pathname === '/') return '/';
  return `/${pathname.replace(/^\/+|\/+$/g, '')}`;
}

export function navigate(to: string) {
  const nextPath = normalizePath(to);
  if (normalizePath(window.location.pathname) === nextPath) {
    window.scrollTo({ top: 0, behavior: 'smooth' });
    return;
  }

  window.history.pushState({}, '', nextPath);
  window.dispatchEvent(new Event(NAVIGATE_EVENT));
}

export function usePathname() {
  const [pathname, setPathname] = useState(() => normalizePath(window.location.pathname));

  useEffect(() => {
    const sync = () => setPathname(normalizePath(window.location.pathname));
    window.addEventListener('popstate', sync);
    window.addEventListener(NAVIGATE_EVENT, sync);
    return () => {
      window.removeEventListener('popstate', sync);
      window.removeEventListener(NAVIGATE_EVENT, sync);
    };
  }, []);

  return pathname;
}

interface SiteLinkProps extends Omit<React.AnchorHTMLAttributes<HTMLAnchorElement>, 'href'> {
  to: string;
}

export const SiteLink: React.FC<SiteLinkProps> = ({ to, onClick, children, ...props }) => (
  <a
    href={to}
    {...props}
    onClick={(event) => {
      onClick?.(event);
      if (
        event.defaultPrevented ||
        event.button !== 0 ||
        event.metaKey ||
        event.ctrlKey ||
        event.shiftKey ||
        event.altKey
      ) {
        return;
      }
      event.preventDefault();
      navigate(to);
    }}
  >
    {children}
  </a>
);
