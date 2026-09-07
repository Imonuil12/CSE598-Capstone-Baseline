import docx

def update_proposal():
    doc = docx.Document('CSE598-capstone-proposal-template.docx')
    
    # 1. Fill Table 0 (Basic Information)
    table0 = doc.tables[0]
    table0.rows[1].cells[1].text = "Imonuil Suleimanov"
    table0.rows[2].cells[1].text = "Agentic Tactical Maneuver Planner for Autonomous Vehicles (AVs)"
    table0.rows[3].cells[1].text = "https://github.com/imonuilsuleimanov/CSE598-Capstone-Baseline"
    table0.rows[4].cells[1].text = "README.md and GEMINI.md"

    # Define content for each section
    section_contents = {
        "Section 1. Problem Definition": """Defined Problem:
This project addresses Tactical Maneuver Planning for Autonomous Vehicles (AVs) operating in complex dynamic traffic environments. In autonomous driving architectures, tactical maneuver planning bridges the gap between high-level routing/navigation and low-level motion control. The target system must continuously evaluate dynamic driving scenes (ego vehicle kinematics, surrounding obstacles, lane topologies, speed limits, road weather conditions) and output optimal, safe high-level driving actions.

Intended User and Context:
Autonomous driving systems, safety validation engineers, and decision-making research platforms operating on multi-lane highways or urban thoroughfares under dynamic traffic conditions.

Input:
Structured environment state including Ego vehicle state (position x/y, velocity vx/vy, lane ID), surrounding obstacle vehicles (positions, velocities, lane IDs, vehicle types), lane topology (speed limit, neighboring lanes, obstruction markers), and environmental metadata (weather, surface condition).

Output:
A structured tactical maneuver decision containing:
1. Target Action: MAINTAIN_SPEED, ACCELERATE, SLOW_DOWN, LANE_CHANGE_LEFT, LANE_CHANGE_RIGHT, or EMERGENCY_BRAKE.
2. Target Lane ID and target velocity (m/s).
3. Safety Verdict (SAFE, CAUTION, UNSAFE) and Time-To-Collision (TTC) metric.
4. Step-by-step tactical rationale explaining why the action was selected over candidates.

Operational Definition of Success & Failure:
- Success: 0 collisions (TTC >= 3.0s under normal flow, or executing appropriate evasive maneuvers when cut-in occurs), 100% compliance with speed limits and lane rules, and clear safety rationales.
- Failure: Collisions or critical TTC violations (< 2.0s without braking), illegal lane transitions into blocked/occupied lanes, or unhandled scenario execution.""",

        "Section 2. Motivation and Project Scope": """Why the Problem Matters:
Tactical decision-making in autonomous driving is safety-critical. Traditional approaches rely on finite state machines (FSMs) or manually engineered rule trees. However, FSMs suffer from combinatorial explosion in complex multi-vehicle interactions, edge-case brittleness, and an inability to provide human-interpretable reasoning when faced with unexpected dynamic maneuvers (e.g., sudden cut-ins or slow-moving obstacles).

Why an Agentic AI Approach:
An Agentic AI approach combining Large Language Models (Gemini API) with deterministic domain safety tools offers significant advantages:
1. Multi-Step Reasoning: The agent can evaluate multiple candidate maneuvers simultaneously.
2. Tool Augmentation: The agent executes deterministic safety checks (TTC calculator, blind-spot gap analyzer, traffic law validator) before finalizing decisions.
3. Interpretability: The agent generates human-readable tactical rationales for every driving maneuver.

Project Scope (In-Scope for Semester):
- Development of a modular Agentic Tactical Maneuver Planner utilizing Gemini API.
- Integration of deterministic safety evaluation tools (TTC computation, blind spot clearance, speed limit compliance).
- Evaluation across diverse highway scenario datasets (Nominal Cruising, Slow Truck Overtake, Cut-in Emergency Braking).
- Full integration and validation with simulated environment benchmarks (Highway-Env).

Out of Scope (Intentionally Omitted):
- Low-level trajectory generation (spline optimization, PID/MPC steering and throttle control).
- Raw sensor perception processing (camera/LiDAR point cloud object detection).""",

        "Section 3. Runnable Baseline": """Baseline System Architecture:
The baseline system implements a tool-augmented Agentic Tactical Maneuver Planner combining Gemini API (via google-genai SDK) with deterministic domain safety evaluation modules.

Step-by-Step Baseline Pipeline:
1. Environment State Ingestion: Loads structured scene data (Ego vehicle kinematics, obstacle positions/velocities, lane topologies).
2. Domain Tool Safety Audit: Executes deterministic safety tools across all 6 candidate maneuver actions to calculate Time-To-Collision (TTC), minimum obstacle distance, blindspot clearance, and speed compliance.
3. LLM Tactical Reasoning Engine: Ingests the scene state and tool safety audit summary into Gemini (or tool-reasoning engine fallback) to evaluate trade-offs (e.g., speed vs. comfort vs. safety).
4. Structured Output Generation: Produces a Pydantic-validated ManeuverPlan object containing the selected action, target lane, velocity, safety verdict, and step-by-step tactical rationale.

Baseline Code Artifacts:
- src/models/vehicle_state.py: Pydantic schemas for state representation and decision plans.
- src/tools/safety_evaluator.py: Deterministic TTC and blind-spot evaluation tools.
- src/tools/traffic_rules.py: Traffic rule and speed limit compliance validator.
- src/agent/maneuver_planner.py: Core Agentic Maneuver Planner implementation.
- run_baseline.py: CLI runner script for scenario execution and logging.""",

        "Section 4. Test Case and Baseline Output": """Concrete Test Cases and Execution Results:

1. Test Case 1: Nominal Highway Cruising (data/scenarios/scenario_1_highway_dense_traffic.json)
- Input: Ego traveling at 25.0 m/s in Center Lane (1). Lead car 80m ahead traveling at 25.0 m/s.
- Actual Output: Action=MAINTAIN_SPEED | Safety Verdict=SAFE | TTC=999.0s | Rationale="Current lane is clear and all safety tool audits passed. Maintaining cruising speed."

2. Test Case 2: Slow Vehicle Overtake (data/scenarios/scenario_2_slow_truck_overtake.json)
- Input: Ego traveling at 26.0 m/s approaching a slow heavy truck (15.0 m/s) 30m ahead in Center Lane (1). Left Lane (0) is clear.
- Actual Output: Action=LANE_CHANGE_LEFT | Safety Verdict=SAFE | Target Lane=0 | Target Velocity=26.0 m/s | Rationale="Slow vehicle detected ahead at 30.0m. Left lane is clear (TTC=999.00s). Executing overtake maneuver."

3. Test Case 3: Cut-in Emergency Brake (data/scenarios/scenario_3_cutin_emergency_brake.json)
- Input: Aggressive vehicle cuts into Ego lane at 15m ahead traveling at 12.0 m/s while Ego is at 28.0 m/s. Left lane blocked by adjacent vehicle.
- Actual Output: Action=EMERGENCY_BRAKE | Safety Verdict=CAUTION | Target Velocity=20.0 m/s | TTC=0.94s | Rationale="Critical forward collision threat detected (TTC=0.94s). No lane change clear. Applying emergency braking."

Output Log Artifact:
Full structured execution outputs are logged to output_logs/baseline_execution_results.json.""",

        "Section 5. Reproducibility and Run Instructions": """Reproducibility Instructions:

Dependencies:
Python 3.9+, google-genai, pydantic, python-dotenv, highway-env, gymnasium, matplotlib, python-docx, pytest.

Setup Steps:
1. Clone repository: git clone <repository_url> && cd CSE598-Capstone-Baseline
2. Install dependencies: pip install -r requirements.txt
3. Configure API Key: Copy .env.example to .env and set GEMINI_API_KEY=<your_api_key>.

Execution Commands:
- Run baseline across all scenarios:
  python run_baseline.py --all

- Run baseline on a specific scenario:
  python run_baseline.py --scenario data/scenarios/scenario_2_slow_truck_overtake.json

- Run automated unit test suite:
  python -m pytest tests/

Input / Output Locations:
- Scenario Inputs: data/scenarios/*.json
- Execution Logs: output_logs/baseline_execution_results.json""",

        "Section 6. Initial Evaluation Plan": """Initial Evaluation Plan for Improved System:

To measure progress over this baseline, the future agentic planner will be evaluated using quantitative metrics across standard simulation benchmarks (Highway-Env):

1. Safety Metrics:
   - Collision Rate (% of scenario episodes resulting in a collision). Target: 0.0%.
   - Minimum TTC Violation Frequency (% of time TTC drops below 2.5s threshold).

2. Operational Efficiency & Comfort:
   - Average Speed Ratio (actual speed vs. target speed limit).
   - Maneuver Jerk / Smoothness (frequency of sudden emergency braking commands).

3. Agentic Performance:
   - Tool Call Accuracy (% of tool inputs/outputs correctly parsed and utilized).
   - Tactical Reasoning Quality (evaluated via LLM-as-a-judge for safety rationale coherence).
   - Decision Latency (mean inference time per planning cycle in milliseconds).""",

        "Section 7. Limitations and Next Steps": """Current Baseline Limitations:
1. Static Frame Input: Current baseline evaluates single static scenario snapshots rather than continuous closed-loop temporal simulation steps.
2. Rule-Based Fallback Scope: Simplifies multi-vehicle interaction modeling in extreme edge cases.

Next Steps for Capstone Project:
1. Closed-Loop Highway-Env Integration: Connect the Agentic Maneuver Planner directly to gymnasium highway-env for multi-step closed-loop simulation.
2. Dynamic Tool Expansion: Develop real-time reachability analyzers and trajectory prediction tools.
3. Benchmark Evaluation Harness: Build automated batch evaluation scripts comparing the Agentic Planner against baseline RL (DQN/PPO) and state-machine planners."""
    }

    # Find paragraphs with section titles and insert content after them
    for p in doc.paragraphs:
        p_text = p.text.strip()
        for title, content in section_contents.items():
            if title in p_text:
                # Add text paragraph right after heading
                p.insert_paragraph_before(content + "\n")
                break
                
    doc.save('CSE598-capstone-proposal-template.docx')
    print("Successfully updated CSE598-capstone-proposal-template.docx")

if __name__ == "__main__":
    update_proposal()
