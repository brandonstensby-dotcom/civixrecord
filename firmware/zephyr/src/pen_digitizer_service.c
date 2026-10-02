#include "pen_digitizer_service.h"

#include <zephyr/logging/log.h>
#include <string.h>

LOG_MODULE_REGISTER(civix_pen, LOG_LEVEL_INF);

static struct bt_uuid_128 pen_svc_uuid = BT_UUID_INIT_128(BT_UUID_CIVIX_PEN_VAL);
static struct bt_uuid_128 pen_stroke_uuid = BT_UUID_INIT_128(BT_UUID_CIVIX_PEN_STROKE_VAL);
static struct bt_uuid_128 pen_config_uuid = BT_UUID_INIT_128(BT_UUID_CIVIX_PEN_CONFIG_VAL);
static struct bt_uuid_128 pen_telem_uuid = BT_UUID_INIT_128(BT_UUID_CIVIX_PEN_TELEMETRY_VAL);

static struct civix_pen_config current_pen_config = {
    .dpi = 1200,
    .sample_rate_hz = 200,
    .pressure_levels = 1,
    .active_mode = 1,
};

static struct civix_pen_telemetry current_pen_telemetry = {
    .ultrasonic_snr_db = 420,
    .tof_delta_ns = 12,
    .transducer_health = 100,
    .battery_pct = 95,
};

static ssize_t read_pen_cfg(struct bt_conn *conn, const struct bt_gatt_attr *attr,
                            void *buf, uint16_t len, uint16_t offset) {
    return bt_gatt_attr_read(conn, attr, buf, len, offset,
                             &current_pen_config, sizeof(current_pen_config));
}

static ssize_t write_pen_cfg(struct bt_conn *conn, const struct bt_gatt_attr *attr,
                             const void *buf, uint16_t len, uint16_t offset,
                             uint8_t flags) {
    if (offset + len > sizeof(current_pen_config)) {
        return BT_GATT_ERR(BT_ATT_ERR_INVALID_OFFSET);
    }
    memcpy((uint8_t *)&current_pen_config + offset, buf, len);
    LOG_INF("Pen Digitizer Config Updated: DPI=%u, SampleRate=%u Hz, Mode=%u",
            current_pen_config.dpi, current_pen_config.sample_rate_hz, current_pen_config.active_mode);
    return len;
}

static ssize_t read_pen_telemetry(struct bt_conn *conn, const struct bt_gatt_attr *attr,
                                  void *buf, uint16_t len, uint16_t offset) {
    return bt_gatt_attr_read(conn, attr, buf, len, offset,
                             &current_pen_telemetry, sizeof(current_pen_telemetry));
}

BT_GATT_SERVICE_DEFINE(civix_pen_svc,
    BT_GATT_PRIMARY_SERVICE(&pen_svc_uuid),
    BT_GATT_CHARACTERISTIC(&pen_stroke_uuid.uuid,
                           BT_GATT_CHRC_NOTIFY,
                           BT_GATT_PERM_NONE,
                           NULL, NULL, NULL),
    BT_GATT_CCC(NULL, BT_GATT_PERM_READ | BT_GATT_PERM_WRITE),
    BT_GATT_CHARACTERISTIC(&pen_config_uuid.uuid,
                           BT_GATT_CHRC_READ | BT_GATT_CHRC_WRITE | BT_GATT_CHRC_NOTIFY,
                           BT_GATT_PERM_READ | BT_GATT_PERM_WRITE,
                           read_pen_cfg, write_pen_cfg, &current_pen_config),
    BT_GATT_CCC(NULL, BT_GATT_PERM_READ | BT_GATT_PERM_WRITE),
    BT_GATT_CHARACTERISTIC(&pen_telem_uuid.uuid,
                           BT_GATT_CHRC_READ | BT_GATT_CHRC_NOTIFY,
                           BT_GATT_PERM_READ,
                           read_pen_telemetry, NULL, &current_pen_telemetry),
    BT_GATT_CCC(NULL, BT_GATT_PERM_READ | BT_GATT_PERM_WRITE),
);

int civix_pen_service_init(void) {
    LOG_INF("CivixRecord Ultrasonic Acoustic Pen Digitizer GATT Service Initialized (Opcode 0x62)");
    return 0;
}

int civix_pen_send_stroke(const struct civix_pen_stroke_sample *sample) {
    if (!sample) {
        return -EINVAL;
    }
    return bt_gatt_notify(NULL, &civix_pen_svc.attrs[1], sample, sizeof(*sample));
}

int civix_pen_update_config(uint32_t dpi, uint16_t sample_rate_hz, uint8_t pressure_levels, uint8_t active_mode) {
    current_pen_config.dpi = dpi;
    current_pen_config.sample_rate_hz = sample_rate_hz;
    current_pen_config.pressure_levels = pressure_levels;
    current_pen_config.active_mode = active_mode;
    return bt_gatt_notify(NULL, &civix_pen_svc.attrs[4], &current_pen_config, sizeof(current_pen_config));
}

int civix_pen_send_telemetry(const struct civix_pen_telemetry *telemetry) {
    if (!telemetry) {
        return -EINVAL;
    }
    memcpy(&current_pen_telemetry, telemetry, sizeof(current_pen_telemetry));
    return bt_gatt_notify(NULL, &civix_pen_svc.attrs[7], &current_pen_telemetry, sizeof(current_pen_telemetry));
}

int civix_pen_get_config(struct civix_pen_config *cfg) {
    if (!cfg) {
        return -EINVAL;
    }
    memcpy(cfg, &current_pen_config, sizeof(*cfg));
    return 0;
}
