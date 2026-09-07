# Agentic Tactical Maneuver Planner for Autonomous Vehicles (AVs)

A minimal, reproducible baseline implementation of an **Agentic AI Tactical Maneuver Planner** for Autonomous Vehicles (AVs), submitted for CSE598 Capstone Project Proposal.

---

## 🚗 Project Overview & Problem Definition

In autonomous driving architectures, **Tactical Maneuver Planning** bridges high-level route navigation and low-level motion control (steering/acceleration MPC). Given a multi-lane highway driving environment with surrounding dynamic traffic, the planner continuously evaluates environmental context and produces high-level, safe tactical maneuvers (`MAINTAIN_SPEED`, `ACCELERATE`, `SLOW_DOWN`, `LANE_CHANGE_LEFT`, `LANE_CHANGE_RIGHT`, `EMERGENCY_BRAKE`).

Traditional Finite State Machines (FSMs) struggle with edge-case brittleness and lack interpretable decision reasoning. This project leverages an **Agentic AI System (Gemini API + Deterministic Safety Tools)** to reason through complex driving scenes, perform safety verification via domain tools, and output structured maneuver commands accompanied by step-by-step safety rationales.

```
                              ┌─────────────────────────────────────────┐
                              │     Environmental Scene Input           │
                              │ (Ego state, Obstacles, Lanes, Weather)  │
                              └────────────────────┬────────────────────┘
                                                   │
                                                   ▼
                               ┌────────────────────────────────────────┐
                               │  Agentic Tactical Maneuver Planner     │
                               │           (Gemini API)                 │
                               └───────┬────────────────────────┬───────┘
                                       │                        │
               Tool Calls / Validation │                        │ Maneuver Candidate
                                       ▼                        │ Evaluation
                     ┌───────────────────────────────────┐      │
                     │       Domain Safety Tools         │      │
                     │  - TTC (Time-To-Collision) Calc   │──────┘
                     │  - Blindspot / Gap Checker        │
                     │  - Speed & Traffic Rule Validator │
                     └───────────────────────────────────┘
                                       │
                                       ▼
                              ┌─────────────────────────────────────────┐
                              │      Structured Tactical Decision       │
                              │  - Target Maneuver Command              │
                              │  - Target Velocity & Lane ID            │
                              │  - Safety Verdict & Rationale           │
                              └─────────────────────────────────────────┘
```

---

## 📁 Repository Structure

```
CSE598-Capstone-Baseline/
├── README.md                                # Setup, run instructions, and reproduce guide
├── GEMINI.md                                # Workspace configuration for Agentic AI
├── CSE598-capstone-proposal-template.docx   # Completed capstone project proposal document
├── requirements.txt                         # Python dependencies
├── .env.example                             # Environment variable template
├── .env                                     # API configuration (excluded from Git)
├── run_baseline.py                          # CLI runner for baseline execution
├── src/
│   ├── models/
│   │   └── vehicle_state.py                 # Pydantic state models & decision schemas
│   ├── tools/
│   │   ├── safety_evaluator.py              # TTC and blindspot safety evaluation tools
│   │   └── traffic_rules.py                 # Speed limit & lane rule validation tool
│   └── agent/
│       └── maneuver_planner.py              # Core Agentic Maneuver Planner (Gemini API)
├── data/
│   └── scenarios/                           # Driving test scenarios
│       ├── scenario_1_highway_dense_traffic.json
│       ├── scenario_2_slow_truck_overtake.json
│       └── scenario_3_cutin_emergency_brake.json
├── output_logs/                             # Generated baseline execution logs
│   └── baseline_execution_results.json
├── tests/
│   └── test_baseline.py                     # Pytest suite for baseline verification
└── .agents/                                 # Agentic AI customizations (rules & skills)
```

---

## 🛠️ Installation & Setup

### 1. Prerequisites
- Python 3.9 or higher

### 2. Clone Repository & Install Dependencies
```bash
git clone https://github.com/imonuilsuleimanov/CSE598-Capstone-Baseline.git
cd CSE598-Capstone-Baseline
pip install -r requirements.txt
```

### 3. Environment Key Setup
Copy `.env.example` to `.env` and set your Gemini API key:
```bash
cp .env.example .env
```
Edit `.env`:
```ini
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 🚀 How to Run & Reproduce Baseline

### Run All Scenarios
To execute the agentic planner across all sample highway scenarios:
```bash
python run_baseline.py --all
```

### Run a Specific Scenario
To run a specific scenario (e.g., slow truck overtake):
```bash
python run_baseline.py --scenario data/scenarios/scenario_2_slow_truck_overtake.json
```

### Run Automated Unit & Integration Tests
```bash
python -m pytest tests/
```

---

## 📊 Concrete Test Cases & Baseline Execution Output

### Test Case 1: Nominal Highway Cruising
- **Input Scenario**: `data/scenarios/scenario_1_highway_dense_traffic.json`
- **Driving Context**: Ego vehicle cruising at 25.0 m/s in Center Lane. Lead vehicle 80m ahead at 25.0 m/s.
- **Baseline Output**:
  ```text
  Selected Action       : MAINTAIN_SPEED
  Target Lane           : 1
  Target Velocity       : 25.0 m/s
  Safety Verdict        : SAFE
  Min Time-To-Collision : 999.00 seconds
  Tactical Rationale    : Current lane is clear and all safety tool audits passed. Maintaining cruising speed.
  ```

### Test Case 2: Slow Truck Overtake
- **Input Scenario**: `data/scenarios/scenario_2_slow_truck_overtake.json`
- **Driving Context**: Ego vehicle at 26.0 m/s approaching a slow heavy truck (15.0 m/s) 30m ahead in Center Lane. Left Lane is open.
- **Baseline Output**:
  ```text
  Selected Action       : LANE_CHANGE_LEFT
  Target Lane           : 0
  Target Velocity       : 26.0 m/s
  Safety Verdict        : SAFE
  Min Time-To-Collision : 999.00 seconds
  Tactical Rationale    : Slow vehicle detected ahead at 30.0m. Left lane is clear (TTC=999.00s). Executing overtake maneuver.
  ```

### Test Case 3: Cut-In Emergency Brake
- **Input Scenario**: `data/scenarios/scenario_3_cutin_emergency_brake.json`
- **Driving Context**: Aggressive vehicle cuts into Ego lane 15m ahead at low speed (12.0 m/s) while Ego is traveling at 28.0 m/s. Left lane blocked by adjacent vehicle.
- **Baseline Output**:
  ```text
  Selected Action       : EMERGENCY_BRAKE
  Target Lane           : 1
  Target Velocity       : 20.0 m/s
  Safety Verdict        : CAUTION
  Min Time-To-Collision : 0.94 seconds
  Tactical Rationale    : Critical forward collision threat detected (TTC=0.94s). No lane change clear. Applying emergency braking.
  ```

---

## 📂 Input & Output File Locations

- **Input Scenarios**: `data/scenarios/*.json`
- **Execution Log**: `output_logs/baseline_execution_results.json`
- **Proposal Document**: `CSE598-capstone-proposal-template.docx`

---

## 📄 License & Attribution

Submitted by **Imonuil Suleimanov** for CSE598 Capstone Project Proposal.
