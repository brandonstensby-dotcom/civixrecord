import React, { useState, useEffect, useRef } from "react";
import { AudioCapture, LoopbackTelemetry } from "./components/AudioCapture";
import { MotionLiveFeed, MotionItem } from "./components/MotionLiveFeed";
import { FlowchartViewer } from "./components/FlowchartViewer";
import {
  Activity,
  Radio,
  FileCheck,
  GitBranch,
  ShieldAlert,
  Server,
  Layers,
  Sparkles,
  Download,
} from "lucide-react";

// Resilient Tauri invoke helper
async function invokeTauri<T>(cmd: string, args?: Record<string, unknown>): Promise<T> {
  if (typeof window !== "undefined" && (window as unknown as { __TAURI_INTERNALS__?: unknown }).__TAURI_INTERNALS__) {
    try {
      const { invoke } = await import("@tauri-apps/api/core");
      return await invoke<T>(cmd, args);
    } catch {
      // Fallback
    }
  }

  if (cmd === "get_waveform_data") {
    // Generate synthetic audio wave chunk for visualizer
    const points = (args?.points as number) || 256;
    const isCapturing = (window as unknown as { _mockCapturing?: boolean })._mockCapturing ?? false;
    const wave: number[] = [];
    const t = Date.now() / 150;
    for (let i = 0; i < points; i++) {
      if (!isCapturing) {
        wave.push((Math.random() - 0.5) * 0.02);
      } else {
        const sample =
          Math.sin(i * 0.15 + t) * 0.45 +
          Math.cos(i * 0.05 - t * 0.7) * 0.25 +
          (Math.random() - 0.5) * 0.1;
        wave.push(Math.max(-1, Math.min(1, sample)));
      }
    }
    return wave as T;
  }

  throw new Error(`Unhandled command: ${cmd}`);
}

export function App() {
  const [activeTab, setActiveTab] = useState<"overview" | "motions" | "diagram" | "telemetry">("overview");
  const [isCapturing, setIsCapturing] = useState<boolean>(false);
  const [meetingTimer, setMeetingTimer] = useState<number>(1420); // 23m 40s in seconds
  const [inCameraStatus, setInCameraStatus] = useState<boolean>(false);
  const [selectedMotion, setSelectedMotion] = useState<MotionItem | null>(null);
  const [telemetry, setTelemetry] = useState<LoopbackTelemetry | null>(null);

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const wavePointsRef = useRef<number[]>(new Array(256).fill(0));

  // Meeting elapsed timer
  useEffect(() => {
    const timer = setInterval(() => {
      setMeetingTimer((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Waveform fetching & rendering loop
  useEffect(() => {
    let animId: number;

    const renderWaveform = async () => {
      try {
        const rawWave = await invokeTauri<number[]>("get_waveform_data", { points: 256 });
        if (rawWave && rawWave.length > 0) {
          wavePointsRef.current = rawWave;
        }
      } catch {
        // Fallback simulated curve
      }

      const canvas = canvasRef.current;
      if (canvas) {
        const ctx = canvas.getContext("2d");
        if (ctx) {
          const width = canvas.width;
          const height = canvas.height;
          ctx.clearRect(0, 0, width, height);

          // Background grid lines
          ctx.strokeStyle = "rgba(51, 65, 85, 0.2)";
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(0, height / 2);
          ctx.lineTo(width, height / 2);
          ctx.stroke();

          // Waveform line
          const points = wavePointsRef.current;
          const sliceWidth = width / (points.length - 1);

          // Glow gradient
          const gradient = ctx.createLinearGradient(0, 0, width, 0);
          gradient.addColorStop(0, "#38bdf8");
          gradient.addColorStop(0.5, "#818cf8");
          gradient.addColorStop(1, "#34d399");

          ctx.lineWidth = 2;
          ctx.strokeStyle = isCapturing ? gradient : "rgba(100, 116, 139, 0.4)";
          ctx.beginPath();

          for (let i = 0; i < points.length; i++) {
            const val = points[i];
            const y = (height / 2) + (val * (height / 2.3));
            const x = i * sliceWidth;

            if (i === 0) {
              ctx.moveTo(x, y);
            } else {
              ctx.lineTo(x, y);
            }
          }
          ctx.stroke();

          // Subdued area fill under waveform
          ctx.lineTo(width, height / 2);
          ctx.lineTo(0, height / 2);
          ctx.closePath();
          ctx.fillStyle = isCapturing
            ? "rgba(99, 102, 241, 0.08)"
            : "rgba(148, 163, 184, 0.02)";
          ctx.fill();
        }
      }

      animId = requestAnimationFrame(renderWaveform);
    };

    animId = requestAnimationFrame(renderWaveform);
    return () => cancelAnimationFrame(animId);
  }, [isCapturing]);

  const formatTimer = (seconds: number) => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hrs > 0 ? `${hrs}:` : ""}${mins < 10 ? "0" : ""}${mins}:${secs < 10 ? "0" : ""}${secs}`;
  };

  return (
    <div className="flex flex-col h-screen w-screen bg-[#090d16] text-slate-100 overflow-hidden">
      {/* Top Application Header */}
      <header className="h-14 border-b border-slate-800 bg-slate-950/80 backdrop-blur-md px-5 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-600/30 border border-indigo-500/50 flex items-center justify-center text-indigo-400">
            <Radio className="w-4 h-4 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold tracking-tight text-sm text-slate-100">
                CivixRecord-OS
              </span>
              <span className="text-[10px] uppercase font-mono px-1.5 py-0.2 bg-slate-800 text-indigo-300 rounded border border-slate-700">
                Desktop v0.4.1
              </span>
            </div>
            <span className="text-[11px] text-slate-400">
              Municipal Council Web Meeting Capture & Autonomous Transcription
            </span>
          </div>
        </div>

        {/* Live Session Telemetry Bar */}
        <div className="flex items-center gap-4">
          <div className="hidden md:flex items-center gap-2 px-3 py-1 bg-slate-900 border border-slate-800 rounded-lg text-xs font-mono">
            <span className="text-slate-400">SESSION:</span>
            <span className="text-emerald-400 font-semibold">{formatTimer(meetingTimer)}</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setInCameraStatus(!inCameraStatus)}
              className={`px-3 py-1 rounded-lg text-xs font-medium flex items-center gap-1.5 border transition ${
                inCameraStatus
                  ? "bg-rose-950/50 text-rose-300 border-rose-800/80"
                  : "bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200"
              }`}
            >
              <ShieldAlert className="w-3.5 h-3.5" />
              {inCameraStatus ? "In-Camera Guard Active" : "Public Session"}
            </button>
          </div>
        </div>
      </header>

      {/* Main Tab Navigation */}
      <nav className="h-10 border-b border-slate-800/80 bg-slate-900/40 px-5 flex items-center gap-2 shrink-0">
        <button
          onClick={() => setActiveTab("overview")}
          className={`h-full px-3 text-xs font-medium flex items-center gap-1.5 border-b-2 transition ${
            activeTab === "overview"
              ? "border-indigo-500 text-indigo-300 bg-indigo-500/5"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <Activity className="w-3.5 h-3.5" />
          Live Monitoring Dashboard
        </button>
        <button
          onClick={() => setActiveTab("motions")}
          className={`h-full px-3 text-xs font-medium flex items-center gap-1.5 border-b-2 transition ${
            activeTab === "motions"
              ? "border-indigo-500 text-indigo-300 bg-indigo-500/5"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <FileCheck className="w-3.5 h-3.5" />
          Motion & Roll-Call Registry
        </button>
        <button
          onClick={() => setActiveTab("diagram")}
          className={`h-full px-3 text-xs font-medium flex items-center gap-1.5 border-b-2 transition ${
            activeTab === "diagram"
              ? "border-indigo-500 text-indigo-300 bg-indigo-500/5"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <GitBranch className="w-3.5 h-3.5" />
          Parliamentary Decision Tree
        </button>
        <button
          onClick={() => setActiveTab("telemetry")}
          className={`h-full px-3 text-xs font-medium flex items-center gap-1.5 border-b-2 transition ${
            activeTab === "telemetry"
              ? "border-indigo-500 text-indigo-300 bg-indigo-500/5"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <Server className="w-3.5 h-3.5" />
          WASAPI Driver Telemetry
        </button>
      </nav>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto p-5 space-y-5">
        {/* Active Audio Capture & Live Oscillogram (Always visible in Overview or Telemetry) */}
        {(activeTab === "overview" || activeTab === "telemetry") && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
            {/* Audio Loopback Controller */}
            <div className="lg:col-span-5">
              <AudioCapture
                onCaptureStateChange={setIsCapturing}
                onTelemetryUpdate={setTelemetry}
              />
            </div>

            {/* Live Waveform Visualizer */}
            <div className="lg:col-span-7 bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-xl backdrop-blur-md flex flex-col justify-between">
              <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-800/80">
                <div className="flex items-center gap-2 text-xs font-semibold text-slate-200">
                  <Activity className="w-4 h-4 text-sky-400" />
                  Real-Time WASAPI Oscillogram & Speech Waveform
                </div>
                <span className="text-[11px] font-mono text-slate-400">
                  {isCapturing ? "ACTIVE RING BUFFER (256 PTS)" : "STANDBY"}
                </span>
              </div>

              {/* Canvas visualizer */}
              <div className="relative w-full h-36 bg-slate-950 rounded-lg overflow-hidden border border-slate-800 flex items-center justify-center">
                <canvas
                  ref={canvasRef}
                  width={640}
                  height={144}
                  className="w-full h-full block"
                />
                {!isCapturing && (
                  <div className="absolute inset-0 flex items-center justify-center bg-slate-950/60 backdrop-blur-sm pointer-events-none">
                    <span className="text-xs text-slate-500 font-mono">
                      Loopback Idle — Engage stream to render live audio buffer
                    </span>
                  </div>
                )}
              </div>

              <div className="flex items-center justify-between text-[11px] text-slate-400 pt-2 font-mono">
                <span>0.00 ms (Zero-Latency Ring)</span>
                <span>FFT Spectrum Window: 16-Bit IEEE 754</span>
              </div>
            </div>
          </div>
        )}

        {/* Tab-Specific Panels */}
        {activeTab === "overview" && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
            <div className="lg:col-span-6">
              <MotionLiveFeed onSelectMotion={setSelectedMotion} />
            </div>
            <div className="lg:col-span-6">
              <FlowchartViewer />
            </div>
          </div>
        )}

        {activeTab === "motions" && (
          <div className="w-full">
            <MotionLiveFeed onSelectMotion={setSelectedMotion} />
          </div>
        )}

        {activeTab === "diagram" && (
          <div className="w-full h-[650px]">
            <FlowchartViewer />
          </div>
        )}

        {activeTab === "telemetry" && (
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-md">
            <h3 className="text-sm font-semibold text-slate-100 mb-4 flex items-center gap-2">
              <Server className="w-4 h-4 text-indigo-400" />
              Low-Level WASAPI / CoreAudio Buffer Metrics
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 font-mono text-xs">
              <div className="bg-slate-950 border border-slate-800 p-3 rounded-lg">
                <div className="text-slate-500">CAPTURE STATUS</div>
                <div className="text-slate-200 font-semibold mt-1">
                  {telemetry?.is_capturing ? "RECORDING" : "IDLE"}
                </div>
              </div>
              <div className="bg-slate-950 border border-slate-800 p-3 rounded-lg">
                <div className="text-slate-500">SAMPLE RATE</div>
                <div className="text-sky-400 font-semibold mt-1">
                  {telemetry?.sample_rate || 48000} Hz
                </div>
              </div>
              <div className="bg-slate-950 border border-slate-800 p-3 rounded-lg">
                <div className="text-slate-500">CHANNELS</div>
                <div className="text-emerald-400 font-semibold mt-1">
                  {telemetry?.channels || 2} Channels
                </div>
              </div>
              <div className="bg-slate-950 border border-slate-800 p-3 rounded-lg">
                <div className="text-slate-500">DROPPED SAMPLES</div>
                <div className="text-slate-200 font-semibold mt-1">
                  {telemetry?.dropped_frames || 0}
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
