"""Tests for captured IQ sample validation."""

import numpy as np
import pytest

from spectrace.capture.validation import (
    IQValidationError,
    validate_iq_samples,
)

def test_valid_iq_samples_pass_validation():
    """Verify that a valid complex NumPy IQ array passes validation."""
    samples = np.array(
        [
            1.0 + 2.0j,
            3.0 + 4.0j,
            5.0 + 6.0j,
        ]
    )

    validate_iq_samples(samples)

def test_empty_iq_samples_are_rejected():
    """Verify that an empty IQ capture fails validation."""
    samples = np.array([], dtype=np.complex128)

    with pytest.raises(
        IQValidationError,
        match="IQ sample array cannot be empty",
    ):
        validate_iq_samples(samples)

def test_non_numpy_iq_samples_are_rejected():
    """Verify that IQ samples must be provided as a NumPy array."""
    samples = [
        1.0 + 2.0j,
        3.0 + 4.0j,
    ]

    with pytest.raises(
        IQValidationError,
        match="IQ samples must be a NumPy array",
    ):
        validate_iq_samples(samples)

def test_non_complex_iq_samples_are_rejected():
    """Verify that IQ samples must contain complex-valued data."""
    samples = np.array(
        [
            1.0,
            2.0,
            3.0,
        ]
    )

    with pytest.raises(
        IQValidationError,
        match="IQ samples must be complex-valued",
    ):
        validate_iq_samples(samples)

def test_non_finite_iq_samples_are_rejected():
    """Verify that IQ samples cannot contain NaN or infinite values."""
    samples = np.array(
        [
            1.0 + 2.0j,
            np.nan + 3.0j,
            4.0 + np.inf * 1j,
        ]
    )

    with pytest.raises(
        IQValidationError,
        match="IQ samples must contain only finite values",
    ):
        validate_iq_samples(samples)