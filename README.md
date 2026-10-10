# Spectrace

**Open-source RF monitoring, fingerprinting, and rogue device detection.**

Spectrace is an open-source cybersecurity project designed to identify unauthorized
wireless devices through RF signal analysis and device fingerprinting.

The project is currently in early development. The SDR acquisition layer is
functional, providing a foundation for signal processing, transmission detection,
RF fingerprinting, and device classification.

**Project Status:** Active development
**Current Milestone:** M2 — Signal Processing complete.
**Next Milestone:** M3 — Transmission Detection

---

## Current Capabilities

Spectrace currently supports:

- Connecting to ADALM-Pluto-compatible SDR hardware
- Configuring SDR receive parameters
  - Center frequency
  - Sample rate
  - RF bandwidth
  - Gain mode
  - Manual gain
  - RX buffer size
- Capturing complex IQ samples
- Validating captured IQ data
- Applying Hann windowing to IQ samples
- Computing centered FFT spectra
- Generating absolute RF frequency axes
- Computing normalized relative power spectra
- Returning aligned frequency and power data through a processing pipeline
- Processing real RF captures from Pluto-compativle SDR hardware

Automated tests use synthetic RF signals where possible so that most of the project can be tested without physical SDR hardware.

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

The current implementation covers the **IQ Capture**, **IQ Validation**, and **Signal Processing** stages.

---

## Signal Processing Pipeline

Captured IQ samples can currently be transformed into aligned RF frequency and relative power data:

```text
Complex IQ Samples
        ↓
   IQ Validation
        ↓
   Hann Window
        ↓
       FFT
        ↓
    FFT Shift
        │
    ┌───┴───┐
    ▼       ▼
Frequency  Relative
  Axis      Power
    │       │
    └───┬───┘
        ▼
 SpectrumResult
```

The frequency axis maps FFT bins to absolute RF frequencies using the configured SDR sample rate and center frequency.

Power values are currently **relative decibel measurements** and should not be interpreted as calibrated dBm measurements.

---

## Installation

### Requirements

- Python 3.12+
- Git
- An ADALM-Pluto-compatible SDR for hardware capture

Most automated signal-processing tests do **not** require SDR hardware.

### Clone the repository
Clone the repository and create a virtual environment:

```bash
python -m venv .venv
```

### Install Spectrace
Activate the environment and install Spectrace in editable mode with development dependencies:

```bash
pip install -e ".[dev]"
```

---

## Basic Usage

### Connect to an SDR

```python
from spectrace.capture.pluto import PlutoRXConfig, PlutoSDR
from spectrace.capture.validation import validate_iq_samples

sdr = PlutoSDR("YOUR_LIBIIO_URI")
sdr.connect()
```

Device URIs should be supplied locally and should not be committed to the repository.

### Configure the receiver

```python
config = PlutoRXConfig(
    center_frequency=2_437_000_000,
    sample_rate=2_000_000,
    rf_bandwidth=1_500_000,
    buffer_size=4096,
)

sdr.configure_rx(config)
```

### Capture and validate IQ samples

```python
from spectrace.capture.validation import validate_iq_samples

samples = sdr.capture()
validate_iq_samples(samples)
```

### Process the spectrum

```python
from spectrace.processing.spectrum import process_spectrum

result = process_spectrum(
    samples,
    sample_rate=config.sample_rate,
    center_frequency=config.center_frequency,
)

print(result.frequencies)
print(result.power_db)
```

Each element of `result.frequencies` corresponds to the power value at the same index in `result.power_db`.

---

## Testing

Run the complete test suite with:

```bash
pytest -v
```

Spectrace uses automated testing throughout development, including synthetic IQ signals with known frequency characteristics.

This allows DSP behavior such as FFT processing, frequency mapping, windowing, and power calculation to be verified without requiring contributors to own SDR hardware.

Hardware integration tests are also performed during development using ADALM-Pluto-compatible SDR hardware.

---

## Development Roadmap

### M0 — Project Foundation

- [x] Repository structure
- [x] Python package configuration
- [x] Development environment
- [x] Testing framework
- [x] Privacy boundaries

### M1 — SDR Capture

- [x] Connect to Pluto-compatible SDR
- [x] Configure receive parameters
- [x] Capture complex IQ samples
- [x] Validate captured IQ data
- [x] Verify capture using physical SDR hardware

### M2 — Signal Processing

- [x] Compute frequency spectrum from IQ samples
- [x] Generate RF frequency axis
- [x] Compute normalized power spectrum
- [x] Apply Hann windowing
- [x] Add end-to-end spectrum processing pipeline
- [x] Verify processing using synthetic RF signals
- [x] Verify processing using real SDR captures

### M3 — Transmission Detection

- [ ] Estimate RF noise floor
- [ ] Detect signal energy above the noise floor
- [ ] Identify candidate transmissions
- [ ] Represent detected transmissions as structured events
- [ ] Test detection using synthetic signals
- [ ] Verify detection against real RF captures

### M4 — Data Collection & Enrollment

- [ ] Capture labeled device transmissions
- [ ] Extract training examples
- [ ] Build local device enrollment workflow
- [ ] Store sensitive RF data locally

### M5 — RF Fingerprinting

- [ ] Build RF fingerprint feature pipeline
- [ ] Train initial machine-learning models
- [ ] Evaluate device discrimination
- [ ] Compare model performance across RF conditions

### M6 — Device Classification

- [ ] Classify detected transmissions
- [ ] Associate fingerprints with enrolled devices
- [ ] Measure classification confidence
- [ ] Handle unknown devices

### M7 — Rogue Device Detection

- [ ] Maintain authorized device registry
- [ ] Detect unknown or unauthorized RF devices
- [ ] Generate detection events
- [ ] Implement confidence and alert thresholds

### M8 — Monitoring & CLI

- [ ] Continuous monitoring workflow
- [ ] Command-line interface
- [ ] Device enrollment commands
- [ ] Detection output
- [ ] Local configuration management

### M9 — Testing & Hardening

- [ ] Expand unit and integration testing
- [ ] Evaluate performance across SNR conditions
- [ ] Test cross-environment robustness
- [ ] Improve error handling
- [ ] Review privacy and security boundaries

### M10 — v0.1 Release

- [ ] Documentation
- [ ] Example configuration
- [ ] Reproducible installation
- [ ] Initial public release

---

## Privacy & Security

RF data can reveal information about nearby devices and environments. Spectrace is designed around a strict separation between **public source code** and **private RF data**.

The public repository should contain:

- Source code
- Tests
- Documentation
- Example configuration
- Synthetic test data
- Model architecture and training code

The following should remain local and must not be committed:

- Raw IQ/RF captures
- Device fingerprints
- Device enrollment records
- Personally identifying device labels
- Trained personal models
- Local configuration
- SDR/device identifiers
- Logs containing sensitive RF metadata

Spectrace's `.gitignore` is configured to exclude common RF capture, model, database, log, and local configuration formats.

Contributors should use synthetic data whenever possible when creating reproducible tests or examples.

---

## Development Philosophy

Spectrace is developed incrementally using:

1. Clearly defined milestones and GitHub issues
2. Feature branches
3. Test-driven development where practical
4. Automated regression testing
5. Hardware integration testing where appropriate
6. Code review before merging
7. Privacy review before publishing RF-related data

DSP components are intentionally kept modular so they can be tested independently of SDR hardware.

---

## Contributing

Spectrace is under active development. 

Contributions, bug reports, testing, and technical discussion are welcome as the project develops.

When contributing RF-related test cases, prefer synthetic data over real captures unless the data has been explicitly reviewed for safe public release.

## License

Spectrace is licensed under the GNU General Public License v3.0 or later. 

See `LICENSE` for details.
