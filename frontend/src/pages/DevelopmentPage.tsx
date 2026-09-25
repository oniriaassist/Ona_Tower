import React from "react";
import ArchitectureSection from "../components/ArchitectureSection";
import Development from "../components/Development";
import OnaIdea from "../components/OnaIdea";
import "../styles/ona-redesign.css";

export const DevelopmentPage: React.FC = () => (
  <div className="ona-story-page">
    <OnaIdea />
    <Development />
    <ArchitectureSection />
  </div>
);
