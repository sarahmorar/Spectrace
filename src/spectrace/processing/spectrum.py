"""Frequency-domain signal processing utilities for Spectrace."""

import numpy as np


from spectrace.capture.validation import IQValidationError, validate_iq_samples


class SpectrumProcessingError(RuntimeError):
    """Raised when Spectrace cannot compute frequency-domain spectrum data."""


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