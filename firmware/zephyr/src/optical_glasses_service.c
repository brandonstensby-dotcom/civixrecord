#include "optical_glasses_service.h"

#include <zephyr/logging/log.h>
#include <string.h>

LOG_MODULE_REGISTER(civix_glasses, LOG_LEVEL_INF);

static struct bt_uuid_128 glasses_svc_uuid = BT_UUID_INIT_128(BT_UUID_CIVIX_GLASSES_VAL);
static struct bt_uuid_128 glasses_sync_uuid = BT_UUID_INIT_128(BT_UUID_CIVIX_GLASSES_SYNC_VAL);
static struct bt_uuid_128 glasses_event_uuid = BT_UUID_INIT_128(BT_UUID_CIVIX_GLASSES_EVENT_VAL);
static struct bt_uuid_128 glasses_telem_uuid = BT_UUID_INIT_128(BT_UUID_CIVIX_GLASSES_TELEMETRY_VAL);

static struct civix_glasses_sync_cfg current_sync_cfg = {
    .fps = 30,
    .shutter_us = 1000,
    .flags = 0x01,
};

static struct civix_glasses_telemetry current_telemetry = {
    .gaze_x = 0,
    .gaze_y = 0,
    .imu_pitch = 0,
    .imu_yaw = 0,
    .optical_lock = 0,
    .battery_pct = 100,
};

static ssize_t read_sync_cfg(struct bt_conn *conn, const struct bt_gatt_attr *attr,
                             void *buf, uint16_t len, uint16_t offset) {
    return bt_gatt_attr_read(conn, attr, buf, len, offset,
                             &current_sync_cfg, sizeof(current_sync_cfg));
}

static ssize_t write_sync_cfg(struct bt_conn *conn, const struct bt_gatt_attr *attr,
                              const void *buf, uint16_t len, uint16_t offset,
                              uint8_t flags) {
    if (offset + len > sizeof(current_sync_cfg)) {
        return BT_GATT_ERR(BT_ATT_ERR_INVALID_OFFSET);
    }
    memcpy((uint8_t *)&current_sync_cfg + offset, buf, len);
    LOG_INF("Optical Glasses Sync Updated: FPS=%u, Shutter=%u us, Flags=0x%02X",
            current_sync_cfg.fps, current_sync_cfg.shutter_us, current_sync_cfg.flags);
    return len;
}

static ssize_t read_telemetry(struct bt_conn *conn, const struct bt_gatt_attr *attr,
                              void *buf, uint16_t len, uint16_t offset) {
    return bt_gatt_attr_read(conn, attr, buf, len, offset,
                             &current_telemetry, sizeof(current_telemetry));
}

BT_GATT_SERVICE_DEFINE(civix_glasses_svc,
    BT_GATT_PRIMARY_SERVICE(&glasses_svc_uuid),
    BT_GATT_CHARACTERISTIC(&glasses_sync_uuid.uuid,
                           BT_GATT_CHRC_READ | BT_GATT_CHRC_WRITE | BT_GATT_CHRC_NOTIFY,
                           BT_GATT_PERM_READ | BT_GATT_PERM_WRITE,
                           read_sync_cfg, write_sync_cfg, &current_sync_cfg),
    BT_GATT_CCC(NULL, BT_GATT_PERM_READ | BT_GATT_PERM_WRITE),
    BT_GATT_CHARACTERISTIC(&glasses_event_uuid.uuid,
                           BT_GATT_CHRC_NOTIFY,
                           BT_GATT_PERM_NONE,
                           NULL, NULL, NULL),
    BT_GATT_CCC(NULL, BT_GATT_PERM_READ | BT_GATT_PERM_WRITE),
    BT_GATT_CHARACTERISTIC(&glasses_telem_uuid.uuid,
                           BT_GATT_CHRC_READ | BT_GATT_CHRC_NOTIFY,
                           BT_GATT_PERM_READ,
                           read_telemetry, NULL, &current_telemetry),
    BT_GATT_CCC(NULL, BT_GATT_PERM_READ | BT_GATT_PERM_WRITE),
);

int civix_glasses_service_init(void) {
    LOG_INF("CivixRecord Optical Glasses Sync GATT Service Initialized (Opcode 0x61)");
    return 0;
}

int civix_glasses_update_sync_config(uint32_t fps, uint32_t shutter_us, uint8_t flags) {
    current_sync_cfg.fps = fps;
    current_sync_cfg.shutter_us = shutter_us;
    current_sync_cfg.flags = flags;
    return bt_gatt_notify(NULL, &civix_glasses_svc.attrs[1], &current_sync_cfg, sizeof(current_sync_cfg));
}

int civix_glasses_send_frame_sync(const struct civix_glasses_frame_event *event) {
    if (!event) {
        return -EINVAL;
    }
    return bt_gatt_notify(NULL, &civix_glasses_svc.attrs[4], event, sizeof(*event));
}

int civix_glasses_send_telemetry(const struct civix_glasses_telemetry *telemetry) {
    if (!telemetry) {
        return -EINVAL;
    }
    memcpy(&current_telemetry, telemetry, sizeof(current_telemetry));
    return bt_gatt_notify(NULL, &civix_glasses_svc.attrs[7], &current_telemetry, sizeof(current_telemetry));
}

int civix_glasses_get_sync_config(struct civix_glasses_sync_cfg *cfg) {
    if (!cfg) {
        return -EINVAL;
    }
    memcpy(cfg, &current_sync_cfg, sizeof(*cfg));
    return 0;
}
