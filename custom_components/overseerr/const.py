"""Constants for the Overseerr integration."""

DOMAIN = "overseerr"
CONF_URL = "url"
CONF_API_KEY = "api_key"

DEFAULT_PORT = 5055

MEDIA_TYPE_MOVIE = "movie"
MEDIA_TYPE_TV = "tv"

STATUS_UNKNOWN = 1
STATUS_PENDING = 2
STATUS_PROCESSING = 3
STATUS_PARTIALLY_AVAILABLE = 4
STATUS_AVAILABLE = 5

STATUS_LABELS = {
    STATUS_UNKNOWN: "Unknown",
    STATUS_PENDING: "Pending",
    STATUS_PROCESSING: "Processing",
    STATUS_PARTIALLY_AVAILABLE: "Partially Available",
    STATUS_AVAILABLE: "Available",
}
