"""
Motion Extractor Module
CivixRecord-OS: Procedural Motion and Vote Extraction Engine
"""

from dataclasses import dataclass, field
import re
from typing import Any, Dict, List, Optional


@dataclass
class VoteRecord:
    in_favour: List[str] = field(default_factory=list)
    opposed: List[str] = field(default_factory=list)
    result: str = "PENDING"  # CARRIED, DEFEATED, PENDING


@dataclass
class CouncilMotion:
    motion_id: str
    timestamp_start: float
    timestamp_end: float
    mover: str
    seconder: Optional[str]
    motion_text: str
    motion_type: str = "MAIN"
    vote: VoteRecord = field(default_factory=VoteRecord)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes CouncilMotion into JSON-compatible dictionary."""
        return {
            "motion_id": self.motion_id,
            "timestamp_start": self.timestamp_start,
            "timestamp_end": self.timestamp_end,
            "mover": self.mover,
            "seconder": self.seconder,
            "motion_text": self.motion_text,
            "motion_type": self.motion_type,
            "outcome": self.vote.result,
        }


class MotionExtractor:
    """Extracts formal council motions, movers, seconders, and votes from meeting utterances."""

    _MOTION_PATTERNS = [
        re.compile(r"(?:i\s+)?move\s+that\s+(?P<text>[^.]+)", re.IGNORECASE),
        re.compile(r"motion\s+by\s+(?P<mover>[A-Za-z\s]+)\s+that\s+(?P<text>[^.]+)", re.IGNORECASE),
    ]

    _SECONDER_PATTERN = re.compile(
        r"(?:seconded\s+by|second\s+by|i('ll)?\s+second)\s+(?P<seconder>[A-Za-z\s]+)",
        re.IGNORECASE,
    )

    _VOTE_RESULT_PATTERN = re.compile(
        r"\b(?P<status>carried|defeated|passed|failed)\b", re.IGNORECASE
    )

    def __init__(self) -> None:
        pass

    def extract_motion(
        self,
        utterance: str,
        speaker: str,
        timestamp: float,
        motion_id: str = "M-001",
    ) -> Optional[CouncilMotion]:
        """Parses an utterance to detect if a formal motion was introduced."""
        if not utterance or not isinstance(utterance, str):
            raise ValueError("utterance must be a non-empty string")

        for pattern in self._MOTION_PATTERNS:
            match = pattern.search(utterance)
            if match:
                text = match.group("text").strip()
                mover = match.groupdict().get("mover", speaker).strip()
                return CouncilMotion(
                    motion_id=motion_id,
                    timestamp_start=timestamp,
                    timestamp_end=timestamp,
                    mover=mover,
                    seconder=None,
                    motion_text=text,
                    motion_type="MAIN",
                )
        return None

    def record_seconder(self, motion: CouncilMotion, utterance: str, speaker: str) -> bool:
        """Parses an utterance to detect if the motion was seconded."""
        if not motion:
            raise ValueError("motion cannot be None")
        match = self._SECONDER_PATTERN.search(utterance)
        if match:
            seconder = match.groupdict().get("seconder")
            motion.seconder = seconder.strip() if seconder else speaker.strip()
            return True
        return False

    def record_outcome(self, motion: CouncilMotion, utterance: str) -> str:
        """Determines if a motion was carried or defeated from voting declaration."""
        if not motion:
            raise ValueError("motion cannot be None")
        match = self._VOTE_RESULT_PATTERN.search(utterance)
        if match:
            status = match.group("status").lower()
            if status in ("carried", "passed"):
                motion.vote.result = "CARRIED"
            elif status in ("defeated", "failed"):
                motion.vote.result = "DEFEATED"
            return motion.vote.result
        return motion.vote.result

    def extract_from_utterances(self, utterances: List[Dict[str, Any]]) -> List[CouncilMotion]:
        """Processes an ordered list of timestamped utterances to extract all motions and outcomes."""
        motions: List[CouncilMotion] = []
        active_motion: Optional[CouncilMotion] = None
        motion_counter = 1

        for item in utterances:
            text = str(item.get("text", "")).strip()
            speaker = str(item.get("speaker", "Unknown")).strip()
            ts = float(item.get("timestamp", 0.0))

            if not text:
                continue

            # Check if this introduces a new motion
            detected = self.extract_motion(text, speaker, ts, motion_id=f"M-{motion_counter:03d}")
            if detected:
                if active_motion:
                    motions.append(active_motion)
                active_motion = detected
                motion_counter += 1
                continue

            if active_motion:
                # Check for seconder
                if not active_motion.seconder:
                    if self.record_seconder(active_motion, text, speaker):
                        continue

                # Check for outcome/vote
                outcome = self.record_outcome(active_motion, text)
                if outcome != "PENDING":
                    active_motion.timestamp_end = ts
                    motions.append(active_motion)
                    active_motion = None

        if active_motion:
            motions.append(active_motion)

        return motions
