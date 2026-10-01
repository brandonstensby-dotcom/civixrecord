"""
Flowchart Generator Module
CivixRecord-OS: Procedural Decision Tree and Flowchart Engine
"""

from typing import List, Optional
from civixrecord.analysis.motion_extractor import CouncilMotion


class FlowchartGenerator:
    """Generates standard Mermaid.js flowcharts depicting meeting procedural decisions."""

    @staticmethod
    def generate_mermaid(meeting_title: str = "Council Public Session", motions: Optional[List[CouncilMotion]] = None) -> str:
        """Synthesizes a structured Mermaid flowchart from recorded motions."""
        if isinstance(meeting_title, list) and motions is None:
            # Handle overloaded call format generate_mermaid(motions)
            motions = meeting_title
            meeting_title = "Council Public Session"
            
        if motions is None:
            motions = []

        lines = [
            "```mermaid",
            "flowchart TD",
            f"    Start([Meeting Call to Order: {meeting_title}])",
        ]

        prev_node = "Start"

        for idx, m in enumerate(motions, start=1):
            m_node = f"Motion_{idx}"
            vote_node = f"Vote_{idx}"
            outcome_node = f"Outcome_{idx}"

            escaped_text = m.motion_text.replace('"', "'")
            lines.append(f'    {prev_node} --> {m_node}["Motion {m.motion_id}: {escaped_text}"]')
            lines.append(f'    {m_node} -->|Moved by {m.mover}| {vote_node}{{"Recorded Vote"}}')

            if m.vote.result == "CARRIED":
                lines.append(f'    {vote_node} -->|Carried| {outcome_node}[Approved & Enacted]')
            elif m.vote.result == "DEFEATED":
                lines.append(f'    {vote_node} -->|Defeated| {outcome_node}[Rejected]')
            else:
                lines.append(f'    {vote_node} -->|Pending| {outcome_node}[Tabled / Referred]')

            prev_node = outcome_node

        lines.append(f"    {prev_node} --> Adjourn([Meeting Adjourned])")
        lines.append("```")

        return "\n".join(lines)
