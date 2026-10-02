// CivixRecord Native Desktop Loopback & IPC Daemon
// Handles zero-latency WASAPI / CoreAudio stream capture and dispatches to CivixRecord Core

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod wasapi_loopback;

use wasapi_loopback::{
    create_loopback_state, get_audio_devices, get_loopback_telemetry, get_waveform_data,
    start_loopback_sink, stop_loopback_sink, AudioStreamStatus,
};

#[tauri::command]
fn get_stream_telemetry(
    state: tauri::State<'_, std::sync::Arc<wasapi_loopback::LoopbackState>>,
) -> AudioStreamStatus {
    match get_loopback_telemetry(state) {
        Ok(t) => AudioStreamStatus {
            is_capturing: t.is_capturing,
            sample_rate: t.sample_rate,
            channels: t.channels,
            dropped_frames: t.dropped_frames,
        },
        Err(_) => AudioStreamStatus {
            is_capturing: false,
            sample_rate: 48000,
            channels: 2,
            dropped_frames: 0,
        },
    }
}

fn main() {
    env_logger::init();
    log::info!("Starting CivixRecord Desktop Loopback Engine v0.4.1");

    let loopback_state = create_loopback_state();

    tauri::Builder::default()
        .manage(loopback_state)
        .invoke_handler(tauri::generate_handler![
            get_stream_telemetry,
            get_audio_devices,
            start_loopback_sink,
            stop_loopback_sink,
            get_loopback_telemetry,
            get_waveform_data
        ])
        .run(tauri::generate_context!())
        .expect("error while running civixrecord desktop application");
}
