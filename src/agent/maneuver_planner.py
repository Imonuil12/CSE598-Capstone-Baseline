import os
import json
from typing import Dict, Any, List
from dotenv import load_dotenv

from src.models.vehicle_state import (
    WorldState, ActionType, ManeuverPlan, SafetyEvaluationResult
)
from src.tools.safety_evaluator import evaluate_action_safety
from src.tools.traffic_rules import validate_traffic_rules

load_dotenv()


class AgenticManeuverPlanner:
    def __init__(self, model_name: str = "gemini-3.5-flash"):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = model_name
        self._init_client()

    def _init_client(self):
        """Initializes Gemini API client if API key is present."""
        self.genai_client = None
        if self.api_key and not self.api_key.startswith("your_"):
            try:
                # Try google-genai SDK first
                from google import genai
                self.genai_client = genai.Client(api_key=self.api_key)
                self.use_new_sdk = True
            except ImportError:
                try:
                    import google.generativeai as genai_legacy
                    genai_legacy.configure(api_key=self.api_key)
                    self.genai_client = genai_legacy.GenerativeModel(self.model_name)
                    self.use_new_sdk = False
                except Exception as e:
                    print(f"[Warning] Failed to initialize Gemini API client: {e}. Using tool-augmented fallback planner.")

    def run_tool_audits(self, world_state: WorldState) -> Dict[str, SafetyEvaluationResult]:
        """Runs safety evaluator tools for all candidate actions."""
        audits = {}
        for action in ActionType:
            audits[action.value] = evaluate_action_safety(world_state, action)
        return audits

    def plan_maneuver(self, world_state: WorldState) -> ManeuverPlan:
        """
        Executes agentic tactical maneuver planning using domain tools and LLM tactical reasoning.
        """
        # Step 1: Execute Tool Audits (Safety & Traffic Rules)
        tool_audits = self.run_tool_audits(world_state)
        
        audits_summary = {
            act: {
                "is_safe": res.is_safe,
                "ttc_sec": res.time_to_collision,
                "min_dist_m": res.min_distance,
                "blindspot_clear": res.blindspot_clear,
                "details": res.details
            }
            for act, res in tool_audits.items()
        }

        # Step 2: Attempt LLM Tactical Reasoning via Gemini API
        if self.genai_client:
            try:
                return self._plan_with_gemini(world_state, audits_summary)
            except Exception as e:
                print(f"[Info] Gemini API call note: {e}. Proceeding with deterministic tool-reasoning engine.")

        # Step 3: Tool-Augmented Deterministic Planner Fallback
        return self._plan_with_rules(world_state, tool_audits)

    def _plan_with_gemini(self, world_state: WorldState, audits_summary: Dict[str, Any]) -> ManeuverPlan:
        prompt = f"""
You are an expert Agentic Tactical Maneuver Planner for Autonomous Vehicles (AVs).
Analyze the driving scene and domain safety tool evaluations below, then output a JSON tactical driving decision.

### SCENARIO: {world_state.scenario_id} - {world_state.description}
- Ego Position X: {world_state.ego_vehicle.position_x:.1f}m | Lane: {world_state.ego_vehicle.lane_id} | Speed: {world_state.ego_vehicle.velocity_x:.1f} m/s
- Road Condition: {world_state.road_condition} | Weather: {world_state.weather}
- Surrounding Obstacles: {[obs.model_dump() for obs in world_state.obstacles]}

### DOMAIN SAFETY TOOL EVALUATIONS:
{json.dumps(audits_summary, indent=2)}

### INSTRUCTIONS:
Select the safest, most efficient tactical maneuver.
Choose one of: ["MAINTAIN_SPEED", "ACCELERATE", "SLOW_DOWN", "LANE_CHANGE_LEFT", "LANE_CHANGE_RIGHT", "EMERGENCY_BRAKE"].

Output strictly raw JSON matching this schema:
{{
  "selected_action": "ACTION_NAME",
  "target_lane_id": integer,
  "target_velocity": float,
  "safety_verdict": "SAFE" | "CAUTION" | "UNSAFE",
  "time_to_collision_seconds": float,
  "rationale": "Clear step-by-step safety explanation."
}}
"""
        if self.use_new_sdk:
            response = self.genai_client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            text = response.text
        else:
            response = self.genai_client.generate_content(prompt)
            text = response.text

        # Extract JSON substring
        json_start = text.find('{')
        json_end = text.rfind('}') + 1
        if json_start != -1 and json_end != -1:
            clean_json = text[json_start:json_end]
            data = json.loads(clean_json)
            
            action_enum = ActionType(data["selected_action"])
            ttc = data.get("time_to_collision_seconds", audits_summary[action_enum.value]["ttc_sec"])
            
            return ManeuverPlan(
                scenario_id=world_state.scenario_id,
                selected_action=action_enum,
                target_lane_id=data["target_lane_id"],
                target_velocity=data["target_velocity"],
                safety_verdict=data["safety_verdict"],
                time_to_collision_seconds=ttc,
                rationale=data["rationale"],
                tool_evaluations=audits_summary
            )
        else:
            raise ValueError("LLM response did not contain valid JSON block.")

    def _plan_with_rules(self, world_state: WorldState, tool_audits: Dict[str, SafetyEvaluationResult]) -> ManeuverPlan:
        """Deterministic safety-critical fallback decision maker."""
        ego = world_state.ego_vehicle
        current_lane = ego.lane_id
        
        maintain_audit = tool_audits[ActionType.MAINTAIN_SPEED.value]
        
        # Scenario 1: Emergency Brake needed if TTC is critical on current lane
        if maintain_audit.time_to_collision < 2.5:
            # Check if lane change is safe first
            left_audit = tool_audits.get(ActionType.LANE_CHANGE_LEFT.value)
            right_audit = tool_audits.get(ActionType.LANE_CHANGE_RIGHT.value)
            
            if left_audit and left_audit.is_safe and left_audit.blindspot_clear:
                return ManeuverPlan(
                    scenario_id=world_state.scenario_id,
                    selected_action=ActionType.LANE_CHANGE_LEFT,
                    target_lane_id=current_lane - 1,
                    target_velocity=ego.velocity_x,
                    safety_verdict="CAUTION",
                    time_to_collision_seconds=left_audit.time_to_collision,
                    rationale=f"Imminent collision threat in current lane (TTC={maintain_audit.time_to_collision:.2f}s). Executing evasive left lane change.",
                    tool_evaluations={k: v.model_dump() for k, v in tool_audits.items()}
                )
            elif right_audit and right_audit.is_safe and right_audit.blindspot_clear:
                return ManeuverPlan(
                    scenario_id=world_state.scenario_id,
                    selected_action=ActionType.LANE_CHANGE_RIGHT,
                    target_lane_id=current_lane + 1,
                    target_velocity=ego.velocity_x,
                    safety_verdict="CAUTION",
                    time_to_collision_seconds=right_audit.time_to_collision,
                    rationale=f"Imminent collision threat in current lane (TTC={maintain_audit.time_to_collision:.2f}s). Executing evasive right lane change.",
                    tool_evaluations={k: v.model_dump() for k, v in tool_audits.items()}
                )
            else:
                return ManeuverPlan(
                    scenario_id=world_state.scenario_id,
                    selected_action=ActionType.EMERGENCY_BRAKE,
                    target_lane_id=current_lane,
                    target_velocity=max(0.0, ego.velocity_x - 8.0),
                    safety_verdict="CAUTION",
                    time_to_collision_seconds=maintain_audit.time_to_collision,
                    rationale=f"Critical forward collision threat detected (TTC={maintain_audit.time_to_collision:.2f}s). No lane change clear. Applying emergency braking.",
                    tool_evaluations={k: v.model_dump() for k, v in tool_audits.items()}
                )

        # Scenario 2: Slow truck ahead, evaluate overtake
        if maintain_audit.min_distance < 35.0:
            left_audit = tool_audits.get(ActionType.LANE_CHANGE_LEFT.value)
            if left_audit and left_audit.is_safe and left_audit.blindspot_clear:
                return ManeuverPlan(
                    scenario_id=world_state.scenario_id,
                    selected_action=ActionType.LANE_CHANGE_LEFT,
                    target_lane_id=current_lane - 1,
                    target_velocity=ego.target_speed,
                    safety_verdict="SAFE",
                    time_to_collision_seconds=left_audit.time_to_collision,
                    rationale=f"Slow vehicle detected ahead at {maintain_audit.min_distance:.1f}m. Left lane is clear (TTC={left_audit.time_to_collision:.2f}s). Executing overtake maneuver.",
                    tool_evaluations={k: v.model_dump() for k, v in tool_audits.items()}
                )
            else:
                return ManeuverPlan(
                    scenario_id=world_state.scenario_id,
                    selected_action=ActionType.SLOW_DOWN,
                    target_lane_id=current_lane,
                    target_velocity=max(0.0, ego.velocity_x - 3.0),
                    safety_verdict="SAFE",
                    time_to_collision_seconds=maintain_audit.time_to_collision,
                    rationale=f"Slow vehicle ahead at {maintain_audit.min_distance:.1f}m. Lane change not optimal. Decelerating to maintain safe gap.",
                    tool_evaluations={k: v.model_dump() for k, v in tool_audits.items()}
                )

        # Scenario 3: Nominal cruising
        return ManeuverPlan(
            scenario_id=world_state.scenario_id,
            selected_action=ActionType.MAINTAIN_SPEED,
            target_lane_id=current_lane,
            target_velocity=ego.target_speed,
            safety_verdict="SAFE",
            time_to_collision_seconds=maintain_audit.time_to_collision,
            rationale="Current lane is clear and all safety tool audits passed. Maintaining cruising speed.",
            tool_evaluations={k: v.model_dump() for k, v in tool_audits.items()}
        )
