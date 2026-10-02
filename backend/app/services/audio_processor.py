"""
CUSUM Acoustic Change-Point Detection and Audio Preprocessor
"""

import math
from typing import List, Tuple
from civixrecord.core_bridge.machine_code_bridge import MachineCodeBridge


class AudioStreamProcessor:
    """Processes raw PCM audio chunks, detecting speaker turn changes using CUSUM statistics."""

    def __init__(self, sample_rate: int = 16000, threshold: float = 0.85, drift: float = 0.05) -> None:
        self.sample_rate = sample_rate
        self.threshold = threshold
        self.drift = drift
        self.bridge = MachineCodeBridge()
        self._positive_cusum = 0.0
        self._negative_cusum = 0.0
        self._mean_energy = 0.0
        self._sample_count = 0

    def compute_frame_energy(self, pcm_samples: bytes) -> float:
        """Calculates root mean square (RMS) signal energy of PCM 16-bit buffer."""
        if not pcm_samples:
            return 0.0
        
        sample_count = len(pcm_samples) // 2
        if sample_count == 0:
            return 0.0

        # Fast RMS calculation
        sum_sq = 0.0
        for i in range(0, len(pcm_samples) - 1, 2):
            sample = int.from_bytes(pcm_samples[i:i+2], byteorder="little", signed=True)
            sum_sq += sample * sample

        mean_sq = sum_sq / sample_count
        return math.sqrt(mean_sq)

    def process_chunk(self, chunk_pcm: bytes) -> Tuple[bool, float]:
        """Returns (is_speaker_change, energy_level)."""
        energy = self.compute_frame_energy(chunk_pcm)
        
        self._sample_count += 1
        delta = energy - self._mean_energy
        self._mean_energy += delta / self._sample_count
        
        # Cumulative Sum (CUSUM) tracking
        self._positive_cusum = max(0.0, self._positive_cusum + (energy - self._mean_energy - self.drift))
        self._negative_cusum = min(0.0, self._negative_cusum + (energy - self._mean_energy + self.drift))
        
        is_change_point = (self._positive_cusum > self.threshold) or (abs(self._negative_cusum) > self.threshold)
        
        if is_change_point:
            self._positive_cusum = 0.0
            self._negative_cusum = 0.0

        return is_change_point, energy
