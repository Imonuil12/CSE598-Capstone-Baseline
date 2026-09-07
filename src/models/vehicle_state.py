from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ActionType(str, Enum):
    MAINTAIN_SPEED = "MAINTAIN_SPEED"
    ACCELERATE = "ACCELERATE"
    SLOW_DOWN = "SLOW_DOWN"
    LANE_CHANGE_LEFT = "LANE_CHANGE_LEFT"
    LANE_CHANGE_RIGHT = "LANE_CHANGE_RIGHT"
    EMERGENCY_BRAKE = "EMERGENCY_BRAKE"


class EgoVehicle(BaseModel):
    id: str = "ego"
    lane_id: int = Field(..., description="Current lane index (0=leftmost, 1=center, 2=rightmost)")
    position_x: float = Field(..., description="Longitudinal position along the road (meters)")
    position_y: float = Field(..., description="Lateral position (meters)")
    velocity_x: float = Field(..., description="Longitudinal velocity (m/s)")
    velocity_y: float = Field(0.0, description="Lateral velocity (m/s)")
    target_speed: float = Field(25.0, description="Desired cruise speed (m/s)")


class ObstacleVehicle(BaseModel):
    id: str
    vehicle_type: str = Field("car", description="Type of vehicle: car, truck, motorcycle")
    lane_id: int = Field(..., description="Current lane index of obstacle")
    position_x: float = Field(..., description="Longitudinal position along the road (meters)")
    position_y: float = Field(..., description="Lateral position (meters)")
    velocity_x: float = Field(..., description="Longitudinal velocity (m/s)")
    velocity_y: float = Field(0.0, description="Lateral velocity (m/s)")


class LaneInfo(BaseModel):
    lane_id: int
    speed_limit: float = Field(29.0, description="Speed limit in m/s (approx 65 mph)")
    is_blocked: bool = False
    left_neighbor_id: Optional[int] = None
    right_neighbor_id: Optional[int] = None


class WorldState(BaseModel):
    scenario_id: str
    description: str
    ego_vehicle: EgoVehicle
    obstacles: List[ObstacleVehicle]
    lanes: List[LaneInfo]
    road_condition: str = "dry"
    weather: str = "clear"


class SafetyEvaluationResult(BaseModel):
    action: ActionType
    is_safe: bool
    time_to_collision: float = Field(..., description="Calculated Time-To-Collision in seconds (inf if no collision course)")
    min_distance: float = Field(..., description="Distance to nearest threat in meters")
    blindspot_clear: bool = True
    speed_compliant: bool = True
    details: str


class ManeuverPlan(BaseModel):
    scenario_id: str
    selected_action: ActionType
    target_lane_id: int
    target_velocity: float
    safety_verdict: str = Field(..., description="SAFE, CAUTION, or UNSAFE")
    time_to_collision_seconds: float
    rationale: str
    tool_evaluations: Dict[str, Any] = Field(default_factory=dict)
