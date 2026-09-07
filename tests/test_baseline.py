import os
import json
import pytest

from src.models.vehicle_state import WorldState, ActionType, SafetyEvaluationResult
from src.tools.safety_evaluator import calculate_ttc, evaluate_action_safety
from src.tools.traffic_rules import validate_traffic_rules
from src.agent.maneuver_planner import AgenticManeuverPlanner


def test_ttc_calculation():
    # Ego at x=100, vx=30. Lead car at x=150, vx=20. dv = 10 m/s. dx = 50 m. TTC = 5.0 s
    ttc = calculate_ttc(100.0, 30.0, 150.0, 20.0)
    assert pytest.approx(ttc, 0.01) == 5.0

    # Ego slower than lead car -> no collision course -> inf
    ttc_no_collision = calculate_ttc(100.0, 20.0, 150.0, 30.0)
    assert ttc_no_collision == float('inf')


def test_traffic_rules_validation():
    scenario_path = "data/scenarios/scenario_1_highway_dense_traffic.json"
    with open(scenario_path) as f:
        world_state = WorldState(**json.load(f))

    # Speed compliant maneuver
    res = validate_traffic_rules(world_state, target_speed=25.0, target_lane_id=1)
    assert res["compliant"] is True

    # Speed limit violation maneuver
    res_speeding = validate_traffic_rules(world_state, target_speed=35.0, target_lane_id=1)
    assert res_speeding["compliant"] is False


def test_safety_evaluator_tool():
    scenario_path = "data/scenarios/scenario_3_cutin_emergency_brake.json"
    with open(scenario_path) as f:
        world_state = WorldState(**json.load(f))

    # Action maintain speed has close obstacle cut-in (x=115 vs ego x=100, dv=16 m/s) -> TTC = 15/16 = 0.9375s
    res = evaluate_action_safety(world_state, ActionType.MAINTAIN_SPEED)
    assert res.is_safe is False
    assert res.time_to_collision < 3.0


def test_agentic_planner_execution():
    planner = AgenticManeuverPlanner()
    scenario_dir = "data/scenarios"
    
    for filename in sorted(os.listdir(scenario_dir)):
        if filename.endswith(".json"):
            filepath = os.path.join(scenario_dir, filename)
            with open(filepath) as f:
                world_state = WorldState(**json.load(f))
                
            plan = planner.plan_maneuver(world_state)
            assert plan.selected_action in ActionType
            assert plan.safety_verdict in ("SAFE", "CAUTION", "UNSAFE")
            assert len(plan.rationale) > 10
