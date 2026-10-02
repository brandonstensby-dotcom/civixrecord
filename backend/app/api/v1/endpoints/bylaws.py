"""
CivixRecord-OS Municipal Procedure & Bylaw Compliance Endpoints
Statutory municipal procedure index, quorum verification, and speaking limit timers
"""

import math
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from backend.app.models.schemas import (
    ProcedureRule,
    QuorumCheckRequest,
    QuorumCheckResponse,
    SpeakingTimerRequest,
    SpeakingTimerResponse,
)

router = APIRouter()

# Procedural Bylaw Rules Registry (Standard Canadian/North American Municipal Standing Rules)
_PROCEDURE_RULES: List[ProcedureRule] = [
    ProcedureRule(
        rule_id="RULE-001",
        title="Quorum of Council",
        category="Governance",
        description="A majority of the validly elected members of council constitutes a quorum unless otherwise defined in the municipal charter.",
        threshold="> 50% voting seats",
        statutory_reference="Municipal Government Act s. 167",
    ),
    ProcedureRule(
        rule_id="RULE-002",
        title="Public Delegation Speaking Time Limits",
        category="Delegations",
        description="Registered public delegations are entitled to a maximum duration of 5 minutes to address council, extendable only by unanimous consent.",
        threshold="300 seconds (5 min)",
        statutory_reference="Council Procedural Bylaw Part IV",
    ),
    ProcedureRule(
        rule_id="RULE-003",
        title="Elected Member Debate Limit",
        category="Debate",
        description="Elected members may speak once to each motion for no more than 5 minutes during general debate before yielding the floor.",
        threshold="300 seconds (5 min)",
        statutory_reference="Council Procedural Bylaw Part V",
    ),
    ProcedureRule(
        rule_id="RULE-004",
        title="In-Camera Closed Session Statutory Grounds",
        category="Confidentiality",
        description="Council may close all or part of a meeting to the public only for FOIP-qualifying subjects: land acquisition, personnel, or legal advice.",
        threshold="Two-thirds majority resolution required",
        statutory_reference="Municipal Government Act s. 197",
    ),
    ProcedureRule(
        rule_id="RULE-005",
        title="Recording of Votes and Recorded Vote Request",
        category="Voting",
        description="Any member may request a recorded vote prior to the vote being taken; upon such request, the minutes must record the name of each member and their vote.",
        threshold="Single member request",
        statutory_reference="Municipal Government Act s. 185",
    ),
    ProcedureRule(
        rule_id="RULE-006",
        title="Point of Order and Privilege",
        category="Order",
        description="A point of order takes precedence over all other business; the presiding officer must immediately rule on the point without debate.",
        threshold="Immediate suspension of floor debate",
        statutory_reference="Roberts Rules of Order s. 23",
    ),
]

_DEFAULT_SPEAKING_LIMITS = {
    "delegate": 300,       # 5 minutes
    "public": 300,         # 5 minutes
    "councillor": 300,     # 5 minutes
    "mayor": 600,          # 10 minutes
    "staff": 600,          # 10 minutes
    "presentation": 900,   # 15 minutes
}


@router.get("/rules", response_model=List[ProcedureRule])
def list_procedure_rules(category: Optional[str] = Query(None, description="Filter rules by procedural category")) -> List[ProcedureRule]:
    """Retrieves the statutory municipal procedure index and parliamentary rules."""
    if category:
        filtered = [r for r in _PROCEDURE_RULES if r.category.lower() == category.lower()]
        return filtered
    return _PROCEDURE_RULES


@router.get("/rules/{rule_id}", response_model=ProcedureRule)
def get_procedure_rule(rule_id: str) -> ProcedureRule:
    """Retrieves details of a specific procedural bylaw rule by ID."""
    for rule in _PROCEDURE_RULES:
        if rule.rule_id.upper() == rule_id.upper():
            return rule
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Procedural rule '{rule_id}' not found",
    )


@router.post("/quorum/verify", response_model=QuorumCheckResponse)
def verify_quorum(request: QuorumCheckRequest) -> QuorumCheckResponse:
    """
    Verifies statutory quorum for council or committee meetings.
    Formula: required = floor(total_seats * threshold) + 1.
    """
    if request.present_members > request.total_seats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Present members cannot exceed total seats",
        )

    threshold = request.custom_quorum_percent if request.custom_quorum_percent is not None else 0.50
    # Statutory quorum requires more than 50% (majority): floor(total * 0.5) + 1
    required_seats = math.floor(request.total_seats * threshold) + 1
    is_met = request.present_members >= required_seats
    pct = round((request.present_members / request.total_seats) * 100, 2)

    detail_msg = (
        f"Quorum is SATISFIED ({request.present_members}/{request.total_seats} members present, {pct}%)."
        if is_met
        else f"Quorum FAILED ({request.present_members}/{request.total_seats} members present; {required_seats} required for majority)."
    )

    return QuorumCheckResponse(
        is_quorum_met=is_met,
        total_seats=request.total_seats,
        present_members=request.present_members,
        required_seats=required_seats,
        quorum_percentage=pct,
        detail=detail_msg,
    )


@router.post("/speaking-timer", response_model=SpeakingTimerResponse)
def calculate_speaking_timer(request: SpeakingTimerRequest) -> SpeakingTimerResponse:
    """
    Calculates statutory speaking limits and warning timers based on speaker role
    in accordance with municipal procedural bylaws.
    """
    role_key = request.role.lower().strip()
    base_limit = _DEFAULT_SPEAKING_LIMITS.get(role_key, 300)

    if request.custom_limit_seconds is not None:
        allowed = max(10, request.custom_limit_seconds)
    else:
        allowed = base_limit

    # Warning alert fires at 60 seconds remaining or 20% of time
    warning_threshold = min(60, max(15, int(allowed * 0.2)))

    return SpeakingTimerResponse(
        speaker=request.speaker,
        role=request.role,
        allowed_seconds=allowed,
        warning_seconds=warning_threshold,
        is_expired=False,
        message=f"Speaker '{request.speaker}' allocated {allowed}s ({allowed // 60}m {allowed % 60}s) with warning at {warning_threshold}s remaining.",
    )
