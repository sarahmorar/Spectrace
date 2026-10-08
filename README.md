# Spectrace

**Open-source RF monitoring, fingerprinting, and rogue device detection.**

Spectrace is an open-source cybersecurity project designed to identify unauthorized
wireless devices through RF signal analysis and device fingerprinting.

The project is currently in early development. The SDR acquisition layer is
functional, providing a foundation for signal processing, transmission detection,
RF fingerprinting, and device classification.

> **Project Status:** M1 — SDR Capture complete.  
> Next: M2 — Signal Processing.

## Current Capabilities

Spectrace currently supports:

- Connecting to ADALM-Pluto-compatible SDR hardware
- Configuring SDR receive parameters
  - Center frequency
  - Sample rate
  - RF bandwidth
  - Gain control
  - RX buffer size
- Capturing complex IQ samples
- Validating captured IQ data
- Detecting malformed, empty, non-complex, or non-finite IQ buffers
- Hardware-independent automated testing

The current implementation has been tested with PlutoSDR-compatible hardware.

## Architecture

Spectrace is being developed as a modular RF security pipeline:

```text
SDR
 ↓
IQ Capture
 ↓
IQ Validation
 ↓
Signal Processing
 ↓
Transmission Detection
 ↓
RF Fingerprinting
 ↓
Device Classification
 ↓
Authorized / Unknown Device
 ↓
Alerting
```

Only the acquisition and validation portions of this pipeline are currently implemented.

## Installation

Spectrace currently requires Python 3.12 or later.

Clone the repository and create a virtual environment:

```bash
python -m venv .venv
```

Activate the environment and install Spectrace in editable mode with development dependencies:

```bash
pip install -e ".[dev]"
```

Spectrace currently uses `pyadi-iio` and `libiio` to communicate with ADALM-Pluto-compatible SDR hardware.

## Basic Usage

```python
from spectrace.capture.pluto import PlutoRXConfig, PlutoSDR
from spectrace.capture.validation import validate_iq_samples

sdr = PlutoSDR("YOUR_LIBIIO_URI")
sdr.connect()

config = PlutoRXConfig(
    center_frequency=2_437_000_000,
    sample_rate=2_000_000,
    rf_bandwidth=1_500_000,
    buffer_size=4096,
)

sdr.configure_rx(config)

samples = sdr.capture()
validate_iq_samples(samples)
```

Spectrace does not automatically save captured IQ data to disk.

## Development Roadmap

- [x] **M0 — Project Foundation**
- [x] **M1 — SDR Capture**
- [ ] **M2 — Signal Processing**
- [ ] **M3 — Transmission Detection**
- [ ] **M4 — Data Collection & Enrollment**
- [ ] **M5 — RF Fingerprinting**
- [ ] **M6 — Device Classification**
- [ ] **M7 — Rogue Device Detection**
- [ ] **M8 — Monitoring & CLI**
- [ ] **M9 — Testing & Hardening**
- [ ] **M10 — v0.1 Release**

## Privacy

RF captures can contain information about nearby wireless activity. Spectrace is designed so that captured IQ data is not automatically persisted.

Raw captures, device fingerprints, local device registries, trained personal models, logs, and other environment-specific data should remain local and should not be committed to the repository.

## Contributing

Spectrace is under active development. Contributions, bug reports, testing, and technical discussion are welcome as the project develops.

## License

Spectrace is licensed under the GNU General Public License v3.0 or later. See `LICENSE` for details.