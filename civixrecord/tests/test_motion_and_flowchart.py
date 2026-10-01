"""
Unit Test Suite for CivixRecord-OS Motion & Flowchart Subsystems
Hermetic, offline test suite enforcing exact procedural verification.
"""

import unittest
from civixrecord.analysis.motion_extractor import MotionExtractor, CouncilMotion
from civixrecord.analysis.flowchart_generator import FlowchartGenerator


class TestCivixRecordAnalysis(unittest.TestCase):

    def setUp(self) -> None:
        self.extractor = MotionExtractor()

    def test_motion_extraction_clean_utterance(self) -> None:
        utterance = "Thank you Mayor, I move that Council adopt the 2026 Operating Budget as presented."
        speaker = "Councillor Smith"
        motion = self.extractor.extract_motion(utterance, speaker, timestamp=124.5, motion_id="M-101")

        self.assertIsNotNone(motion)
        self.assertEqual(motion.motion_id, "M-101")
        self.assertEqual(motion.mover, "Councillor Smith")
        self.assertIn("adopt the 2026 Operating Budget", motion.motion_text)
        self.assertEqual(motion.timestamp_start, 124.5)

    def test_seconder_and_outcome_recording(self) -> None:
        motion = CouncilMotion(
            motion_id="M-102",
            timestamp_start=200.0,
            timestamp_end=200.0,
            mover="Councillor Jones",
            seconder=None,
            motion_text="approve Bylaw 104-B",
            motion_type="MAIN",
        )

        seconded = self.extractor.record_seconder(motion, "I second Councillor Jones's motion", "Councillor Davis")
        self.assertTrue(seconded)
        self.assertIn("Councillor Jones", motion.seconder)

        outcome = self.extractor.record_outcome(motion, "All in favour? None opposed, motion is carried.")
        self.assertEqual(outcome, "CARRIED")
        self.assertEqual(motion.vote.result, "CARRIED")

    def test_flowchart_generation_mermaid(self) -> None:
        motion1 = CouncilMotion(
            motion_id="M-01",
            timestamp_start=10.0,
            timestamp_end=15.0,
            mover="Councillor Allen",
            seconder="Councillor Baker",
            motion_text="adopt the agenda",
            motion_type="PROCEDURAL",
        )
        motion1.vote.result = "CARRIED"

        motion2 = CouncilMotion(
            motion_id="M-02",
            timestamp_start=50.0,
            timestamp_end=65.0,
            mover="Councillor Baker",
            seconder="Councillor Clark",
            motion_text="rezone parcel 402",
            motion_type="MAIN",
        )
        motion2.vote.result = "DEFEATED"

        mermaid_doc = FlowchartGenerator.generate_mermaid("Regular Council Meeting", [motion1, motion2])

        self.assertIn("```mermaid", mermaid_doc)
        self.assertIn("flowchart TD", mermaid_doc)
        self.assertIn("Motion M-01", mermaid_doc)
        self.assertIn("adopt the agenda", mermaid_doc)
        self.assertIn("Approved & Enacted", mermaid_doc)
        self.assertIn("Motion M-02", mermaid_doc)
        self.assertIn("Rejected", mermaid_doc)
        self.assertIn("Meeting Adjourned", mermaid_doc)


if __name__ == "__main__":
    unittest.main()
