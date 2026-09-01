"use client";

import React, { useEffect } from "react";
import { useJalnetraStore } from "../../store/useJalnetraStore";
import { ShieldCheck, MapPin, AlertCircle, Navigation, CheckCircle2 } from "lucide-react";

export default function ResponderApp() {
  const {
    incidents,
    isConnected,
    fetchInitialData,
    updateIncidentStatus
  } = useJalnetraStore();

  useEffect(() => {
    fetchInitialData();
  }, [fetchInitialData]);

  // Ensure incidents array exists and sort by timestamp
  const activeIncidents = [...(incidents || [])].sort((a, b) => 
    new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );

  const getStatusColor = (status: string) => {
    switch(status) {
      case 'NEW': return 'bg-error-container text-on-error-container border-error';
      case 'ACCEPT': 
      case 'ACKNOWLEDGED': return 'bg-tertiary-container text-on-tertiary-container border-tertiary';
      case 'EN_ROUTE': return 'bg-primary-container text-on-primary-container border-primary';
      case 'RESOLVED': return 'bg-surface-variant text-on-surface-variant border-outline';
      default: return 'bg-surface text-on-surface border-outline-variant';
    }
  };

  const advanceStatus = (id: string, currentStatus: string) => {
    let nextStatus = 'ACKNOWLEDGED';
    if (currentStatus === 'NEW') nextStatus = 'ACKNOWLEDGED';
    else if (currentStatus === 'ACKNOWLEDGED') nextStatus = 'EN_ROUTE';
    else if (currentStatus === 'EN_ROUTE') nextStatus = 'RESOLVED';
    
    updateIncidentStatus(id, nextStatus);
  };

  return (
    <div className="bg-surface text-on-surface font-body-md min-h-screen w-screen flex flex-col overflow-y-auto">
      <header className="bg-tertiary text-on-tertiary p-4 flex justify-between items-center sticky top-0 z-50 shadow-md">
        <div className="flex items-center gap-3">
          <ShieldCheck size={28} />
          <div>
            <h1 className="font-headline-md font-bold leading-none">JALNETRA</h1>
            <span className="text-label-sm opacity-80">FIELD RESPONDER</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
           <span className="text-label-sm font-bold opacity-80">{isConnected ? 'LIVE' : 'OFFLINE'}</span>
           <span className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-500 animate-pulse'}`}></span>
        </div>
      </header>

      <main className="p-4 flex flex-col gap-4 max-w-lg mx-auto w-full pb-8">
        <h2 className="font-label-lg font-bold text-on-surface-variant flex items-center gap-2 mb-2">
          <AlertCircle size={20} />
          ACTIVE INCIDENTS ({activeIncidents.filter(i => i.status !== 'RESOLVED').length})
        </h2>

        {activeIncidents.length === 0 ? (
          <div className="bg-surface-container border border-outline-variant p-8 rounded-2xl flex flex-col items-center justify-center text-center mt-10">
            <CheckCircle2 size={64} className="text-green-500 mb-4 opacity-80" />
            <h3 className="font-headline-md font-bold mb-1">All Clear</h3>
            <span className="font-body-md text-on-surface-variant">No active incidents in your sector.</span>
          </div>
        ) : (
          activeIncidents.map((incident: any) => {
            const status = incident.status || 'NEW';
            const isResolved = status === 'RESOLVED';

            return (
            <div key={incident.id} className={`p-5 rounded-2xl shadow-md border-l-4 transition-all ${getStatusColor(status)} ${isResolved ? 'opacity-60' : ''}`}>
              <div className="flex justify-between items-start mb-2">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`text-label-sm font-bold px-2 py-0.5 rounded ${status === 'NEW' ? 'bg-error text-on-error' : 'bg-surface text-on-surface'}`}>
                      {status}
                    </span>
                    <span className="text-label-sm font-bold opacity-70">
                      {new Date(incident.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                    </span>
                  </div>
                  <h3 className="font-headline-sm font-bold">SOS #{incident.id.slice(0, 6).toUpperCase()}</h3>
                </div>
              </div>
              
              <div className="mt-3 flex flex-col gap-2">
                <div className="flex items-start gap-2">
                  <MapPin size={18} className="mt-0.5 opacity-70" />
                  <div>
                    <div className="text-label-sm font-bold opacity-70">LOCATION</div>
                    <div className="font-bold">{incident.location?.lat.toFixed(4)}, {incident.location?.lng.toFixed(4)}</div>
                  </div>
                </div>

                <div className="bg-surface/50 p-3 rounded-lg mt-1 border border-outline/20">
                  <div className="text-label-sm font-bold opacity-70 mb-1">DETAILS</div>
                  <div className="font-body-md">{incident.message}</div>
                </div>
              </div>
              
              {!isResolved && (
                <div className="mt-4 pt-4 border-t border-outline/20 flex gap-3">
                  <button 
                    onClick={() => advanceStatus(incident.id, status)}
                    className="flex-1 bg-surface text-on-surface py-3 rounded-xl font-bold flex justify-center items-center gap-2 shadow-sm hover:bg-surface-variant transition-colors"
                  >
                    <CheckCircle2 size={20} className={status === 'EN_ROUTE' ? 'text-green-500' : ''} />
                    {status === 'NEW' ? 'ACCEPT' : status === 'ACKNOWLEDGED' ? 'EN ROUTE' : 'RESOLVE'}
                  </button>
                  <button 
                    onClick={() => {
                      if (incident.location) {
                        window.open(`https://maps.google.com/?q=${incident.location.lat},${incident.location.lng}`, '_blank');
                      } else {
                        alert("Location data unavailable");
                      }
                    }}
                    className="flex-1 bg-surface/30 border border-outline/40 py-3 rounded-xl font-bold flex justify-center items-center gap-2 hover:bg-surface/50 transition-colors"
                  >
                    <Navigation size={20} />
                    MAP
                  </button>
                </div>
              )}
            </div>
          )})
        )}
      </main>
    </div>
  );
}
