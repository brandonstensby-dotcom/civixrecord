"""
Motion Parsing & Decision Flowchart Endpoints
"""

from typing import List
from fastapi import APIRouter, HTTPException
from backend.app.models.schemas import Utterance, MotionResponse, DecisionTreeResponse, MotionStatus
from civixrecord.analysis.motion_extractor import MotionExtractor, CouncilMotion
from civixrecord.analysis.flowchart_generator import FlowchartGenerator

router = APIRouter()
_extractor = MotionExtractor()
_flowchart_gen = FlowchartGenerator()


@router.post("/parse", response_model=List[MotionResponse])
def parse_motions_from_transcript(utterances: List[Utterance]) -> List[MotionResponse]:
    """Ingests meeting utterances and extracts formal motions, movers, seconders, and outcomes."""
    raw_dicts = [u.model_dump() for u in utterances]
    motions = _extractor.extract_from_utterances(raw_dicts)
    
    responses: List[MotionResponse] = []
    for m in motions:
        status_enum = MotionStatus.PENDING
        if m.vote.result == "CARRIED":
            status_enum = MotionStatus.CARRIED
        elif m.vote.result == "DEFEATED":
            status_enum = MotionStatus.DEFEATED
            
        responses.append(MotionResponse(
            motion_id=m.motion_id,
            timestamp_start=m.timestamp_start,
            timestamp_end=m.timestamp_end,
            mover=m.mover,
            seconder=m.seconder,
            motion_text=m.motion_text,
            motion_type=m.motion_type,
            outcome=status_enum,
            votes_for=m.vote.in_favour,
            votes_against=m.vote.opposed,
        ))
    return responses


@router.post("/generate-tree", response_model=DecisionTreeResponse)
def generate_decision_tree(meeting_title: str, utterances: List[Utterance]) -> DecisionTreeResponse:
    """Compiles meeting transcript into an interactive Mermaid.js procedural flowchart."""
    raw_dicts = [u.model_dump() for u in utterances]
    motions = _extractor.extract_from_utterances(raw_dicts)
    mermaid_code = _flowchart_gen.generate_mermaid(meeting_title, motions)
    
    return DecisionTreeResponse(
        meeting_id="generated",
        title=meeting_title,
        motion_count=len(motions),
        mermaid_diagram=mermaid_code,
    )
