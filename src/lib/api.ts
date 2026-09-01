import axios from "axios";

export const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export const WS_BASE = API_BASE.replace("http://", "ws://").replace("https://", "wss://").replace("/api", "/ws");

export const api = axios.create({
  baseURL: `${API_BASE}/api`,
  headers: {
    "Content-Type": "application/json",
  },
});

export const jalnetraAPI = {
  // System
  getHealth: () => api.get("/system/health").then((res) => res.data),
  getRegions: () => api.get("/regions").then((res) => res.data),

  // Risk & Intelligence
  getRisk: () => api.get("/risk").then((res) => res.data),
  getPropagation: () => api.get("/propagation").then((res) => res.data),
  getImpact: () => api.get("/impact").then((res) => res.data),
  getRoutes: () => api.get("/routes").then((res) => res.data),
  getShelters: () => api.get("/shelters").then((res) => res.data),
  getSensors: () => api.get("/sensors").then((res) => res.data),
  getIncidents: () => api.get("/incidents").then((res) => res.data),
  getAlerts: () => api.get("/events").then((res) => res.data), // Alerts are from /events or similar depending on the exact backend
  getEvents: () => api.get("/events").then((res) => res.data),

  // Actions
  triggerSOS: (data: any) => api.post("/demo/sos", data).then((res) => res.data),
  sendWhatsAppAlert: (data: any) => api.post("/demo/whatsapp", data).then((res) => res.data),

  // Demo Controls
  startDemo: () => api.post("/demo/start").then((res) => res.data),
  pauseDemo: () => api.post("/demo/pause").then((res) => res.data),
  resetDemo: () => api.post("/demo/reset").then((res) => res.data),
  increaseRainfall: () => api.post("/demo/rainfall/increase").then((res) => res.data),
  failSensor: (sensorId: string = "sensor-water-02") =>
    api.post(`/demo/sensor/fail?sensor_id=${sensorId}`).then((res) => res.data),
  closeRoad: (roadId: string = "road-bridge") =>
    api.post(`/demo/road/close?road_id=${roadId}`).then((res) => res.data),
  degradeNetwork: () => api.post("/demo/network/degrade").then((res) => res.data),
  restoreNetwork: () => api.post("/demo/network/restore").then((res) => res.data),
};
