/*
 * CivixRecord Edge Firmware - Nordic nRF5340 / nRF52840 Entrypoint
 * Autonomous civic meeting acoustic capture & multi-sensor hardware mesh
 */

#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/gap.h>

#include "ble_audio_service.h"
#include "optical_glasses_service.h"
#include "pen_digitizer_service.h"

LOG_MODULE_REGISTER(civix_edge, LOG_LEVEL_INF);

static const struct bt_data ad[] = {
    BT_DATA_BYTES(BT_DATA_FLAGS, (BT_LE_AD_GENERAL | BT_LE_AD_NO_BREDR)),
    BT_DATA(BT_DATA_NAME_COMPLETE, "CivixRecord-Sensor", 18),
};

static void bt_ready(int err) {
    if (err) {
        LOG_ERR("Bluetooth initialization failed (err %d)", err);
        return;
    }

    LOG_INF("Bluetooth initialized successfully");

    err = civix_ble_audio_service_init();
    if (err) {
        LOG_ERR("Failed to register Civix Audio GATT service (err %d)", err);
        return;
    }

    err = civix_glasses_service_init();
    if (err) {
        LOG_ERR("Failed to register Civix Optical Glasses GATT service (err %d)", err);
        return;
    }

    err = civix_pen_service_init();
    if (err) {
        LOG_ERR("Failed to register Civix Pen Digitizer GATT service (err %d)", err);
        return;
    }

    err = bt_le_adv_start(BT_LE_ADV_CONN_NAME, ad, ARRAY_SIZE(ad), NULL, 0);
    if (err) {
        LOG_ERR("Advertising failed to start (err %d)", err);
        return;
    }

    LOG_INF("BLE Advertising started. Multi-sensor mesh listening for CivixRecord Core connection.");
}

int main(void) {
    LOG_INF("CivixRecord Edge Hardware Firmware v0.4.1 booting...");

    int err = bt_enable(bt_ready);
    if (err) {
        LOG_ERR("bt_enable failed (err %d)", err);
        return 0;
    }

    while (1) {
        k_sleep(K_SECONDS(1));
    }

    return 0;
}
