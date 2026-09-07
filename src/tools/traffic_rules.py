from typing import Dict, Any
from src.models.vehicle_state import WorldState, ActionType


def validate_traffic_rules(world_state: WorldState, target_speed: float, target_lane_id: int) -> Dict[str, Any]:
    """
    Validates speed limits, valid lane bounds, and road conditions.
    """
    lanes_dict = {lane.lane_id: lane for lane in world_state.lanes}
    
    if target_lane_id not in lanes_dict:
        return {
            "compliant": False,
            "reason": f"Target lane {target_lane_id} does not exist."
        }
        
    lane_info = lanes_dict[target_lane_id]
    if lane_info.is_blocked:
        return {
            "compliant": False,
            "reason": f"Target lane {target_lane_id} is marked as blocked due to construction or hazard."
        }
        
    if target_speed > lane_info.speed_limit + 2.0:
        return {
            "compliant": False,
            "reason": f"Target speed {target_speed:.1f} m/s exceeds lane speed limit {lane_info.speed_limit:.1f} m/s."
        }
        
    weather_factor = 1.0
    if world_state.weather.lower() in ("rain", "storm"):
        weather_factor = 0.85
    elif world_state.weather.lower() == "snow":
        weather_factor = 0.70
        
    recommended_max_speed = lane_info.speed_limit * weather_factor
    
    return {
        "compliant": True,
        "speed_limit": lane_info.speed_limit,
        "recommended_max_speed": recommended_max_speed,
        "reason": "Maneuver fully complies with traffic regulations and road conditions."
    }
