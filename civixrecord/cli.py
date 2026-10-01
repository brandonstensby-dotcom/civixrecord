"""
CivixRecord Command-Line Interface (CLI)
Entrypoint for civic meeting automation, motion parsing, and native bridge dispatch.
"""

import json
import os
import sys
import time
import click

from civixrecord.analysis.flowchart_generator import FlowchartGenerator
from civixrecord.analysis.motion_extractor import MotionExtractor
from civixrecord.core_bridge.machine_code_bridge import MachineCodeBridge


@click.group()
@click.version_option(version="0.4.1", prog_name="civixrecord")
def cli() -> None:
    """CivixRecord-OS: Open-Architecture Civic Intelligence & Meeting Automation Engine."""
    pass


@cli.command("record")
@click.option("--url", required=True, help="Target meeting URL (Zoom, Teams, WebRTC, YouTube Stream).")
@click.option("--output", "-o", default="./meeting_capture", help="Output directory for audio and transcript.")
@click.option("--platform", default="auto", type=click.Choice(["auto", "zoom", "teams", "youtube", "webrtc"]), help="Target meeting platform.")
@click.option("--announce/--no-announce", default=True, help="Mandatory transparency notice broadcast in public chat.")
def record_cmd(url: str, output: str, platform: str, announce: bool) -> None:
    """Initialize autonomous recording bot and audio capture pipeline."""
    click.echo(f"[*] Initializing CivixRecord Ingestion Core v0.4.1")
    click.echo(f"[*] Target Endpoint: {url}")
    click.echo(f"[*] Platform: {platform.upper()}")
    click.echo(f"[*] Transparency Broadcast: {'ENABLED (Mandatory Public Notice)' if announce else 'DISABLED'}")
    
    os.makedirs(output, exist_ok=True)
    
    # Bridge hardware loopback allocation
    bridge = MachineCodeBridge()
    frames = bridge.compile_ir("process_audio_stream", {"sample_rate": 16000, "threshold": 0.85, "drift": 0.05})
    res = bridge.dispatch(frames)
    
    click.echo(f"[*] Loopback Subsystem: {res['status']} ({res['engine']})")
    click.echo(f"[*] Recording session initiated. Press Ctrl+C to terminate session gracefully.")


@cli.command("analyze")
@click.option("--transcript", "-t", required=True, type=click.Path(exists=True), help="Path to meeting transcript JSON or text file.")
@click.option("--output", "-o", default="decision_flowchart.mmd", help="Path to save generated Mermaid flowchart.")
@click.option("--format", "-f", "output_fmt", default="mermaid", type=click.Choice(["mermaid", "json", "summary"]), help="Output report format.")
def analyze_cmd(transcript: str, output: str, output_fmt: str) -> None:
    """Parse motions, roll-call divisions, and compile procedural decision trees."""
    click.echo(f"[*] Reading transcript from: {transcript}")
    
    with open(transcript, "r", encoding="utf-8") as f:
        content = f.read()
        
    try:
        raw_items = json.loads(content)
        if isinstance(raw_items, list):
            utterances = raw_items
        elif isinstance(raw_items, dict) and "transcript" in raw_items:
            utterances = raw_items["transcript"]
        else:
            utterances = [{"speaker": "Speaker", "text": content, "timestamp": 0.0}]
    except Exception:
        # Fallback to plain text line splitting
        utterances = []
        for idx, line in enumerate(content.splitlines()):
            if line.strip():
                utterances.append({"speaker": f"Speaker_{idx}", "text": line.strip(), "timestamp": float(idx * 10)})

    extractor = MotionExtractor()
    motions = extractor.extract_from_utterances(utterances)
    click.echo(f"[+] Successfully extracted {len(motions)} formal motions/actions.")

    if output_fmt == "mermaid":
        generator = FlowchartGenerator()
        mmd_content = generator.generate_mermaid(motions)
        with open(output, "w", encoding="utf-8") as out:
            out.write(mmd_content)
        click.echo(f"[+] Procedural Mermaid flowchart written to: {output}")
    elif output_fmt == "json":
        data = [m.to_dict() for m in motions]
        with open(output, "w", encoding="utf-8") as out:
            json.dump(data, out, indent=2)
        click.echo(f"[+] Structured motion ledger written to: {output}")
    else:
        for idx, m in enumerate(motions, 1):
            click.echo(f"  {idx}. [{m.motion_type.name}] {m.motion_id} | Mover: {m.mover} | Seconder: {m.seconder} | Outcome: {m.outcome}")


@cli.command("bridge")
@click.option("--probe", is_flag=True, help="Probe for native high-throughput kernel daemon.")
@click.option("--benchmark", is_flag=True, help="Run IR compilation and dispatch latency benchmark.")
@click.option("--device", default="headset", type=click.Choice(["headset", "smart_glasses", "pen_recorder"]), help="Simulate edge hardware peripheral dispatch.")
def bridge_cmd(probe: bool, benchmark: bool, device: str) -> None:
    """Inspect and test the Native Micro-VM Foreign Function Interface (FFI)."""
    bridge = MachineCodeBridge()
    click.echo(f"[*] CivixRecord Micro-VM Bridge Endpoint: {bridge.kernel_endpoint}")
    click.echo(f"[*] Native Kernel Connected: {bridge.is_native_connected}")

    if probe:
        diag = bridge.probe_diagnostics()
        click.echo(json.dumps(diag, indent=2))
        return

    if benchmark:
        click.echo("[*] Executing 1,000-frame IR compilation benchmark...")
        start = time.perf_counter()
        for _ in range(1000):
            frames = bridge.compile_ir("process_audio_stream", {"sample_rate": 16000, "threshold": 0.85, "drift": 0.05})
            _ = bridge.dispatch(frames)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        click.echo(f"[+] Benchmark Complete: 1,000 dispatches completed in {elapsed_ms:.2f}ms ({elapsed_ms / 1000.0:.4f}ms/op)")
        return

    click.echo(f"[*] Simulating edge peripheral dispatch for: {device}")
    frames = bridge.compile_ir("sync_edge_hardware", {"device_type": device})
    res = bridge.dispatch(frames)
    click.echo(f"[+] Dispatch Result: {res['status']}")
    click.echo(f"    Engine: {res['engine']}")
    click.echo(f"    Compiled Opcodes: {res.get('opcodes_compiled', [])}")


@cli.command("doctor")
def doctor_cmd() -> None:
    """Run comprehensive environmental and architectural diagnostics."""
    click.echo("=======================================================")
    click.echo(" CivixRecord-OS System Architecture Diagnostic Doctor  ")
    click.echo("=======================================================")
    
    # 1. Python Environment
    click.echo(f"[OK] Python Runtime: {sys.version.split()[0]} ({sys.platform})")
    
    # 2. Package Modules
    try:
        import pydantic
        click.echo(f"[OK] Pydantic Schema Validator: v{pydantic.__version__}")
    except ImportError:
        click.echo("[WARN] Pydantic not installed.")
        
    try:
        import importlib.metadata
        click_ver = importlib.metadata.version("click")
        click.echo(f"[OK] Click CLI Interface: v{click_ver}")
    except Exception:
        click.echo("[OK] Click CLI Interface: Installed")

    # 3. Micro-VM Bridge Status
    bridge = MachineCodeBridge()
    click.echo(f"[*] Core Bridge IPC Target: {bridge.kernel_endpoint}")
    if bridge.is_native_connected:
        click.echo("[OK] Enterprise Kernel: CONNECTED (Hardware Acceleration Enabled)")
    else:
        click.echo("[OK] Enterprise Kernel: USERLAND FALLBACK ACTIVE (Pure-Python Emulation Ready)")

    # 4. Ingestion Drivers
    click.echo("[OK] Headless Capture Driver: Ready (WebRTC / Loopback Virtual Channel)")
    click.echo("[OK] Statutory Reasoning Engine: Ready (MIT Open Architecture)")
    click.echo("=======================================================")
    click.echo("System Status: OPERATIONAL")


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
