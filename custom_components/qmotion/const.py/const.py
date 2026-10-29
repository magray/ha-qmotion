"""Constants for the QMotion integration."""

DOMAIN = "qmotion"
CONF_HOST = "host"
CONF_PORT = "port"
DEFAULT_PORT = 9760
SUPPORTED_POSITIONS = (0, 12.5, 25, 37.5, 50, 62.5, 75, 87.5, 100)
POSITION_CODES = {
    0: "02", 12.5: "0e", 25: "0c", 37.5: "0b", 50: "08",
    62.5: "09", 75: "07", 87.5: "06", 100: "01",
}
