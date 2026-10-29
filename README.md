# QMotion Blinds for Home Assistant

A native Home Assistant integration for QMotion blinds through a local QSync hub. The QSync command and record layout follows observations documented in [devbobo/qmotion](https://github.com/devbobo/qmotion), which is MIT licensed.

## Features

- Each named QMotion blind group appears as its own Home Assistant device and cover, with open, close, and set position controls. Assign each device to a different HA area; its QMotion group name remains the device name.
- Supports QSync's nine positions: 0%, 12.5%, 25%, 37.5%, 50%, 62.5%, 75%, 87.5%, and 100%. Requested positions are rounded to the nearest supported step.
- Communicates locally over TCP port 9760 without cloud access or credentials.

**Position reporting is estimated.** The observed protocol does not provide live position feedback. Home Assistant restores the last known position and estimates travel over 30 seconds, so manual use, power loss, or a different blind travel time can make the displayed position inaccurate. QSync's observed protocol has no dedicated stop command; Stop reissues the current estimated position as a new target.

## Install with HACS

1. In HACS, open **Integrations** and choose the three-dot menu, then **Custom repositories**.
2. Add https://github.com/magray/ha-qmotion with category **Integration**.
3. Find **QMotion Blinds**, install it, restart Home Assistant, then add the integration from **Settings → Devices & services**. Enter your QSync hub IP address; TCP port defaults to 9760.
4. In **Settings → Devices & services**, open each QMotion group device and assign its area. The device retains the group name reported by QSync.

## Manual installation

Copy the custom_components/qmotion folder into your Home Assistant config/custom_components/qmotion folder, restart Home Assistant, and add **QMotion Blinds** from **Settings → Devices & services**.

The integration polls the hub's blind inventory every 60 seconds. It asks for the hub IP directly; UDP broadcast discovery on port 9720 is not required. This project is independent and is not affiliated with QMotion.
