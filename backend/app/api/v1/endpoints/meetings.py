"""
Meeting Lifecycle & Ingestion Management Endpoints
"""

import uuid
from typing import Dict, List
from fastapi import APIRouter, HTTPException, status
from backend.app.models.schemas import MeetingCreate, MeetingResponse, MeetingPlatform

router = APIRouter()

# In-memory session database
_MEETINGS_DB: Dict[str, MeetingResponse] = {}


@router.post("/", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
def create_meeting(meeting_in: MeetingCreate) -> MeetingResponse:
    """Registers a new civic meeting session and allocates ingestion loopback pipes."""
    meeting_id = f"mtg-{uuid.uuid4().hex[:8]}"
    record = MeetingResponse(
        meeting_id=meeting_id,
        title=meeting_in.title,
        municipality=meeting_in.municipality,
        platform=meeting_in.platform,
        is_active=True,
        in_camera_locked=False,
        total_motions=0,
    )
    _MEETINGS_DB[meeting_id] = record
    return record


@router.get("/", response_model=List[MeetingResponse])
def list_meetings() -> List[MeetingResponse]:
    """Lists all active and recorded civic meetings."""
    return list(_MEETINGS_DB.values())


@router.get("/{meeting_id}", response_model=MeetingResponse)
def get_meeting(meeting_id: str) -> MeetingResponse:
    """Retrieves metadata and status of a specific meeting session."""
    if meeting_id not in _MEETINGS_DB:
        raise HTTPException(status_code=404, detail="Meeting session not found")
    return _MEETINGS_DB[meeting_id]


@router.post("/{meeting_id}/in-camera-lock")
def toggle_in_camera_lock(meeting_id: str, locked: bool) -> Dict[str, str]:
    """Enforces the mandatory in-camera statutory privacy fence, muting capture pipes."""
    if meeting_id not in _MEETINGS_DB:
        raise HTTPException(status_code=404, detail="Meeting session not found")
    
    _MEETINGS_DB[meeting_id].in_camera_locked = locked
    state_str = "MUTED_IN_CAMERA_SESSION" if locked else "UNMUTED_PUBLIC_SESSION"
    return {"meeting_id": meeting_id, "statutory_fence": state_str}
