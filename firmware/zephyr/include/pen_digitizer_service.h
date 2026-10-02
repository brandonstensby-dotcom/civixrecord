#pragma once

#include <zephyr/types.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/conn.h>
#include <zephyr/bluetooth/uuid.h>
#include <zephyr/bluetooth/gatt.h>

#ifdef __cplusplus
extern "C" {
#endif

/* 128-bit Base UUID for CivixRecord Ultrasonic Acoustic Pen Digitizer (Opcode 0x62):
 * 9E110070-C141-4E65-B801-D48293817100
 */
#define BT_UUID_CIVIX_PEN_VAL \
    BT_UUID_128_ENCODE(0x9E110070, 0xC141, 0x4E65, 0xB801, 0xD48293817100)

/* Characteristic: High-Rate Acoustic Stroke Coordinate Stream */
#define BT_UUID_CIVIX_PEN_STROKE_VAL \
    BT_UUID_128_ENCODE(0x9E110071, 0xC141, 0x4E65, 0xB801, 0xD48293817100)

/* Characteristic: Digitizer Resolution (DPI) & Sampling Configuration */
#define BT_UUID_CIVIX_PEN_CONFIG_VAL \
    BT_UUID_128_ENCODE(0x9E110072, 0xC141, 0x4E65, 0xB801, 0xD48293817100)

/* Characteristic: Ultrasonic Time-of-Flight & Transducer Telemetry */
#define BT_UUID_CIVIX_PEN_TELEMETRY_VAL \
    BT_UUID_128_ENCODE(0x9E110073, 0xC141, 0x4E65, 0xB801, 0xD48293817100)

#pragma pack(push, 1)
struct civix_pen_config {
    uint32_t dpi;              /* Digitizer resolution: 600, 1200, 2400 */
    uint16_t sample_rate_hz;   /* Acoustic pulse rate: 100-500 Hz */
    uint8_t  pressure_levels;  /* 0 = 2048, 1 = 4096, 2 = 8192 levels */
    uint8_t  active_mode;      /* 0 = Low-power standby, 1 = Continuous tracking */
};

struct civix_pen_stroke_sample {
    uint32_t timestamp_us;     /* Microsecond sampling timestamp */
    int32_t  pos_x;            /* X coordinate in micrometers */
    int32_t  pos_y;            /* Y coordinate in micrometers */
    uint16_t pressure;         /* Tip pressure reading (0-8191) */
    int16_t  tilt_x;           /* Acoustic tilt X in 0.1 deg */
    int16_t  tilt_y;           /* Acoustic tilt Y in 0.1 deg */
    uint8_t  button_flags;     /* Bit 0: Tip contact, Bit 1: Barrel button */
    uint8_t  proximity;        /* 0 = Surface contact, 1 = Proximity hover */
};

struct civix_pen_telemetry {
    uint16_t ultrasonic_snr_db;  /* Acoustic SNR in 0.1 dB */
    uint16_t tof_delta_ns;       /* Differential time of flight in ns */
    uint8_t  transducer_health;  /* Piezo transducer health check (0-100) */
    uint8_t  battery_pct;        /* Stylus battery state of charge (0-100) */
};
#pragma pack(pop)

int civix_pen_service_init(void);
int civix_pen_send_stroke(const struct civix_pen_stroke_sample *sample);
int civix_pen_update_config(uint32_t dpi, uint16_t sample_rate_hz, uint8_t pressure_levels, uint8_t active_mode);
int civix_pen_send_telemetry(const struct civix_pen_telemetry *telemetry);
int civix_pen_get_config(struct civix_pen_config *cfg);

#ifdef __cplusplus
}
#endif
