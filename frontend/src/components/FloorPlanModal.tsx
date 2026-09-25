import React, { useEffect, useState } from 'react';
import { X, ZoomIn, ZoomOut, RotateCcw } from 'lucide-react';
import { ResidenceTypology } from '../types';
import { ONA_IMAGES, ImageKey } from '../data/images';

interface FloorPlanModalProps {
  typology: ResidenceTypology | null;
  isOpen: boolean;
  onClose: () => void;
}

export const FloorPlanModal: React.FC<FloorPlanModalProps> = ({ typology, isOpen, onClose }) => {
  const [zoomLevel, setZoomLevel] = useState<number>(1);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleKeyDown);
    } else {
      document.body.style.overflow = 'auto';
    }

    return () => {
      document.body.style.overflow = 'auto';
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen || !typology) return null;

  const handleZoomIn = () => setZoomLevel((prev) => Math.min(prev + 0.25, 2.5));
  const handleZoomOut = () => setZoomLevel((prev) => Math.max(prev - 0.25, 0.75));
  const handleResetZoom = () => setZoomLevel(1);

  return (
    <div
      id="floor-plan-modal-backdrop"
      className="fixed inset-0 z-50 bg-[#302A26]/95 backdrop-blur-xl flex flex-col justify-between overflow-hidden animate-fade-in"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-typology-title"
    >
      {/* Modal Header */}
      <div className="w-full bg-[#38312C] border-b border-[#403832] px-6 sm:px-10 py-5 flex items-center justify-between z-10">
        <div>
          <span className="font-sans text-[11px] font-semibold tracking-[0.24em] text-[#A58A71] uppercase block">
            Architectural Blueprint
          </span>
          <h2 id="modal-typology-title" className="font-display text-xl sm:text-2xl text-[#F5F0EA] font-light">
            {typology.name} &middot; {typology.areaDisplay}
          </h2>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-3">
          <div className="hidden sm:flex items-center space-x-2 bg-[#302A26] border border-[#403832] px-3 py-1.5 rounded-sm">
            <button
              onClick={handleZoomOut}
              className="p-1 text-[#CFC2B7] hover:text-[#FFFFFF] transition-colors cursor-pointer"
              title="Zoom Out"
              aria-label="Zoom Out"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <span className="font-sans text-xs text-[#E7DED6] px-1 font-mono">
              {Math.round(zoomLevel * 100)}%
            </span>
            <button
              onClick={handleZoomIn}
              className="p-1 text-[#CFC2B7] hover:text-[#FFFFFF] transition-colors cursor-pointer"
              title="Zoom In"
              aria-label="Zoom In"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
            <button
              onClick={handleResetZoom}
              className="p-1 text-[#CFC2B7] hover:text-[#FFFFFF] transition-colors ml-1 border-l border-[#403832] pl-2 cursor-pointer"
              title="Reset View"
              aria-label="Reset View"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>

          <button
            id="close-floor-plan-modal"
            onClick={onClose}
            className="p-2.5 bg-[#302A26] hover:bg-[#A58A71] text-[#FFFFFF] transition-colors rounded-sm border border-[#403832] focus:outline-none cursor-pointer"
            aria-label="Close Fullscreen Floor Plan"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Modal Main Content */}
      <div className="flex-1 overflow-y-auto lg:overflow-hidden grid grid-cols-1 lg:grid-cols-12 p-6 sm:p-10 gap-8 items-center bg-[#302A26]">
        {/* Floor Plan Visual Area */}
        <div className="lg:col-span-8 h-full flex items-center justify-center bg-[#F3EEE7] p-6 sm:p-10 border border-[#403832] relative overflow-hidden rounded-sm shadow-2xl">
          <div
            style={{
              transform: `scale(${zoomLevel})`,
              transition: 'transform 0.2s cubic-bezier(0.16, 1, 0.3, 1)',
            }}
            className="w-full max-w-2xl origin-center"
          >
            <img src={ONA_IMAGES[typology.planKey as ImageKey]} alt={`${typology.name} floor plan`} className="w-full h-auto max-h-[70vh] object-contain" />
          </div>

          <div className="absolute bottom-4 right-4 bg-[#302A26]/95 border border-[#A58A71]/50 backdrop-blur-sm text-[#F5F0EA] text-[10px] font-sans tracking-widest px-3 py-1.5 uppercase rounded-sm">
            {typology.code} &middot; {typology.areaDisplay}
          </div>
        </div>

        {/* Breakdown Inspector */}
        <div className="lg:col-span-4 bg-[#38312C] border border-[#403832] p-6 sm:p-8 h-full overflow-y-auto space-y-6 rounded-sm shadow-xl">
          <div>
            <span className="font-sans text-xs font-semibold tracking-[0.2em] text-[#A58A71] uppercase block mb-1">
              {typology.code}
            </span>
            <h3 className="font-display text-2xl text-[#F5F0EA] font-light mb-2">
              {typology.name}
            </h3>
            <p className="font-sans text-sm text-[#E7DED6] leading-relaxed font-light">
              {typology.description}
            </p>
          </div>

          {/* Quick Metrics */}
          <div className="py-4 border-y border-[#403832] space-y-3">
            <div>
              <span className="font-sans text-[10px] tracking-wider text-[#CFC2B7] uppercase block">
                Bedrooms
              </span>
              <span className="font-display text-2xl text-[#F5F0EA] font-light">
                {typology.bedrooms} Bedrooms
              </span>
            </div>
            <div>
              <span className="font-sans text-[10px] tracking-wider text-[#CFC2B7] uppercase block">
                Approximate Total Area
              </span>
              <span className="font-display text-2xl text-[#A58A71] font-light">
                {typology.areaDisplay}
              </span>
            </div>
          </div>

          {/* Features List */}
          <div className="pt-2">
            <p className="font-sans text-xs font-semibold tracking-widest text-[#A58A71] uppercase mb-3">
              Confirmed Features
            </p>
            <ul className="space-y-2 text-xs text-[#E7DED6]">
              {typology.features.map((feat, i) => (
                <li key={i} className="flex items-start space-x-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#A58A71] mt-1 flex-shrink-0" />
                  <span>{feat}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="pt-4 border-t border-[#403832]">
            <p className="font-sans text-[11px] text-[#CFC2B7] italic">
              Approximate areas and architectural schematic representation.
            </p>
          </div>
        </div>
      </div>

      {/* Modal Footer */}
      <div className="w-full bg-[#38312C] border-t border-[#403832] px-6 sm:px-10 py-4 flex items-center justify-between text-xs text-[#E7DED6] z-10 font-sans">
        <span className="tracking-wider">
          ONA Towers &middot; Mazizini, Zanzibar &middot; {typology.name}
        </span>
        <span className="text-[#A58A71] font-semibold tracking-widest uppercase">
          Press ESC to Exit Fullscreen
        </span>
      </div>
    </div>
  );
};
