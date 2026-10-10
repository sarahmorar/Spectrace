"""Tests for Spectrace frequency-domain spectrum processing."""

import numpy as np
import pytest

from spectrace.processing.spectrum import (
    SpectrumProcessingError,
    compute_spectrum,
    generate_frequency_axis,
)


def test_compute_spectrum_returns_shifted_fft():
    """Verify that spectrum computation returns a centered FFT. (Aka, did we calculate the correct FFT?)"""
    samples = np.array(
        [
            1.0 + 0.0j,
            0.0 + 1.0j,
            -1.0 + 0.0j,
            0.0 - 1.0j,
        ]
    )

    expected = np.fft.fftshift(np.fft.fft(samples))

    result = compute_spectrum(samples)

    np.testing.assert_allclose(result, expected)

def test_compute_spectrum_preserves_size_and_complex_values():
    """Verify that spectrum output preserves size and complex values. (Aka, does our function uphold the API contract?)"""
    samples = np.array(
        [
            1.0 + 2.0j,
            3.0 + 4.0j,
            5.0 + 6.0j,
            7.0 + 8.0j,
        ]
    )

    result = compute_spectrum(samples)

    assert isinstance(result, np.ndarray)
    assert result.size == samples.size
    assert np.iscomplexobj(result)

def test_compute_spectrum_does_not_modify_input():
    """Verify that spectrum computation does not modify the IQ samples. (Aka, are the original IQ samples not modified?)"""
    samples = np.array(
        [
            1.0 + 2.0j,
            3.0 + 4.0j,
            5.0 + 6.0j,
            7.0 + 8.0j,
        ]
    )
    original_samples = samples.copy()

    compute_spectrum(samples)

    np.testing.assert_array_equal(samples, original_samples)

def test_compute_spectrum_rejects_invalid_input():
    """Ensure invalid spectrum input raises a Spectrace-specific error. (AKA, does the function handle invalid input?)"""
    samples = [1.0 + 2.0j, 3.0 + 4.0j]

    with pytest.raises(SpectrumProcessingError):
        compute_spectrum(samples)

def test_compute_spectrum_places_tone_in_expected_bin():
    """Verify that a synthetic tone produces a peak in the expected FFT bin. (AKA, does the FFT produce the expected frequency-domain result?)"""
    sample_count = 8
    tone_bin = 1
    sample_indices = np.arange(sample_count)

    samples = np.exp(
        2j * np.pi * tone_bin * sample_indices / sample_count
    )

    result = compute_spectrum(samples)

    peak_index = np.argmax(np.abs(result))

    assert peak_index == sample_count // 2 + tone_bin

def test_compute_spectrum_rejects_real_samples():
    """Ensure real-valued samples cannot be processed as IQ data. (AKA, does the function reject non-complex input?)"""
    samples = np.array([1.0, 2.0, 3.0, 4.0])

    with pytest.raises(SpectrumProcessingError):
        compute_spectrum(samples)

def test_generate_frequency_axis_returns_expected_frequencies():
    """Verify that FFT bins map to the expected absolute RF frequencies. (AKA, does the frequency axis generation produce the correct frequencies?)"""
    sample_count = 8
    sample_rate = 2_000_000
    center_frequency = 2_437_000_000

    expected = np.array(
        [
            2_436_000_000,
            2_436_250_000,
            2_436_500_000,
            2_436_750_000,
            2_437_000_000,
            2_437_250_000,
            2_437_500_000,
            2_437_750_000,
        ]
    )

    result = generate_frequency_axis(
        sample_count,
        sample_rate,
        center_frequency,
    )

    np.testing.assert_allclose(result, expected)

def test_generate_frequency_axis_supports_odd_sample_count():
    """Verify that frequency-axis generation supports an odd number of FFT bins. (AKA, does the function handle odd-sized FFTs?)"""
    sample_count = 5
    sample_rate = 1_000_000
    center_frequency = 100_000_000

    expected = np.array(
        [
            99_600_000,
            99_800_000,
            100_000_000,
            100_200_000,
            100_400_000,
        ]
    )

    result = generate_frequency_axis(
        sample_count,
        sample_rate,
        center_frequency,
    )

    np.testing.assert_allclose(result, expected)

def test_generate_frequency_axis_rejects_invalid_sample_count():
    """Ensure frequency-axis generation rejects a non-positive sample count. (AKA, does the function handle invalid sample counts?)"""
    with pytest.raises(SpectrumProcessingError):
        generate_frequency_axis(
            sample_count=0,
            sample_rate=2_000_000,
            center_frequency=2_437_000_000,
        )

def test_generate_frequency_axis_rejects_invalid_sample_rate():
    """Ensure frequency-axis generation rejects a non-positive sample rate. (AKA, does the function handle invalid sample rates?)"""
    with pytest.raises(SpectrumProcessingError):
        generate_frequency_axis(
            sample_count=8,
            sample_rate=0,
            center_frequency=2_437_000_000,
        )

def test_generate_frequency_axis_rejects_invalid_center_frequency():
    """Ensure frequency-axis generation rejects a non-positive center frequency."""
    with pytest.raises(SpectrumProcessingError):
        generate_frequency_axis(
            sample_count=8,
            sample_rate=2_000_000,
            center_frequency=0,
        )

def test_generate_frequency_axis_matches_sample_count():
    """Ensure the frequency axis contains one value for each FFT bin."""
    sample_count = 16

    result = generate_frequency_axis(
        sample_count=sample_count,
        sample_rate=2_000_000,
        center_frequency=2_437_000_000,
    )

    assert result.size == sample_count