import React, { useEffect } from "react";

import { AdminApp } from "./admin/AdminApp";
import { recordPageVisit } from "./api/analytics";

import Footer from "./components/Footer";
import Header from "./components/Header";

import BrochurePage from "./pages/BrochurePage";
import CommercialPage from "./pages/CommercialPage";
import { DevelopmentPage } from "./pages/DevelopmentPage";
import EnquirePage from "./pages/EnquirePage";
import { HomePage } from "./pages/HomePage";
import LifestylePage from "./pages/LifestylePage";
import { LocationPage } from "./pages/LocationPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import ResidencesPage from "./pages/ResidencesPage";

import { usePathname } from "./routing";

import "./styles/admin-premium.css";

const pageTitles: Record<string, string> = {
  "/": "ONA Towers — Zanzibar | Live above. See beyond.",
  "/residences": "Residences | ONA Towers Zanzibar",
  "/development": "Our Story | ONA Towers Zanzibar",
  "/lifestyle": "Life at ONA | ONA Towers Zanzibar",
  "/commercial": "ONA House | ONA Towers Zanzibar",
  "/location": "Location | ONA Towers Zanzibar",
  "/brochure": "Project Brochure | ONA Towers Zanzibar",
  "/enquire": "Contact | ONA Towers Zanzibar",
};

export function App() {
  const pathname = usePathname();

  useEffect(() => {
    document.title = pathname.startsWith("/admin")
      ? "Administration | ONA Towers"
      : pageTitles[pathname] || "ONA Towers Zanzibar";

    window.scrollTo({
      top: 0,
      behavior: "auto",
    });

    if (!pathname.startsWith("/admin")) {
      void recordPageVisit(pathname);
    }
  }, [pathname]);

  if (
    pathname === "/admin" ||
    pathname.startsWith("/admin/")
  ) {
    return (
      <div className="ona-admin-premium-shell">
        <AdminApp pathname={pathname} />
      </div>
    );
  }

  let page: React.ReactNode;

  switch (pathname) {
    case "/":
      page = <HomePage />;
      break;

    case "/residences":
      page = <ResidencesPage />;
      break;

    case "/development":
      page = <DevelopmentPage />;
      break;

    case "/lifestyle":
      page = <LifestylePage />;
      break;

    case "/commercial":
      page = <CommercialPage />;
      break;

    case "/location":
      page = <LocationPage />;
      break;

    case "/brochure":
      page = <BrochurePage />;
      break;

    case "/enquire":
      page = <EnquirePage />;
      break;

    default:
      page = <NotFoundPage />;
  }

  return (
    <div className="relative min-h-screen bg-[#302A26] text-[#E7DED6] overflow-x-hidden selection:bg-[#A58A71] selection:text-[#FFFFFF]">
      <Header />

      <main
        id="main-content"
        tabIndex={-1}
        className="focus:outline-none"
      >
        {page}
      </main>

      <Footer />
    </div>
  );
}

export default App;