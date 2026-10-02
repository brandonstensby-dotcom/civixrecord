#pragma once

#include <zephyr/types.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/conn.h>
#include <zephyr/bluetooth/uuid.h>
#include <zephyr/bluetooth/gatt.h>

#ifdef __cplusplus
extern "C" {
#endif

/* 128-bit Base UUID for CivixRecord Civic Audio GATT Service:
 * 9E110001-C141-4E65-B801-D48293817100
 */
#define BT_UUID_CIVIX_VAL \
    BT_UUID_128_ENCODE(0x9E110001, 0xC141, 0x4E65, 0xB801, 0xD48293817100)

#define BT_UUID_CIVIX_AUDIO_STREAM_VAL \
    BT_UUID_128_ENCODE(0x9E110002, 0xC141, 0x4E65, 0xB801, 0xD48293817100)

#define BT_UUID_CIVIX_TELEMETRY_VAL \
    BT_UUID_128_ENCODE(0x9E110003, 0xC141, 0x4E65, 0xB801, 0xD48293817100)

int civix_ble_audio_service_init(void);
int civix_ble_send_audio_packet(const uint8_t *data, uint16_t len);

#ifdef __cplusplus
}
#endif
