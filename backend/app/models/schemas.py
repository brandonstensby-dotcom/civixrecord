"""
CivixRecord-OS Backend API Schemas
Open-Source Civic Intelligence Platform Data Models
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class MeetingPlatform(str, Enum):
    ZOOM = "zoom"
    TEAMS = "teams"
    YOUTUBE = "youtube"
    WEBRTC = "webrtc"
    MANUAL = "manual"


class MotionStatus(str, Enum):
    PENDING = "PENDING"
    CARRIED = "CARRIED"
    DEFEATED = "DEFEATED"
    TABLED = "TABLED"


class Utterance(BaseModel):
    speaker: str
    text: str
    timestamp: float
    confidence: float = 0.95


class MotionCreate(BaseModel):
    motion_id: str
    motion_text: str
    mover: str
    seconder: Optional[str] = None
    motion_type: str = "MAIN"


class MotionResponse(BaseModel):
    motion_id: str
    timestamp_start: float
    timestamp_end: float
    mover: str
    seconder: Optional[str] = None
    motion_text: str
    motion_type: str = "MAIN"
    outcome: MotionStatus
    votes_for: List[str] = []
    votes_against: List[str] = []


class MeetingCreate(BaseModel):
    title: str
    municipality: str
    meeting_url: Optional[str] = None
    platform: MeetingPlatform = MeetingPlatform.ZOOM
    scheduled_start: Optional[datetime] = None


class MeetingResponse(BaseModel):
    meeting_id: str
    title: str
    municipality: str
    platform: MeetingPlatform
    is_active: bool = False
    in_camera_locked: bool = False
    total_motions: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionTreeResponse(BaseModel):
    meeting_id: str
    title: str
    motion_count: int
    mermaid_diagram: str
    svg_render_url: Optional[str] = None


# WebRTC Signaling Schemas
class WebRTCOffer(BaseModel):
    meeting_id: str
    sdp: str
    type: str = "offer"


class WebRTCAnswer(BaseModel):
    meeting_id: str
    sdp: str
    type: str = "answer"


# Statutory & Bylaw Procedural Schemas
class ProcedureRule(BaseModel):
    rule_id: str
    title: str
    category: str
    description: str
    threshold: Optional[str] = None
    statutory_reference: Optional[str] = None


class QuorumCheckRequest(BaseModel):
    total_seats: int = Field(gt=0, description="Total statutory seats on council or committee")
    present_members: int = Field(ge=0, description="Number of voting members currently in attendance")
    custom_quorum_percent: Optional[float] = Field(None, ge=0.0, le=1.0, description="Custom quorum threshold (default: 0.50)")


class QuorumCheckResponse(BaseModel):
    is_quorum_met: bool
    total_seats: int
    present_members: int
    required_seats: int
    quorum_percentage: float
    detail: str


class SpeakingTimerRequest(BaseModel):
    speaker: str
    role: str = "delegate"  # e.g., delegate, councillor, mayor, staff
    custom_limit_seconds: Optional[int] = None


class SpeakingTimerResponse(BaseModel):
    speaker: str
    role: str
    allowed_seconds: int
    warning_seconds: int
    is_expired: bool = False
    message: str
