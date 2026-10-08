"""Validation utilities for captured RF IQ sample data."""

import numpy as np


class IQValidationError(ValueError):
    """Raised when captured IQ sample data fails validation."""

def validate_iq_samples(samples) -> None:
    """Validate captured IQ sample data.

    Args:
        samples: Captured IQ samples to validate.

    Raises:
        IQValidationError: If the captured samples are invalid.
    """
    if not isinstance(samples, np.ndarray):
        raise IQValidationError("IQ samples must be a NumPy array.")

    if samples.size == 0:
        raise IQValidationError("IQ sample array cannot be empty.")

    if not np.iscomplexobj(samples):
        raise IQValidationError("IQ samples must be complex-valued.")

    if not np.all(np.isfinite(samples)):
        raise IQValidationError(
            "IQ samples must contain only finite values."
        )