# QMotion Blinds for Home Assistant

A native Home Assistant integration for controlling QMotion blinds through a local QSync hub. It follows the observed protocol described by [devbobo/qmotion](https://github.com/devbobo/qmotion), whose repository is MIT licensed.

## Features

- Adds each blind as a Home Assistant cover entity with open, close, and set position controls.
- Supports QSync's nine positions: 0%, 12.5%, 25%, 37.5%, 50%, 62.5%, 75%, 87.5%, and 100%. Requests are rounded to the nearest supported step.
- Connects directly over the local network; no cloud service or credentials are used.

**Position is estimated.** QSync does not report live position in the observed protocol. Home Assistant restores the last known position and estimates movement over 30 seconds. Manual control, power loss, automations, or a different travel time can make the displayed position inaccurate. Stop reissues the estimated current position as a new target because the observed protocol has no dedicated stop command.

## Installation

1. Copy `custom_components/qmotion` into `<config>/custom_components/qmotion`.
2. Restart Home Assistant.
3. Go to **Settings → Devices & services → Add integration**, search for **QMotion Blinds**, and enter your QSync hub IP address. TCP port defaults to `9760`.

The integration polls blind inventory every 60 seconds and requires TCP access to the hub on port 9760. It asks for the hub IP directly; the upstream client's UDP broadcast discovery on port 9720 is not required.

This independent integration is not affiliated with QMotion.
