import math
from typing import List, Dict, Any
from src.models.vehicle_state import (
    WorldState, EgoVehicle, ObstacleVehicle, ActionType, SafetyEvaluationResult
)

# Safety thresholds
TTC_CRITICAL_THRESHOLD = 3.0  # seconds - below this is high risk
BLINDSPOT_REAR_GAP = 12.0     # meters minimum rear clearance in target lane
BLINDSPOT_FRONT_GAP = 15.0    # meters minimum front clearance in target lane


def calculate_ttc(ego_x: float, ego_vx: float, obs_x: float, obs_vx: float) -> float:
    """
    Calculates Time-To-Collision (TTC) between ego and an obstacle in the same lane.
    If ego is behind obstacle and moving faster, TTC = (obs_x - ego_x) / (ego_vx - obs_vx).
    Returns float('inf') if no collision course exists.
    """
    dx = obs_x - ego_x
    dv = ego_vx - obs_vx
    
    if dx > 0 and dv > 0:
        return dx / dv
    elif dx < 0 and dv < 0: # Ego is ahead of obstacle and moving slower
        return abs(dx) / abs(dv)
    return float('inf')


def evaluate_action_safety(world_state: WorldState, action: ActionType) -> SafetyEvaluationResult:
    """
    Evaluates safety parameters (TTC, gap clearance, blind spot) for a specific candidate maneuver.
    """
    ego = world_state.ego_vehicle
    obstacles = world_state.obstacles
    
    target_lane = ego.lane_id
    simulated_vx = ego.velocity_x
    
    if action == ActionType.MAINTAIN_SPEED:
        simulated_vx = ego.velocity_x
    elif action == ActionType.ACCELERATE:
        simulated_vx = ego.velocity_x + 3.0
    elif action == ActionType.SLOW_DOWN:
        simulated_vx = max(0.0, ego.velocity_x - 3.0)
    elif action == ActionType.EMERGENCY_BRAKE:
        simulated_vx = max(0.0, ego.velocity_x - 8.0)
    elif action == ActionType.LANE_CHANGE_LEFT:
        target_lane = ego.lane_id - 1
    elif action == ActionType.LANE_CHANGE_RIGHT:
        target_lane = ego.lane_id + 1
        
    # Check lane validity
    lane_ids = [lane.lane_id for lane in world_state.lanes if not lane.is_blocked]
    if target_lane not in lane_ids:
        return SafetyEvaluationResult(
            action=action,
            is_safe=False,
            time_to_collision=0.0,
            min_distance=0.0,
            blindspot_clear=False,
            speed_compliant=False,
            details=f"Target lane {target_lane} is blocked or out of bounds."
        )
        
    # Find vehicles in target lane
    target_lane_obs = [obs for obs in obstacles if obs.lane_id == target_lane]
    
    min_ttc = float('inf')
    min_dist = float('inf')
    blindspot_clear = True
    
    for obs in target_lane_obs:
        dist = abs(obs.position_x - ego.position_x)
        if dist < min_dist:
            min_dist = dist
            
        # Check blindspot gap for lane changes
        if action in (ActionType.LANE_CHANGE_LEFT, ActionType.LANE_CHANGE_RIGHT):
            # Vehicle behind us in target lane
            if obs.position_x < ego.position_x and (ego.position_x - obs.position_x) < BLINDSPOT_REAR_GAP:
                blindspot_clear = False
            # Vehicle ahead of us in target lane
            elif obs.position_x >= ego.position_x and (obs.position_x - ego.position_x) < BLINDSPOT_FRONT_GAP:
                blindspot_clear = False
                
        # Calculate TTC for lead vehicles ahead
        if obs.position_x > ego.position_x:
            ttc = calculate_ttc(ego.position_x, simulated_vx, obs.position_x, obs.velocity_x)
            if ttc < min_ttc:
                min_ttc = ttc
                
    is_safe = (min_ttc >= TTC_CRITICAL_THRESHOLD) and blindspot_clear
    
    # Emergency brake is always safe if needed
    if action == ActionType.EMERGENCY_BRAKE:
        is_safe = True
        
    details_str = (
        f"Action: {action.value} | Target Lane: {target_lane} | Min TTC: {min_ttc:.2f}s | "
        f"Min Dist: {min_dist:.1f}m | Blindspot Clear: {blindspot_clear}"
    )
    
    return SafetyEvaluationResult(
        action=action,
        is_safe=is_safe,
        time_to_collision=min_ttc if min_ttc != float('inf') else 999.0,
        min_distance=min_dist if min_dist != float('inf') else 999.0,
        blindspot_clear=blindspot_clear,
        speed_compliant=True,
        details=details_str
    )
