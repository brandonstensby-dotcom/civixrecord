#pragma once

#include <zephyr/types.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/conn.h>
#include <zephyr/bluetooth/uuid.h>
#include <zephyr/bluetooth/gatt.h>

#ifdef __cplusplus
extern "C" {
#endif

/* 128-bit Base UUID for CivixRecord Optical Glasses Service (Opcode 0x61):
 * 9E110061-C141-4E65-B801-D48293817100
 */
#define BT_UUID_CIVIX_GLASSES_VAL \
    BT_UUID_128_ENCODE(0x9E110061, 0xC141, 0x4E65, 0xB801, 0xD48293817100)

/* Characteristic: Frame Rate & Shutter Timing Sync */
#define BT_UUID_CIVIX_GLASSES_SYNC_VAL \
    BT_UUID_128_ENCODE(0x9E110062, 0xC141, 0x4E65, 0xB801, 0xD48293817100)

/* Characteristic: Zero-Copy Frame Event Stream */
#define BT_UUID_CIVIX_GLASSES_EVENT_VAL \
    BT_UUID_128_ENCODE(0x9E110063, 0xC141, 0x4E65, 0xB801, 0xD48293817100)

/* Characteristic: Gaze Alignment & Optical Sensor Telemetry */
#define BT_UUID_CIVIX_GLASSES_TELEMETRY_VAL \
    BT_UUID_128_ENCODE(0x9E110064, 0xC141, 0x4E65, 0xB801, 0xD48293817100)

#pragma pack(push, 1)
struct civix_glasses_sync_cfg {
    uint32_t fps;           /* Target optical capture rate (fps) */
    uint32_t shutter_us;    /* Exposure shutter duration in microseconds */
    uint8_t flags;          /* Bit 0: Continuous sync, Bit 1: Strobe lock */
};

struct civix_glasses_frame_event {
    uint32_t frame_index;   /* Monotonic camera frame counter */
    uint32_t timestamp_us;  /* Sensor exposure timestamp */
    uint16_t exposure_us;   /* Actual integration period */
    uint8_t strobe_state;   /* IR illuminator / LED sync pulse status */
};

struct civix_glasses_telemetry {
    int16_t gaze_x;         /* Normalized eye tracking X (-1000..+1000) */
    int16_t gaze_y;         /* Normalized eye tracking Y (-1000..+1000) */
    int16_t imu_pitch;      /* IMU pitch angle in 0.1 deg */
    int16_t imu_yaw;        /* IMU yaw angle in 0.1 deg */
    uint8_t optical_lock;   /* 1 = Fixated, 0 = Saccade */
    uint8_t battery_pct;    /* Hardware battery percentage (0-100) */
};
#pragma pack(pop)

int civix_glasses_service_init(void);
int civix_glasses_update_sync_config(uint32_t fps, uint32_t shutter_us, uint8_t flags);
int civix_glasses_send_frame_sync(const struct civix_glasses_frame_event *event);
int civix_glasses_send_telemetry(const struct civix_glasses_telemetry *telemetry);
int civix_glasses_get_sync_config(struct civix_glasses_sync_cfg *cfg);

#ifdef __cplusplus
}
#endif
