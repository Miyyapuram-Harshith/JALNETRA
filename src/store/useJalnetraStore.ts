import { create } from "zustand";
import { jalnetraAPI, WS_BASE } from "../lib/api";

interface JalnetraState {
  risk: any;
  propagation: any;
  impact: any;
  routes: any;
  sensors: any[];
  systemHealth: any;
  incidents: any[];
  isConnected: boolean;
  networkStatus: string;
  dataFreshness: number;
  lastUpdate: string;
  isDemoMode: boolean;
  timeline: number;
  mapLayers: Record<string, boolean>;

  fetchInitialData: () => Promise<void>;
  connectWebSocket: () => void;
  updateData: () => Promise<void>;
  setTimeline: (t: number) => void;
  toggleMapLayer: (layer: string) => void;
  updateIncidentStatus: (id: string, status: string) => void;
}

export const useJalnetraStore = create<JalnetraState>((set, get) => ({
  risk: null,
  propagation: null,
  impact: null,
  routes: null,
  sensors: [],
  systemHealth: null,
  incidents: [],
  isConnected: false,
  networkStatus: "ONLINE",
  dataFreshness: 0,
  lastUpdate: new Date().toISOString(),
  isDemoMode: false,
  timeline: 0,
  mapLayers: {
    flood: true,
    route: true,
    sensors: true,
  },

  setTimeline: (t) => set({ timeline: t }),
  toggleMapLayer: (layer) =>
    set((state) => ({
      mapLayers: { ...state.mapLayers, [layer]: !state.mapLayers[layer] },
    })),
  updateIncidentStatus: (id, status) =>
    set((state) => ({
      incidents: state.incidents.map((inc) =>
        inc.id === id ? { ...inc, status } : inc
      ),
    })),

  updateData: async () => {
    try {
      const [risk, propagation, impact, routes, health] = await Promise.all([
        jalnetraAPI.getRisk(),
        jalnetraAPI.getPropagation(),
        jalnetraAPI.getImpact(),
        jalnetraAPI.getRoutes(),
        jalnetraAPI.getHealth(),
      ]);

      set({
        risk,
        propagation,
        impact,
        routes,
        systemHealth: health,
        isDemoMode: health.demo_mode,
        lastUpdate: new Date().toISOString(),
        dataFreshness: 0,
      });
    } catch (e) {
      console.error("Failed to fetch API data", e);
      set({ networkStatus: "DEGRADED" });
    }
  },

  fetchInitialData: async () => {
    await get().updateData();
    get().connectWebSocket();

    // Start a timer to increment data freshness
    setInterval(() => {
      set((state) => ({ dataFreshness: state.dataFreshness + 1 }));
    }, 1000);
  },

  connectWebSocket: () => {
    const ws = new WebSocket(`${WS_BASE}/risk`);

    ws.onopen = () => {
      set({ isConnected: true, networkStatus: "ONLINE" });
      console.log("JALNETRA WebSocket Connected");
    };

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      console.log("WS MESSAGE:", msg);
      
      if (
        msg.event === "RISK_UPDATED" ||
        msg.event === "RISK_ESCALATED" ||
        msg.event === "RISK_DEESCALATED" ||
        msg.event === "DEMO_STARTED" ||
        msg.event === "DEMO_RESET" ||
        msg.event === "ROAD_THREATENED" ||
        msg.event === "NETWORK_DEGRADED" ||
        msg.event === "NETWORK_RESTORED" ||
        msg.event === "SENSOR_OFFLINE" ||
        msg.event === "INCIDENT_CREATED" ||
        msg.event === "WHATSAPP_SENT"
      ) {
        // Automatically fetch new state on important events
        get().updateData();

        if (msg.event === "NETWORK_DEGRADED") set({ networkStatus: "DEGRADED" });
        if (msg.event === "NETWORK_RESTORED") set({ networkStatus: "ONLINE" });
      }
    };

    ws.onclose = () => {
      set({ isConnected: false });
      console.log("JALNETRA WebSocket Disconnected, retrying...");
      setTimeout(() => get().connectWebSocket(), 5000);
    };

    ws.onerror = (error) => {
      console.error("JALNETRA WebSocket Error", error);
      ws.close();
    };
  },
}));
