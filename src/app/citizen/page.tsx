"use client";

import React, { useEffect, useState } from "react";
import { useJalnetraStore } from "../../store/useJalnetraStore";
import { jalnetraAPI } from "../../lib/api";
import { AlertTriangle, Navigation2, PhoneCall, Clock, MapPin, ShieldAlert } from "lucide-react";

export default function CitizenApp() {
  const {
    risk,
    routes,
    isConnected,
    fetchInitialData,
  } = useJalnetraStore();

  const [sosSent, setSosSent] = useState(false);

  useEffect(() => {
    fetchInitialData();
  }, [fetchInitialData]);

  const maxRisk = risk?.zones?.[0] || { risk_level: "NORMAL", risk_probability: 0 };
  const safeDeparture = routes?.safe_departure || {};
  
  const handleSOS = async () => {
    try {
      setSosSent(true);
      await jalnetraAPI.triggerSOS({
        latitude: 30.4480,
        longitude: 78.0780,
        message: "Emergency triggered from Citizen App",
        people_count: 1,
        medical_needed: false,
      });
      setTimeout(() => alert("SOS SENT - Responders Notified. Please stay calm and follow evacuation orders."), 500);
    } catch (e) {
      alert("SOS FAILED - Try calling local emergency line");
      setSosSent(false);
    }
  };

  const isDanger = maxRisk.risk_level === 'WARNING' || maxRisk.risk_level === 'EVACUATE' || maxRisk.risk_level === 'CRITICAL';
  
  return (
    <div className={`font-body-md min-h-screen w-screen flex flex-col transition-colors duration-500 ${isDanger ? 'bg-error text-on-error' : 'bg-surface text-on-surface'}`}>
      {/* Header */}
      <header className={`p-4 flex justify-between items-center shadow-md z-50 ${isDanger ? 'bg-error-container text-on-error-container' : 'bg-primary text-on-primary'}`}>
        <div className="flex items-center gap-2">
          <ShieldAlert size={24} />
          <h1 className="font-headline-md font-bold">JALNETRA Citizen</h1>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-label-sm font-bold opacity-80">{isConnected ? 'LIVE' : 'OFFLINE'}</span>
          <span className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500 animate-pulse'}`}></span>
        </div>
      </header>

      <main className="flex-1 p-4 flex flex-col gap-4 max-w-md mx-auto w-full">
        {/* Current Risk */}
        <div className={`p-6 rounded-2xl shadow-xl flex flex-col items-center justify-center text-center transition-all ${isDanger ? 'bg-error-container text-on-error-container border-2 border-red-400 animate-pulse-slow' : 'bg-surface-container border border-outline-variant'}`}>
          <AlertTriangle size={48} className={`mb-2 ${isDanger ? 'text-error' : 'text-green-500'}`} />
          <h2 className="font-label-lg font-bold opacity-80 mb-1">YOUR CURRENT RISK</h2>
          <div className="text-display-lg font-bold tracking-tight leading-none mb-2">
            {maxRisk.risk_level}
          </div>
          {maxRisk.estimated_onset_minutes > 0 && (
            <div className={`font-label-md font-bold px-4 py-2 rounded-full mt-2 ${isDanger ? 'bg-error text-on-error' : 'bg-surface-variant text-on-surface-variant'}`}>
              Impact in ~{maxRisk.estimated_onset_minutes} MIN
            </div>
          )}
        </div>

        {/* Evacuation Route (Only show if there is a recommendation) */}
        {safeDeparture.recommended_route && (
          <div className={`p-5 rounded-2xl shadow-lg border ${isDanger ? 'bg-surface text-on-surface border-transparent' : 'bg-secondary-container/20 border-secondary'}`}>
            <h2 className={`font-label-md font-bold flex items-center gap-2 mb-4 ${isDanger ? 'text-error' : 'text-secondary'}`}>
              <Navigation2 size={20} />
              RECOMMENDED ACTION
            </h2>
            
            <div className="flex flex-col gap-4">
              <div className="flex items-start gap-3">
                <MapPin size={24} className="mt-1 opacity-70" />
                <div>
                  <div className="text-label-sm font-bold opacity-70">DESTINATION</div>
                  <div className="text-headline-md font-bold leading-tight">{safeDeparture.recommended_shelter_name}</div>
                  <div className="text-body-md font-bold opacity-80 mt-1">Via {safeDeparture.recommended_route.route_name}</div>
                </div>
              </div>

              <div className={`mt-2 p-4 rounded-xl flex items-center justify-between ${isDanger ? 'bg-error-container text-on-error-container' : 'bg-secondary text-on-secondary'}`}>
                <div className="flex items-center gap-2">
                  <Clock size={24} />
                  <span className="font-label-md font-bold">MODELED DEPARTURE WINDOW</span>
                </div>
                <div className="text-display-md font-bold leading-none">
                  {safeDeparture.safe_departure_window_minutes}m
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="mt-auto pt-6 pb-4 flex flex-col gap-4">
          <button 
            onClick={() => {
              if (safeDeparture.recommended_shelter_name) {
                alert(`Starting navigation to ${safeDeparture.recommended_shelter_name} via ${safeDeparture.recommended_route.route_name}`);
              } else {
                alert("No safe route available at this time.");
              }
            }}
            className={`py-4 rounded-xl font-headline-md font-bold w-full shadow-lg flex justify-center items-center gap-3 transition-transform active:scale-95 ${isDanger ? 'bg-surface text-error hover:bg-surface-variant' : 'bg-secondary text-on-secondary hover:bg-secondary/90'}`}>
            <Navigation2 size={24} />
            START NAVIGATION
          </button>
          
          <button 
            onClick={handleSOS} 
            disabled={sosSent}
            className={`py-4 rounded-xl font-headline-md font-bold w-full shadow-lg flex justify-center items-center gap-3 transition-transform active:scale-95 ${sosSent ? 'bg-surface-variant text-on-surface-variant opacity-70' : isDanger ? 'bg-red-800 text-white border-2 border-red-500' : 'bg-error text-on-error hover:bg-error/90'}`}
          >
            <PhoneCall size={24} className={sosSent ? '' : 'animate-bounce'} />
            {sosSent ? 'SOS TRANSMITTED' : 'REQUEST EMERGENCY HELP'}
          </button>
        </div>
      </main>
    </div>
  );
}
