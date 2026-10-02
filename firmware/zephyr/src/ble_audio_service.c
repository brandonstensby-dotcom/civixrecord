#include "ble_audio_service.h"
#include <zephyr/logging/log.h>

LOG_MODULE_REGISTER(civix_gatt, LOG_LEVEL_INF);

static struct bt_uuid_128 civix_uuid = BT_UUID_INIT_128(BT_UUID_CIVIX_VAL);
static struct bt_uuid_128 audio_stream_uuid = BT_UUID_INIT_128(BT_UUID_CIVIX_AUDIO_STREAM_VAL);
static struct bt_uuid_128 telemetry_uuid = BT_UUID_INIT_128(BT_UUID_CIVIX_TELEMETRY_VAL);

static uint8_t telemetry_buf[16] = {0};

static ssize_t read_telemetry(struct bt_conn *conn, const struct bt_gatt_attr *attr,
                              void *buf, uint16_t len, uint16_t offset) {
    return bt_gatt_attr_read(conn, attr, buf, len, offset, telemetry_buf, sizeof(telemetry_buf));
}

BT_GATT_SERVICE_DEFINE(civix_svc,
    BT_GATT_PRIMARY_SERVICE(&civix_uuid),
    BT_GATT_CHARACTERISTIC(&audio_stream_uuid.uuid,
                           BT_GATT_CHRC_NOTIFY,
                           BT_GATT_PERM_NONE,
                           NULL, NULL, NULL),
    BT_GATT_CCC(NULL, BT_GATT_PERM_READ | BT_GATT_PERM_WRITE),
    BT_GATT_CHARACTERISTIC(&telemetry_uuid.uuid,
                           BT_GATT_CHRC_READ | BT_GATT_CHRC_NOTIFY,
                           BT_GATT_PERM_READ,
                           read_telemetry, NULL, telemetry_buf),
);

int civix_ble_audio_service_init(void) {
    LOG_INF("CivixRecord Custom 128-bit GATT Service Registered");
    return 0;
}

int civix_ble_send_audio_packet(const uint8_t *data, uint16_t len) {
    return bt_gatt_notify(NULL, &civix_svc.attrs[1], data, len);
}
