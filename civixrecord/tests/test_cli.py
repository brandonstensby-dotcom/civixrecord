"""
CLI Integration Test Suite for CivixRecord
"""

import json
from click.testing import CliRunner

from civixrecord.cli import cli


class TestCivixRecordCli:

    def test_cli_version(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.4.1" in result.output

    def test_cli_doctor(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["doctor"])
        assert result.exit_code == 0
        assert "CivixRecord-OS System Architecture Diagnostic Doctor" in result.output
        assert "System Status: OPERATIONAL" in result.output

    def test_cli_bridge_probe(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["bridge", "--probe"])
        assert result.exit_code == 0
        assert "spec_standard" in result.output
        assert "CIVIX-IR-v2.1" in result.output

    def test_cli_bridge_benchmark(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["bridge", "--benchmark"])
        assert result.exit_code == 0
        assert "1,000 dispatches completed" in result.output

    def test_cli_analyze_flowchart(self, tmp_path) -> None:
        transcript_file = tmp_path / "sample_transcript.json"
        output_file = tmp_path / "output.mmd"

        sample_data = [
            {"speaker": "Mayor", "text": "We are now considering Bylaw 2026-12.", "timestamp": 10.0},
            {"speaker": "Councillor Smith", "text": "I move that Bylaw 2026-12 be adopted.", "timestamp": 25.0},
            {"speaker": "Councillor Adams", "text": "I second the motion.", "timestamp": 30.0},
            {"speaker": "Mayor", "text": "All in favour? Motion carried unanimously.", "timestamp": 45.0},
        ]
        transcript_file.write_text(json.dumps(sample_data), encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "-t", str(transcript_file), "-o", str(output_file)])
        assert result.exit_code == 0
        assert "Successfully extracted 1 formal motions/actions." in result.output
        assert output_file.exists()
        assert "flowchart TD" in output_file.read_text(encoding="utf-8")
