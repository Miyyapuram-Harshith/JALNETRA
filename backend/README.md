# JALNETRA — THE EYE BEFORE THE FLOOD

### Hyperlocal Flash-Flood Intelligence, Evacuation & Last-Mile Alert Backend

---

> **⚠️ DECISION-SUPPORT PROTOTYPE** — JALNETRA provides modeled estimates and system recommendations.
> It is NOT an official government emergency service. All predictions carry uncertainty.

---

## Quick Start

```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy environment config
cp .env.example .env

# 4. Run the backend
uvicorn app.main:app --reload
```

The server starts at **http://localhost:8000**

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/system/health

---

## Demo Mode

By default, `DEMO_MODE=true` in `.env`. This means:

- ✅ No database credentials needed (SQLite)
- ✅ No weather API key needed (demo weather provider)
- ✅ No IoT devices needed (sensor simulator)
- ✅ No WhatsApp credentials needed (mock provider)
- ✅ Demo region "Hilly Village Alpha" is pre-loaded

**Everything works out of the box.**

---

## Demo Scenario (Jury Demo)

Run the scripted 20-step demo:

```bash
# 1. Start demo
curl -X POST http://localhost:8000/api/demo/start

# 2. Check initial state (NORMAL)
curl http://localhost:8000/api/risk

# 3. Increase rainfall
curl -X POST http://localhost:8000/api/demo/rainfall/increase
curl -X POST http://localhost:8000/api/demo/rainfall/increase

# 4. Check risk escalation
curl http://localhost:8000/api/risk

# 5. Check safe departure window
curl http://localhost:8000/api/routes

# 6. Close a road
curl -X POST "http://localhost:8000/api/demo/road/close?road_id=road-bridge"

# 7. Send WhatsApp alert
curl -X POST http://localhost:8000/api/demo/whatsapp

# 8. Trigger citizen SOS
curl -X POST http://localhost:8000/api/demo/sos

# 9. Inject sensor failure
curl -X POST http://localhost:8000/api/demo/sensor/fail

# 10. Degrade network
curl -X POST http://localhost:8000/api/demo/network/degrade

# 11. Restore network
curl -X POST http://localhost:8000/api/demo/network/restore

# 12. Reset everything
curl -X POST http://localhost:8000/api/demo/reset
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./jalnetra_demo.db` | Database connection |
| `DEMO_MODE` | `true` | Enable demo mode |
| `USE_REAL_WEATHER` | `false` | Use real weather API |
| `USE_REAL_IOT` | `false` | Accept real IoT sensor data |
| `WHATSAPP_PROVIDER` | `mock` | WhatsApp provider: `mock` or `meta` |
| `WHATSAPP_ACCESS_TOKEN` | - | Meta WhatsApp Business API token |
| `WHATSAPP_PHONE_NUMBER_ID` | - | Meta phone number ID |
| `WHATSAPP_RECIPIENT_NUMBER` | - | Default recipient number |
| `FRONTEND_ORIGIN` | `http://localhost:3000` | CORS allowed origin |

---

## WhatsApp Setup

### Mock Mode (Default)
No setup needed. Messages are generated but not sent.

### Real WhatsApp (Meta Business API)

1. Create a Meta Developer account
2. Set up WhatsApp Business API
3. Get access token and phone number ID
4. Update `.env`:

```env
WHATSAPP_PROVIDER=meta
WHATSAPP_ACCESS_TOKEN=your_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_id
WHATSAPP_RECIPIENT_NUMBER=recipient_phone_with_country_code
```

---

## IoT Setup

### Simulated (Default)
Sensor readings are generated automatically.

### Real ESP32

ESP32 sends HTTP POST to:

```
POST http://your-server:8000/api/sensors/{sensor_id}/reading
Content-Type: application/json

{
  "timestamp": "2026-09-01T10:30:00",
  "rainfall_mm": 42.5,
  "water_level_m": 4.28,
  "soil_moisture_percent": 81.2,
  "battery_percent": 84,
  "signal_strength": 78
}
```

No MQTT required. No code changes needed.

---

## API Overview

### Risk & Intelligence
| Endpoint | Method | Description |
|---|---|---|
| `/api/risk` | GET | Risk assessment for all zones |
| `/api/forecast` | GET | Weather forecast timeline |
| `/api/propagation` | GET | Flood propagation GeoJSON |
| `/api/impact` | GET | Impact assessment |
| `/api/routes` | GET | Routes with safe departure window |
| `/api/departure-window` | GET | Safe departure window only |

### Data
| Endpoint | Method | Description |
|---|---|---|
| `/api/regions` | GET | Region data with GeoJSON |
| `/api/sensors` | GET | All sensors with health |
| `/api/roads` | GET | Roads with risk status |
| `/api/shelters` | GET | Shelters with capacity |

### Actions
| Endpoint | Method | Description |
|---|---|---|
| `/api/sensors/{id}/reading` | POST | Submit sensor reading |
| `/api/sensors/{id}/simulate` | POST | Trigger sensor scenario |
| `/api/incidents/sos` | POST | Citizen SOS |
| `/api/alerts/whatsapp` | POST | Send WhatsApp alert |
| `/api/simulation/run` | POST | Run scenario simulation |

### Demo Controls
| Endpoint | Method | Description |
|---|---|---|
| `/api/demo/start` | POST | Start jury demo |
| `/api/demo/reset` | POST | Reset all state |
| `/api/demo/rainfall/increase` | POST | Increase rainfall |
| `/api/demo/sensor/fail` | POST | Inject sensor failure |
| `/api/demo/road/close` | POST | Close a road |
| `/api/demo/network/degrade` | POST | Degrade network |
| `/api/demo/sos` | POST | Trigger demo SOS |
| `/api/demo/whatsapp` | POST | Trigger demo WhatsApp |

### WebSocket
| Endpoint | Description |
|---|---|
| `/ws/risk` | Risk updates |
| `/ws/sensors` | Sensor updates |
| `/ws/alerts` | Alert notifications |
| `/ws/incidents` | Incident updates |
| `/ws/routes` | Route changes |
| `/ws/simulation` | Simulation events |
| `/ws/system` | System status |

---

## Architecture

```
FastAPI Monolith
├── API Routes (10 modules)
├── Engines
│   ├── Risk Engine (hybrid rules + ML)
│   ├── Confidence Engine
│   ├── Propagation Engine (GeoJSON)
│   ├── Impact Engine (spatial intersection)
│   ├── Route Engine (time-aware)
│   └── Safe Departure Engine
├── Services
│   ├── Sensor Service (trust engine)
│   ├── Alert Service (dedup, escalation)
│   ├── Incident Service (priority, assignment)
│   └── Audit Service
├── Providers
│   ├── Weather (demo / real)
│   ├── Sensors (simulated / real ESP32)
│   └── WhatsApp (mock / Meta API)
├── Simulation
│   └── Demo Controller (jury demo)
├── Real-time
│   └── WebSocket Manager
└── Data
    └── Hilly Village Alpha (demo region)
```

---

## The Pipeline

```
FIRST RAINDROP
      ↓
SENSOR DATA
      ↓
VALIDATION & TRUST
      ↓
MULTI-SOURCE FUSION
      ↓
RISK INTELLIGENCE
      ↓
FLOOD PROPAGATION
      ↓
IMPACT ANALYSIS
      ↓
ROAD & SHELTER STATUS
      ↓
SAFE DEPARTURE WINDOW
      ↓
BEST AVAILABLE ROUTE
      ↓
ALERT (WhatsApp)
      ↓
CITIZEN
      ↓
SOS → RESPONDER
```

---

## License

Hackathon project — JALNETRA Team
