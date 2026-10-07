# Kia EV (Ituran) for Home Assistant

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/docs/faq/custom_repositories)
[![Validate](https://github.com/tomerezra/ha-kia-ituran/actions/workflows/validate.yml/badge.svg)](https://github.com/tomerezra/ha-kia-ituran/actions/workflows/validate.yml)

Unofficial Home Assistant integration that reads electric vehicle data (battery level, range, charging info) for **Kia EVs in Israel** that use the **MY KIA** app, which is backed by **Ituran** telematics.

> **Disclaimer:** This project is not affiliated with, endorsed by, or supported by Kia or Ituran. It uses an undocumented API that the MY KIA app uses. That API may change or stop working at any time. Use at your own risk.

## Features

- Battery level (%)
- Driving range (km)
- Charging AC mode
- Time remaining for charge
- Any other value the API reports is added automatically as a sensor (named after its label, with the raw code as an attribute)

Data is polled from the cloud every 5 minutes.

## Requirements

- A Kia EV registered in the MY KIA app (Israel)
- Home Assistant 2024.8 or newer
- The three values the app sends to Ituran: `UserName`, `Password` and `PlatformId` (see below)

## Installation

### HACS (recommended)

1. In HACS, open the menu (⋮) → **Custom repositories**.
2. Add `https://github.com/tomerezra/ha-kia-ituran` with type **Integration**.
3. Search for **Kia EV (Ituran)** and download it.
4. Restart Home Assistant.

### Manual

Copy `custom_components/kia_ituran` into your `config/custom_components` folder and restart Home Assistant.

## Getting your credentials

The integration needs the exact values the MY KIA app sends in its `GetElectricData` request. Right now, the only way to get them is to capture the app's traffic on your own phone. These steps use [Proxyman](https://proxyman.io/) on iOS. Any HTTPS debugging proxy works the same way.

1. Install Proxyman on your iPhone and follow its setup to install and trust its certificate.
2. Enable SSL proxying for the domain `app.ituran.com`.
3. Start capturing, open the **MY KIA** app and open the screen that shows the battery and range.
4. In Proxyman, find the POST request to:
   `https://app.ituran.com/ituranmobileservice/mobileservice.asmx/GetElectricData`
5. Open the request body (form data) and copy the three values: `UserName`, `Password` and `PlatformId`.
6. Stop capturing. You can remove the Proxyman certificate afterwards.

> **Keep these values private.** They give access to your vehicle data. Don't post them in issues or on forums.

## Configuration

1. Go to **Settings → Devices & services → Add integration**.
2. Search for **Kia EV (Ituran)**.
3. Enter `UserName`, `Password` and `PlatformId`.

The integration checks the values with the API before saving them.

## Troubleshooting

- **"Ituran rejected the credentials":** the API returned an error. Make sure you copied all three values exactly. If they worked before and stopped, capture them again.
- **"Cannot connect to Ituran":** network problem or the API is down. Try again later.
- To get debug logs, add this to `configuration.yaml`:

  ```yaml
  logger:
    logs:
      custom_components.kia_ituran: debug
  ```

## Contributing

Issues and pull requests are welcome. If your car reports values that show up with a generic name, please open an issue with the label and code (not your credentials) so they can be mapped properly.

## License

[MIT](LICENSE)
