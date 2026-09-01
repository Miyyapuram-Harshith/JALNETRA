"use client";

import React, { useEffect, useState } from "react";
import { useJalnetraStore } from "../../store/useJalnetraStore";
import { jalnetraAPI } from "../../lib/api";
import JalnetraMap from "../../components/JalnetraMap";
import { Menu, X, Activity, Server, Database, CloudRain, Wifi, Send } from "lucide-react";

export default function CommandCenter() {
  const {
    risk,
    impact,
    routes,
    systemHealth,
    networkStatus,
    dataFreshness,
    timeline,
    mapLayers,
    fetchInitialData,
    setTimeline,
    toggleMapLayer,
  } = useJalnetraStore();

  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  useEffect(() => {
    fetchInitialData();
  }, [fetchInitialData]);

  const maxRisk = risk?.zones?.[0] || { 
    risk_level: "NORMAL", 
    risk_probability: 0, 
    estimated_onset_minutes: 0,
    confidence: { level: "HIGH", reason: "All systems nominal" },
    risk_drivers: []
  };

  const safeDeparture = routes?.safe_departure || {};
  const isDemo = systemHealth?.demo_mode || false;
  
  const handleStartDemo = async () => await jalnetraAPI.startDemo();
  const handleIncreaseRainfall = async () => await jalnetraAPI.increaseRainfall();
  const handleSendWhatsApp = async () => {
    if (confirm("Send WhatsApp Alert to all affected citizens?")) {
      await jalnetraAPI.sendWhatsAppAlert({});
    }
  };
  const handleFailSensor = async () => await jalnetraAPI.failSensor();
  const handleCloseRoad = async () => await jalnetraAPI.closeRoad();
  const handleNetworkDegrade = async () => await jalnetraAPI.degradeNetwork();
  const handleReset = async () => await jalnetraAPI.resetDemo();

  return (
    <div className="bg-background text-on-background font-body-md h-screen w-screen overflow-hidden flex flex-col">
      {/* TopAppBar */}
      <header className="flex justify-between items-center w-full px-4 md:px-8 h-16 z-50 bg-surface border-b border-outline-variant shrink-0 shadow-sm">
        <div className="flex items-center gap-4 md:gap-6">
          <button className="md:hidden" onClick={() => setIsSidebarOpen(!isSidebarOpen)}>
            {isSidebarOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
          <h1 className="font-headline-md text-headline-md font-bold text-primary">JALNETRA</h1>
          <div className="hidden md:flex items-center gap-2 border-l border-outline-variant pl-6">
            <span className={`flex items-center gap-1 font-label-sm text-label-sm px-2 py-1 rounded ${networkStatus === 'ONLINE' ? 'bg-primary-container text-on-primary-container' : 'bg-error-container text-on-error-container'}`}>
              <span className={`w-2 h-2 rounded-full ${networkStatus === 'ONLINE' ? 'bg-primary' : 'bg-error animate-pulse'}`}></span>
              STATUS: {networkStatus}
            </span>
            <span className="font-label-md text-label-md text-on-surface-variant px-2 py-1 rounded border border-outline-variant">
              REGION: Hilly Village Alpha
            </span>
            {isDemo && (
              <span className="font-label-md text-label-md text-tertiary bg-tertiary-fixed px-2 py-1 rounded">
                DEMO ENVIRONMENT
              </span>
            )}
          </div>
        </div>
        <div className="flex items-center gap-4 md:gap-6">
          <div className="flex items-center gap-4 text-on-surface-variant font-mono-data text-mono-data">
            <span className="hidden sm:inline">Data Freshness: {dataFreshness}s</span>
          </div>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden relative">
        {/* Responsive SideNavBar */}
        <nav className={`${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0 absolute md:relative z-40 transition-transform duration-300 ease-in-out flex flex-col py-4 w-[340px] h-full overflow-y-auto bg-surface border-r border-outline-variant shrink-0 shadow-xl md:shadow-none`}>
          <div className="px-4 mb-6 flex flex-col gap-4">
            
            {/* System Health */}
            <div className="data-card rounded-xl p-4 flex flex-col gap-2">
              <span className="font-label-md font-bold text-on-surface mb-1">SYSTEM HEALTH</span>
              <div className="grid grid-cols-2 gap-2 text-label-sm">
                <div className="flex items-center gap-2"><Server size={14} className={systemHealth ? 'text-green-600' : 'text-error'}/> API</div>
                <div className="flex items-center gap-2"><Database size={14} className={systemHealth ? 'text-green-600' : 'text-error'}/> DB</div>
                <div className="flex items-center gap-2"><Activity size={14} className={systemHealth ? 'text-green-600' : 'text-error'}/> AI ENGINE</div>
                <div className="flex items-center gap-2"><CloudRain size={14} className={systemHealth?.weather_api_connected ? 'text-green-600' : 'text-error'}/> WEATHER</div>
                <div className="flex items-center gap-2"><Wifi size={14} className={networkStatus === 'ONLINE' ? 'text-green-600' : 'text-error'}/> SENSORS</div>
              </div>
            </div>

            {/* Risk Intelligence */}
            <div className="data-card rounded-xl p-4 flex flex-col gap-2 relative overflow-hidden">
              <div className={`absolute top-0 left-0 w-1 h-full ${maxRisk.risk_level === 'NORMAL' ? 'bg-green-500' : maxRisk.risk_level === 'WATCH' ? 'bg-yellow-500' : 'bg-error'}`}></div>
              <div className="flex justify-between items-start pl-2">
                <span className="font-label-md font-bold text-on-surface flex items-center gap-2">
                  <Activity size={18} /> RISK INTELLIGENCE
                </span>
                <span className={`text-label-sm font-bold px-2 py-0.5 rounded ${maxRisk.risk_level === 'NORMAL' ? 'bg-green-100 text-green-800' : 'bg-error-container text-on-error-container'}`}>
                  {maxRisk.risk_level}
                </span>
              </div>
              <div className="mt-2 text-display-lg font-bold pl-2 leading-none" style={{ color: maxRisk.risk_level === 'NORMAL' ? '#16a34a' : 'var(--color-error)' }}>
                {Math.round(maxRisk.risk_probability * 100)}%
              </div>
              
              <div className="mt-3 pt-3 border-t border-outline-variant pl-2">
                <div className="text-label-sm font-bold text-on-surface-variant mb-1">EXPLAINABLE RISK DRIVERS</div>
                {maxRisk.risk_drivers && maxRisk.risk_drivers.length > 0 ? (
                  <ul className="text-label-sm list-disc pl-4 text-on-surface">
                    {maxRisk.risk_drivers.map((driver: any, i: number) => (
                      <li key={i}>{driver.factor}: {driver.value}</li>
                    ))}
                  </ul>
                ) : (
                  <span className="text-label-sm text-on-surface-variant">Conditions are stable.</span>
                )}
              </div>

              {/* Confidence Engine */}
              <div className="mt-3 pt-3 border-t border-outline-variant pl-2">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-label-sm font-bold text-on-surface-variant">SENSOR CONFIDENCE</span>
                  <span className={`text-label-sm font-bold ${maxRisk.confidence?.level === 'HIGH' ? 'text-green-600' : 'text-error'}`}>{maxRisk.confidence?.level || 'UNKNOWN'}</span>
                </div>
                <div className="text-label-sm text-on-surface-variant">{maxRisk.confidence?.reason || 'No data'}</div>
              </div>
            </div>

            {/* Projected Impact */}
            <div className="data-card rounded-xl p-4 flex flex-col gap-2">
              <span className="font-label-md font-bold text-on-surface">PROJECTED IMPACT</span>
              <div className="flex justify-between py-1">
                <span className="text-label-sm">Population Affected</span>
                <span className="font-bold">{impact?.affected_population || 0}</span>
              </div>
              <div className="flex justify-between py-1 border-t border-outline-variant/50">
                <span className="text-label-sm">Roads Threatened</span>
                <span className="font-bold text-error">{impact?.threatened_roads?.length || 0}</span>
              </div>
              <div className="flex justify-between py-1 border-t border-outline-variant/50">
                <span className="text-label-sm">Shelters Accessible</span>
                <span className="font-bold">{impact?.accessible_shelters?.length || 0}</span>
              </div>
            </div>

            {/* Safe Departure Window */}
            <div className="data-card rounded-xl p-4 flex flex-col gap-2 bg-secondary-container/10 border border-secondary shadow-md relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-1 bg-secondary"></div>
              <span className="font-label-md font-bold text-secondary">MODELED DEPARTURE WINDOW</span>
              <div className="text-display-lg font-bold text-secondary leading-none my-1">
                {safeDeparture?.safe_departure_window_minutes ?? '--'} MIN
              </div>
              <div className="text-label-sm text-on-surface-variant italic mb-2">Modeled Estimate</div>
              <div className="flex flex-col gap-1 text-label-sm bg-surface-container-low p-2 rounded">
                <div className="flex justify-between"><span>Hazard Arrival:</span><span className="font-bold">{safeDeparture?.hazard_arrival_minutes ?? '--'} MIN</span></div>
                <div className="flex justify-between"><span>Travel Time:</span><span className="font-bold">{safeDeparture?.travel_time_minutes ?? '--'} MIN</span></div>
                <div className="flex justify-between"><span>Safety Buffer:</span><span className="font-bold">{safeDeparture?.safety_buffer_minutes ?? '--'} MIN</span></div>
              </div>
              <div className="mt-2 pt-2 border-t border-secondary/20">
                <div className="text-label-sm font-bold text-secondary mb-1">RECOMMENDATION:</div>
                <div className="text-label-md font-bold text-on-surface">PROCEED TO {safeDeparture?.recommended_shelter_name || 'N/A'}</div>
                <div className="text-label-sm text-on-surface-variant font-bold">VIA {safeDeparture?.recommended_route?.route_name || 'N/A'}</div>
              </div>
            </div>

            {/* WhatsApp Actions */}
            <div className="mt-2">
               <button onClick={handleSendWhatsApp} className="w-full bg-[#25D366] text-white py-3 rounded-xl flex items-center justify-center gap-2 font-bold hover:bg-[#128C7E] transition-colors shadow-md">
                  <Send size={18} />
                  SEND WHATSAPP ALERT
               </button>
            </div>

            {/* Demo Controls */}
            <div className="data-card rounded-xl p-4 flex flex-col gap-2 mt-4 bg-tertiary-container/10 border-tertiary-container">
              <h3 className="font-label-sm font-bold text-tertiary">JURY SCENARIO CONTROLS</h3>
              <div className="grid grid-cols-2 gap-2 mt-2">
                <button onClick={handleStartDemo} className="bg-primary text-on-primary py-1.5 rounded text-label-sm font-bold">START DEMO</button>
                <button onClick={handleReset} className="bg-error text-on-error py-1.5 rounded text-label-sm font-bold">RESET</button>
                <button onClick={handleIncreaseRainfall} className="bg-surface-variant text-on-surface-variant py-1.5 rounded text-label-sm border border-outline">Rain++</button>
                <button onClick={handleCloseRoad} className="bg-surface-variant text-on-surface-variant py-1.5 rounded text-label-sm border border-outline">Close Road</button>
                <button onClick={handleFailSensor} className="bg-surface-variant text-on-surface-variant py-1.5 rounded text-label-sm border border-outline">Fail Sensor</button>
                <button onClick={handleNetworkDegrade} className="bg-surface-variant text-on-surface-variant py-1.5 rounded text-label-sm border border-outline">Net Fail</button>
              </div>
            </div>

          </div>
        </nav>

        {/* Central Map Area */}
        <main className="flex-1 relative bg-surface-variant overflow-hidden flex flex-col">
          <div className="flex-1 relative">
            <JalnetraMap />
            
            {/* Map Layers Control Overlay */}
            <div className="absolute top-4 right-4 bg-surface/90 backdrop-blur p-3 rounded-xl shadow-lg border border-outline-variant z-10 flex flex-col gap-2">
              <span className="font-label-sm font-bold mb-1">LAYERS</span>
              <label className="flex items-center gap-2 text-label-sm cursor-pointer hover:text-primary">
                <input type="checkbox" checked={mapLayers.flood} onChange={() => toggleMapLayer('flood')} className="rounded"/>
                Flood Prediction
              </label>
              <label className="flex items-center gap-2 text-label-sm cursor-pointer hover:text-primary">
                <input type="checkbox" checked={mapLayers.route} onChange={() => toggleMapLayer('route')} className="rounded"/>
                Safe Routes
              </label>
              <label className="flex items-center gap-2 text-label-sm cursor-pointer hover:text-primary">
                <input type="checkbox" checked={mapLayers.sensors} onChange={() => toggleMapLayer('sensors')} className="rounded"/>
                Sensors
              </label>
            </div>
          </div>
          
          {/* Temporal Simulation Bottom Bar */}
          <div className="h-24 bg-surface border-t border-outline-variant flex items-center px-6 z-10 shrink-0">
            <div className="flex-1 max-w-4xl mx-auto flex flex-col gap-2">
              <div className="flex justify-between text-label-sm font-bold text-on-surface-variant">
                <span>TEMPORAL FLOOD SIMULATION</span>
                <span className="text-primary">{timeline === 0 ? 'NOW' : `+${timeline} MIN`}</span>
              </div>
              <input 
                type="range" 
                min="0" max="60" step="10" 
                value={timeline} 
                onChange={(e) => setTimeline(parseInt(e.target.value))}
                className="w-full h-2 bg-surface-variant rounded-lg appearance-none cursor-pointer accent-primary"
              />
              <div className="flex justify-between text-label-sm text-outline mt-1 px-1">
                <span>NOW</span>
                <span>+10</span>
                <span>+20</span>
                <span>+30</span>
                <span>+40</span>
                <span>+50</span>
                <span>+60</span>
              </div>
            </div>
          </div>
        </main>

        {/* Overlay for mobile sidebar */}
        {isSidebarOpen && (
          <div className="absolute inset-0 bg-black/50 z-30 md:hidden" onClick={() => setIsSidebarOpen(false)}></div>
        )}
      </div>
    </div>
  );
}
