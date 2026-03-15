# Overseerr for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/YOUR_GITHUB_USERNAME/overseerr-hacs.svg)](https://github.com/YOUR_GITHUB_USERNAME/overseerr-hacs/releases)

A Home Assistant integration for [Overseerr](https://overseerr.dev/) — the media request and management tool for Plex ecosystems.

> **Also install the dashboard card:** [overseerr-card-hacs](https://github.com/YOUR_GITHUB_USERNAME/overseerr-card-hacs)

---

## Features

- **Config Flow** — set up entirely through the Home Assistant GUI
- **Sensor entities** for pending and total request counts
- **Services** to request media or search programmatically from automations
- **Event bus** integration — fires `overseerr_search_results` events for use in automations

---

## Installation via HACS

1. Open HACS in Home Assistant
2. Go to **Integrations**
3. Click the three-dot menu → **Custom repositories**
4. Add: `https://github.com/YOUR_GITHUB_USERNAME/overseerr-hacs` — Category: **Integration**
5. Click **Download** on the Overseerr card that appears
6. Restart Home Assistant

## Setup

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **Overseerr**
3. Enter your Overseerr URL (e.g. `http://192.168.1.100:5055`) and API Key

> Your API Key is in Overseerr under **Settings → General**

---

## Sensor Entities

| Entity | Description |
|---|---|
| `sensor.overseerr_pending_requests` | Number of requests awaiting approval |
| `sensor.overseerr_total_requests` | Total number of all-time requests |

---

## Services

### `overseerr.request_media`

Request a movie or TV show by its TMDB ID.

```yaml
service: overseerr.request_media
data:
  media_type: movie   # or "tv"
  media_id: 550
```

### `overseerr.search`

Search and fire results as a Home Assistant event (`overseerr_search_results`).

```yaml
service: overseerr.search
data:
  query: "The Bear"
```

---

## Automation Example

Notify when new requests are pending approval:

```yaml
automation:
  - alias: "Overseerr — Pending Request Notification"
    trigger:
      - platform: state
        entity_id: sensor.overseerr_pending_requests
    condition:
      - condition: numeric_state
        entity_id: sensor.overseerr_pending_requests
        above: 0
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "Overseerr"
          message: "{{ states('sensor.overseerr_pending_requests') }} media request(s) need approval"
```

---

## Dashboard Card

Install the companion Lovelace card from the separate HACS repository:
**[overseerr-card-hacs](https://github.com/berserk88/overseerr-card-hacs**

The card provides a full graphical interface for searching and requesting media directly from your Home Assistant dashboard.

---

## Requirements

- Home Assistant 2023.1.0 or newer
- A running [Overseerr](https://overseerr.dev/) instance accessible from your network
