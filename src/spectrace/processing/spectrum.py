"""Frequency-domain signal processing utilities for Spectrace."""

from dataclasses import dataclass

import numpy as np


from spectrace.capture.validation import IQValidationError, validate_iq_samples


class SpectrumProcessingError(RuntimeError):
    """Raised when Spectrace cannot compute frequency-domain spectrum data."""


@dataclass
class SpectrumResult:
    """Processed frequency and power data for an IQ capture."""

    frequencies: np.ndarray
    power_db: np.ndarray


def compute_spectrum(samples: np.ndarray) -> np.ndarray:
    """Compute a centered frequency-domain spectrum from IQ samples.

    Args:
        samples: Complex IQ samples to transform.

    Returns:
        Complex frequency-domain spectrum with zero frequency centered.

    Raises:
        SpectrumProcessingError: If the IQ samples cannot be processed.
    """
    try:
        validate_iq_samples(samples)
    except IQValidationError as exc:
        raise SpectrumProcessingError(
            "Cannot compute spectrum from invalid IQ samples."
        ) from exc

    spectrum = np.fft.fft(samples)

    return np.fft.fftshift(spectrum)

def generate_frequency_axis(
    sample_count: int,
    sample_rate: float,
    center_frequency: float,
) -> np.ndarray:
    """Generate absolute RF frequencies for shifted FFT bins.

    Args:
        sample_count: Number of frequency bins in the spectrum.
        sample_rate: SDR sample rate in Hz.
        center_frequency: SDR center frequency in Hz.

    Returns:
        Absolute RF frequency for each shifted FFT bin.

    Raises:
        SpectrumProcessingError: If frequency-axis parameters are invalid.
    """
    # Reject invalid FFT sizes before attempting frequency calculations.
    if sample_count <= 0:
        raise SpectrumProcessingError(
            "Sample count must be greater than zero."
        )

    if sample_rate <= 0:
        raise SpectrumProcessingError(
            "Sample rate must be greater than zero."
        )

    if center_frequency <= 0:
        raise SpectrumProcessingError(
            "Center frequency must be greater than zero."
        )

    frequency_offsets = np.fft.fftshift(
        np.fft.fftfreq(sample_count, d=1 / sample_rate)
    )

    return frequency_offsets + center_frequency

def compute_power_spectrum(
    spectrum: np.ndarray,
    decibels: bool = False,
) -> np.ndarray:
    """Compute normalized power from a complex frequency-domain spectrum.

    Args:
        spectrum: Complex frequency-domain spectrum.
        decibels: Whether to return power in decibels.

    Returns:
        Normalized power, optionally converted to decibels.
    """
    if not isinstance(spectrum, np.ndarray):
        raise SpectrumProcessingError(
            "Frequency spectrum must be a NumPy array."
        )

    if spectrum.size == 0:
        raise SpectrumProcessingError(
            "Frequency spectrum cannot be empty."
        )

    if not np.iscomplexobj(spectrum):
        raise SpectrumProcessingError(
            "Frequency spectrum must be complex-valued."
        )

    if not np.all(np.isfinite(spectrum)):
        raise SpectrumProcessingError(
            "Frequency spectrum must contain only finite values."
        )

    sample_count = spectrum.size
    magnitude = np.abs(spectrum)
    power = (magnitude / sample_count) ** 2

    if decibels:
        # Apply a numerical floor so zero-power bins do not produce -inf.
        power_floor = np.finfo(float).tiny
        return 10 * np.log10(np.maximum(power, power_floor))

    return power

def apply_window(
        samples: np.ndarray,
        window_type: str = "hann",
    ) -> np.ndarray:
    """Apply a Hann window to complex IQ samples.

    Args:
        samples: Complex IQ samples to window.

    Returns:
        Windowed complex IQ samples.
    """
    try:
        validate_iq_samples(samples)
    except IQValidationError as exc:
        raise SpectrumProcessingError(
            "Cannot apply window to invalid IQ samples."
        ) from exc
    
    if window_type != "hann":
        raise SpectrumProcessingError(
            f"Unsupported window type: {window_type}"
        )
    
    window = np.hanning(samples.size)

    return samples * window

def process_spectrum(
    samples: np.ndarray,
    sample_rate: float,
    center_frequency: float,
) -> SpectrumResult:
    """Process IQ samples into aligned frequency and power data.

    Args:
        samples: Complex IQ samples to process.
        sample_rate: SDR sample rate in Hz.
        center_frequency: SDR center frequency in Hz.

    Returns:
        Processed RF frequencies and relative power in decibels.
    """
    windowed_samples = apply_window(samples)

    spectrum = compute_spectrum(windowed_samples)

    frequencies = generate_frequency_axis(
        spectrum.size,
        sample_rate,
        center_frequency,
    )

    power_db = compute_power_spectrum(
        spectrum,
        decibels=True,
    )

    return SpectrumResult(
        frequencies=frequencies,
        power_db=power_db,
    )