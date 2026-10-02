import React, { useState, useEffect, useRef } from "react";
import { Mic, Volume2, Activity, Play, Square, RefreshCw, AlertCircle, Cpu } from "lucide-react";

export interface AudioDeviceInfo {
  id: string;
  name: string;
  is_default: boolean;
  is_loopback_capable: boolean;
  default_sample_rate: number;
  default_channels: number;
}

export interface LoopbackTelemetry {
  is_capturing: boolean;
  device_name: string;
  peak_linear: number;
  peak_db: number;
  rms_linear: number;
  rms_db: number;
  sample_rate: number;
  channels: number;
  total_samples: number;
  dropped_frames: number;
  buffer_capacity: number;
}

interface AudioCaptureProps {
  onCaptureStateChange?: (isCapturing: boolean) => void;
  onTelemetryUpdate?: (telemetry: LoopbackTelemetry) => void;
}

// Resilient Tauri invoke helper with fallback for web preview
async function invokeTauri<T>(cmd: string, args?: Record<string, unknown>): Promise<T> {
  if (typeof window !== "undefined" && (window as unknown as { __TAURI_INTERNALS__?: unknown }).__TAURI_INTERNALS__) {
    try {
      const { invoke } = await import("@tauri-apps/api/core");
      return await invoke<T>(cmd, args);
    } catch (err) {
      console.warn(`Tauri invoke "${cmd}" failed, fallback to mock:`, err);
    }
  }

  // Mock implementation for development and testing
  if (cmd === "get_audio_devices") {
    return [
      {
        id: "out:default",
        name: "Speakers (Realtek High Definition Audio) - Loopback Target",
        is_default: true,
        is_loopback_capable: true,
        default_sample_rate: 48000,
        default_channels: 2,
      },
      {
        id: "out:virtual_cable",
        name: "VB-Audio Virtual Cable (WASAPI Loopback)",
        is_default: false,
        is_loopback_capable: true,
        default_sample_rate: 48000,
        default_channels: 2,
      },
      {
        id: "in:default",
        name: "Microphone Array (Intel Smart Sound Technology)",
        is_default: false,
        is_loopback_capable: false,
        default_sample_rate: 44100,
        default_channels: 1,
      },
    ] as T;
  }

  if (cmd === "start_loopback_sink") {
    return "WASAPI_LOOPBACK_STARTED" as T;
  }

  if (cmd === "stop_loopback_sink") {
    return "LOOPBACK_STOPPED" as T;
  }

  if (cmd === "get_loopback_telemetry") {
    const isCapturing = (window as unknown as { _mockCapturing?: boolean })._mockCapturing ?? false;
    const peak = isCapturing ? 0.2 + Math.random() * 0.55 : 0.001;
    const peakDb = isCapturing ? -20 + Math.random() * 15 : -96.0;
    return {
      is_capturing: isCapturing,
      device_name: "Realtek Audio WASAPI Loopback",
      peak_linear: peak,
      peak_db: peakDb,
      rms_linear: peak * 0.7,
      rms_db: peakDb - 3.5,
      sample_rate: 48000,
      channels: 2,
      total_samples: isCapturing ? 245000 : 0,
      dropped_frames: 0,
      buffer_capacity: 16384,
    } as T;
  }

  throw new Error(`Unhandled command: ${cmd}`);
}

export const AudioCapture: React.FC<AudioCaptureProps> = ({
  onCaptureStateChange,
  onTelemetryUpdate,
}) => {
  const [devices, setDevices] = useState<AudioDeviceInfo[]>([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState<string>("");
  const [isCapturing, setIsCapturing] = useState<boolean>(false);
  const [telemetry, setTelemetry] = useState<LoopbackTelemetry>({
    is_capturing: false,
    device_name: "Initializing...",
    peak_linear: 0,
    peak_db: -96.0,
    rms_linear: 0,
    rms_db: -96.0,
    sample_rate: 48000,
    channels: 2,
    total_samples: 0,
    dropped_frames: 0,
    buffer_capacity: 16384,
  });
  const [statusMessage, setStatusMessage] = useState<string>("Ready");
  const [loading, setLoading] = useState<boolean>(false);

  const pollIntervalRef = useRef<number | null>(null);

  // Load available devices
  const fetchDevices = async () => {
    try {
      const devList = await invokeTauri<AudioDeviceInfo[]>("get_audio_devices");
      setDevices(devList);
      if (devList.length > 0 && !selectedDeviceId) {
        const def = devList.find((d) => d.is_default) || devList[0];
        setSelectedDeviceId(def.id);
      }
    } catch (e) {
      setStatusMessage(`Error fetching devices: ${e}`);
    }
  };

  useEffect(() => {
    fetchDevices();
  }, []);

  // Poll loopback telemetry
  useEffect(() => {
    if (isCapturing) {
      pollIntervalRef.current = window.setInterval(async () => {
        try {
          const tel = await invokeTauri<LoopbackTelemetry>("get_loopback_telemetry");
          setTelemetry(tel);
          if (onTelemetryUpdate) {
            onTelemetryUpdate(tel);
          }
        } catch (e) {
          console.error("Telemetry poll failed", e);
        }
      }, 60);
    } else {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
      setTelemetry((prev) => ({
        ...prev,
        is_capturing: false,
        peak_linear: 0,
        peak_db: -96.0,
        rms_linear: 0,
        rms_db: -96.0,
      }));
    }

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, [isCapturing, onTelemetryUpdate]);

  // Handle capture toggle
  const toggleCapture = async () => {
    setLoading(true);
    try {
      if (!isCapturing) {
        (window as unknown as { _mockCapturing?: boolean })._mockCapturing = true;
        const res = await invokeTauri<string>("start_loopback_sink", {
          deviceId: selectedDeviceId || null,
        });
        setIsCapturing(true);
        setStatusMessage(res);
        if (onCaptureStateChange) onCaptureStateChange(true);
      } else {
        (window as unknown as { _mockCapturing?: boolean })._mockCapturing = false;
        const res = await invokeTauri<string>("stop_loopback_sink");
        setIsCapturing(false);
        setStatusMessage(res);
        if (onCaptureStateChange) onCaptureStateChange(false);
      }
    } catch (err) {
      setStatusMessage(`Capture fault: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  // Peak meter percentage (clamped between 0 and 100)
  const peakPercent = Math.min(100, Math.max(0, telemetry.peak_linear * 100));
  const rmsPercent = Math.min(100, Math.max(0, telemetry.rms_linear * 100));

  // Determine meter color based on dB level
  const getMeterColor = (db: number) => {
    if (db > -3) return "bg-red-500 shadow-red-500/50";
    if (db > -12) return "bg-amber-400 shadow-amber-400/50";
    return "bg-emerald-400 shadow-emerald-400/50";
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-xl backdrop-blur-md">
      <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className={`p-2.5 rounded-lg ${isCapturing ? "bg-emerald-500/20 text-emerald-400" : "bg-slate-800 text-slate-400"}`}>
            <Volume2 className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
              WASAPI / CoreAudio Virtual Loopback
              {isCapturing && (
                <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  LIVE CAPTURE
                </span>
              )}
            </h2>
            <p className="text-xs text-slate-400">
              Zero-latency native system audio mirror and civic speech buffer
            </p>
          </div>
        </div>

        <button
          onClick={fetchDevices}
          className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-md transition"
          title="Refresh Audio Devices"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-5 items-center">
        {/* Device Selector */}
        <div className="md:col-span-6 space-y-1.5">
          <label className="text-xs font-medium text-slate-300 flex items-center gap-1.5">
            <Mic className="w-3.5 h-3.5 text-indigo-400" />
            Audio Source / Render Endpoint
          </label>
          <select
            value={selectedDeviceId}
            disabled={isCapturing || loading}
            onChange={(e) => setSelectedDeviceId(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {devices.map((device) => (
              <option key={device.id} value={device.id}>
                {device.name} {device.is_default ? "★ Default" : ""}
              </option>
            ))}
          </select>
        </div>

        {/* Loopback Toggle Button */}
        <div className="md:col-span-6 flex items-center justify-end gap-3 pt-4 md:pt-0">
          <button
            onClick={toggleCapture}
            disabled={loading}
            className={`w-full md:w-auto px-5 py-2.5 rounded-lg font-medium text-sm flex items-center justify-center gap-2 transition shadow-lg ${
              isCapturing
                ? "bg-rose-600 hover:bg-rose-500 text-white shadow-rose-900/30"
                : "bg-indigo-600 hover:bg-indigo-500 text-white shadow-indigo-900/30"
            }`}
          >
            {isCapturing ? (
              <>
                <Square className="w-4 h-4 fill-current" />
                Halt Loopback
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                Engage Loopback Stream
              </>
            )}
          </button>
        </div>
      </div>

      {/* Real-time Peak & RMS Audio Meters */}
      <div className="mt-5 pt-4 border-t border-slate-800/80 space-y-3">
        <div className="flex items-center justify-between text-xs font-mono">
          <div className="flex items-center gap-2 text-slate-400">
            <Activity className="w-3.5 h-3.5 text-emerald-400" />
            <span>Peak Level:</span>
            <span className={`font-semibold ${telemetry.peak_db > -3 ? "text-rose-400" : "text-emerald-400"}`}>
              {isCapturing ? `${telemetry.peak_db.toFixed(1)} dBFS` : "-- dBFS"}
            </span>
          </div>
          <div className="flex items-center gap-2 text-slate-400">
            <span>RMS:</span>
            <span className="text-sky-300">
              {isCapturing ? `${telemetry.rms_db.toFixed(1)} dBFS` : "-- dBFS"}
            </span>
          </div>
        </div>

        {/* Visual Peak Bar Meter */}
        <div className="relative w-full h-3 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
          {/* Gradient backdrop ticks */}
          <div className="absolute inset-0 flex justify-between px-1 opacity-20 pointer-events-none text-[8px] text-slate-500 items-center">
            <span>-96dB</span>
            <span>-24dB</span>
            <span>-12dB</span>
            <span>-6dB</span>
            <span>0dB</span>
          </div>
          {/* RMS bar */}
          <div
            className="absolute top-0 bottom-0 left-0 bg-indigo-500/40 transition-all duration-75"
            style={{ width: `${rmsPercent}%` }}
          />
          {/* Peak bar */}
          <div
            className={`absolute top-0 bottom-0 left-0 transition-all duration-75 ${getMeterColor(telemetry.peak_db)}`}
            style={{ width: `${peakPercent}%` }}
          />
        </div>

        {/* Telemetry metadata footer */}
        <div className="flex flex-wrap items-center justify-between text-[11px] text-slate-400 pt-1">
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1">
              <Cpu className="w-3 h-3 text-slate-500" />
              {telemetry.sample_rate} Hz ({telemetry.channels} Ch)
            </span>
            <span>Ring Capacity: {telemetry.buffer_capacity} f32</span>
          </div>
          <div className="flex items-center gap-2">
            <span>Dropped Frames:</span>
            <span className={telemetry.dropped_frames > 0 ? "text-amber-400 font-semibold" : "text-emerald-400"}>
              {telemetry.dropped_frames}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
