"use client";

import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Fix for default marker icons in Leaflet + Next.js
const DefaultIcon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

interface MapPickerProps {
  onLocationSelect?: (lat: number, lng: number) => void;
  initialPosition?: [number, number];
  markers?: Array<{ lat: number; lng: number; title?: string }>;
}

const LocationMarker = ({ onSelect }: { onSelect: (lat: number, lng: number) => void }) => {
  const [position, setPosition] = useState<L.LatLng | null>(null);
  
  useMapEvents({
    click(e) {
      setPosition(e.latlng);
      onSelect(e.latlng.lat, e.latlng.lng);
    },
  });

  return position === null ? null : (
    <Marker position={position}>
      <Popup>Selected Location</Popup>
    </Marker>
  );
};

export const EliteMap = ({ onLocationSelect, initialPosition = [17.3850, 78.4867], markers = [] }: MapPickerProps) => {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) return <div className="w-full h-full bg-slate-900 animate-pulse rounded-xl" />;

  return (
    <div className="w-full h-full rounded-xl overflow-hidden border border-white/[0.06] shadow-2xl relative z-0">
      <MapContainer
        center={initialPosition}
        zoom={13}
        scrollWheelZoom={true}
        style={{ height: "100%", width: "100%", background: "#0f172a" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          className="map-tiles-dark"
        />
        
        {onLocationSelect && <LocationMarker onSelect={onLocationSelect} />}
        
        {markers.map((marker, idx) => (
          <Marker key={idx} position={[marker.lat, marker.lng]}>
            <Popup>{marker.title || `Marker ${idx + 1}`}</Popup>
          </Marker>
        ))}
      </MapContainer>
      
      {/* Visual Overlay for Cyber-Noir vibe */}
      <div className="absolute inset-0 pointer-events-none border-[12px] border-black/10 mix-blend-overlay z-10" />
      <style jsx global>{`
        .leaflet-container {
          filter: grayscale(1) invert(0.9) hue-rotate(200deg) brightness(0.8);
        }
        .leaflet-touch .leaflet-bar {
          border: 1px solid rgba(255, 255, 255, 0.1) !important;
          background: rgba(15, 23, 42, 0.8) !important;
          backdrop-filter: blur(10px);
        }
        .leaflet-touch .leaflet-bar a {
          color: #fff !important;
          background: transparent !important;
        }
      `}</style>
    </div>
  );
};

export default EliteMap;
