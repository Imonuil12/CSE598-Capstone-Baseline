#!/usr/bin/env python3
"""
CLI Runner for Agentic Tactical Maneuver Planner for Autonomous Vehicles (AVs).
Reproducible Baseline Execution Script.
"""

import sys
import os
import json
import argparse
from typing import List

from src.models.vehicle_state import WorldState, ManeuverPlan
from src.agent.maneuver_planner import AgenticManeuverPlanner


def load_scenario(filepath: str) -> WorldState:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Scenario file not found: {filepath}")
    with open(filepath, "r") as f:
        data = json.load(f)
    return WorldState(**data)


def render_ascii_scene(world_state: WorldState):
    """Renders a simple ASCII representation of the 3-lane road and vehicle positions."""
    ego = world_state.ego_vehicle
    obstacles = world_state.obstacles
    
    print("\n" + "="*80)
    print(f" SCENARIO VISUALIZATION: {world_state.scenario_id}")
    print(f" Description: {world_state.description}")
    print("="*80)
    
    for lane_id in range(3):
        lane_str = f"Lane {lane_id} | "
        for x_pos in range(60, 200, 10):
            symbol = "-"
            # Check Ego
            if lane_id == ego.lane_id and abs(x_pos - ego.position_x) < 5:
                symbol = "[EGO]"
            else:
                # Check Obstacles
                for obs in obstacles:
                    if obs.lane_id == lane_id and abs(x_pos - obs.position_x) < 5:
                        symbol = f"[{obs.id[:4].upper()}]"
                        break
            lane_str += f"{symbol:^7}"
        print(lane_str)
    print("="*80 + "\n")


def print_plan_report(world_state: WorldState, plan: ManeuverPlan):
    render_ascii_scene(world_state)
    
    print("--------------------------------------------------------------------------------")
    print(f" AGENTIC TACTICAL MANEUVER DECISION REPORT")
    print("--------------------------------------------------------------------------------")
    print(f" Scenario ID           : {plan.scenario_id}")
    print(f" Ego Vehicle State     : Position=({world_state.ego_vehicle.position_x:.1f}m, Lane {world_state.ego_vehicle.lane_id}), Velocity={world_state.ego_vehicle.velocity_x:.1f} m/s")
    print(f" Selected Action       : {plan.selected_action.value}")
    print(f" Target Lane           : {plan.target_lane_id}")
    print(f" Target Velocity       : {plan.target_velocity:.1f} m/s")
    print(f" Safety Verdict        : {plan.safety_verdict}")
    print(f" Min Time-To-Collision : {plan.time_to_collision_seconds:.2f} seconds")
    print(f" Tactical Rationale    : {plan.rationale}")
    print("--------------------------------------------------------------------------------")
    print(" Safety Tool Audit Summary:")
    for act, audit in plan.tool_evaluations.items():
        is_safe = audit.get("is_safe", False)
        ttc = audit.get("ttc_sec", 999.0)
        status = "SAFE" if is_safe else "UNSAFE"
        print(f"  - Action {act:<20}: [{status:<6}] TTC={ttc:.2f}s | Details: {audit.get('details', '')}")
    print("--------------------------------------------------------------------------------\n")


def main():
    parser = argparse.ArgumentParser(description="Agentic Tactical Maneuver Planner for Autonomous Vehicles")
    parser.add_argument(
        "--scenario",
        type=str,
        default="data/scenarios/scenario_2_slow_truck_overtake.json",
        help="Path to scenario JSON file"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all sample scenarios in data/scenarios/"
    )
    args = parser.parse_args()

    planner = AgenticManeuverPlanner()

    scenarios_to_run = []
    if args.all:
        scenario_dir = "data/scenarios"
        scenarios_to_run = [
            os.path.join(scenario_dir, f)
            for f in sorted(os.listdir(scenario_dir))
            if f.endswith(".json")
        ]
    else:
        scenarios_to_run = [args.scenario]

    results = []
    os.makedirs("output_logs", exist_ok=True)

    print("\n" + "#"*80)
    print("  AGENTIC TACTICAL MANEUVER PLANNER FOR AUTONOMOUS VEHICLES - BASELINE EXECUTION")
    print("#"*80)

    for scenario_path in scenarios_to_run:
        world_state = load_scenario(scenario_path)
        plan = planner.plan_maneuver(world_state)
        print_plan_report(world_state, plan)
        results.append(plan.model_dump())

    log_output_path = "output_logs/baseline_execution_results.json"
    with open(log_output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"[Success] Baseline execution completed cleanly. Log saved to: {log_output_path}\n")


if __name__ == "__main__":
    main()
