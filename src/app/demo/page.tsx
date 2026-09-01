"use client";

import React, { useEffect } from "react";
import { useJalnetraStore } from "../../store/useJalnetraStore";
import { jalnetraAPI } from "../../lib/api";

export default function DemoControl() {
  const { systemHealth, fetchInitialData } = useJalnetraStore();

  useEffect(() => {
    fetchInitialData();
  }, [fetchInitialData]);

  const handleStartDemo = async () => await jalnetraAPI.startDemo();
  const handleIncreaseRainfall = async () => await jalnetraAPI.increaseRainfall();
  const handleFailSensor = async () => await jalnetraAPI.failSensor();
  const handleCloseRoad = async () => await jalnetraAPI.closeRoad();
  const handleNetworkDegrade = async () => await jalnetraAPI.degradeNetwork();
  const handleReset = async () => await jalnetraAPI.resetDemo();

  return (
    <div className="bg-background text-on-background min-h-screen p-8">
      <h1 className="text-display-lg font-bold mb-8">JALNETRA DEMO CONTROL</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="data-card p-6 rounded-xl flex flex-col gap-4">
          <h2 className="font-headline-md font-bold">Scenario Control</h2>
          <button onClick={handleStartDemo} className="bg-primary text-on-primary py-3 rounded font-bold">START JURY DEMO</button>
          <button onClick={handleReset} className="bg-error text-on-error py-3 rounded font-bold">RESET SCENARIO</button>
        </div>

        <div className="data-card p-6 rounded-xl flex flex-col gap-4">
          <h2 className="font-headline-md font-bold">Environment Actions</h2>
          <button onClick={handleIncreaseRainfall} className="bg-surface-variant text-on-surface-variant py-3 rounded font-bold border border-outline">INCREASE RAINFALL</button>
          <button onClick={handleCloseRoad} className="bg-surface-variant text-on-surface-variant py-3 rounded font-bold border border-outline">CLOSE ROAD</button>
        </div>

        <div className="data-card p-6 rounded-xl flex flex-col gap-4">
          <h2 className="font-headline-md font-bold">System Failures</h2>
          <button onClick={handleFailSensor} className="bg-surface-variant text-on-surface-variant py-3 rounded font-bold border border-outline">FAIL SENSOR</button>
          <button onClick={handleNetworkDegrade} className="bg-surface-variant text-on-surface-variant py-3 rounded font-bold border border-outline">DEGRADE NETWORK</button>
        </div>
      </div>
    </div>
  );
}
