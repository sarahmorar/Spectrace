"""Tests for PlutoSDR connection management."""

import numpy as np
import pytest

from unittest.mock import patch

import pytest

from spectrace.capture.pluto import (
    PlutoCaptureError,
    PlutoConfigurationError,
    PlutoConnectionError,
    PlutoRXConfig,
    PlutoSDR,
)


def test_connect_with_uri():
    """Verify that PlutoSDR connects using the configured URI."""
    uri = "ip:test-device"

    with patch("spectrace.capture.pluto.adi.Pluto") as mock_pluto:
        sdr = PlutoSDR(uri=uri)
        sdr.connect()

        mock_pluto.assert_called_once_with(uri=uri)
        assert sdr.device is mock_pluto.return_value


def test_connect_without_uri():
    """Verify that PlutoSDR can use pyadi-iio automatic discovery."""
    with patch("spectrace.capture.pluto.adi.Pluto") as mock_pluto:
        sdr = PlutoSDR()
        sdr.connect()

        mock_pluto.assert_called_once_with()
        assert sdr.device is mock_pluto.return_value


def test_connection_failure():
    """Verify that connection failures raise a Spectrace-specific error."""
    with patch(
        "spectrace.capture.pluto.adi.Pluto",
        side_effect=Exception("Connection failed"),
    ):
        sdr = PlutoSDR(uri="ip:test-device")

        with pytest.raises(PlutoConnectionError):
            sdr.connect()


def test_rx_config_defaults():
    """Verify that RX configuration uses the expected default values."""
    config = PlutoRXConfig(
        center_frequency=2_437_000_000,
        sample_rate=2_000_000,
        rf_bandwidth=1_500_000,
    )

    assert config.center_frequency == 2_437_000_000
    assert config.sample_rate == 2_000_000
    assert config.rf_bandwidth == 1_500_000
    assert config.gain_mode == "slow_attack"
    assert config.gain is None
    assert config.buffer_size == 4096


def test_configure_rx():
    """Verify that receive configuration is applied to the PlutoSDR."""
    config = PlutoRXConfig(
        center_frequency=2_437_000_000,
        sample_rate=2_000_000,
        rf_bandwidth=1_500_000,
        buffer_size=8192,
    )

    with patch("spectrace.capture.pluto.adi.Pluto") as mock_pluto:
        sdr = PlutoSDR(uri="ip:test-device")
        sdr.connect()
        sdr.configure_rx(config)

        device = mock_pluto.return_value

        assert device.rx_lo == config.center_frequency
        assert device.sample_rate == config.sample_rate
        assert device.rx_rf_bandwidth == config.rf_bandwidth
        assert device.gain_control_mode_chan0 == config.gain_mode
        assert device.rx_buffer_size == config.buffer_size


def test_configure_rx_with_manual_gain():
    """Verify that manual RX gain is applied when manual gain mode is used."""
    config = PlutoRXConfig(
        center_frequency=2_437_000_000,
        sample_rate=2_000_000,
        rf_bandwidth=1_500_000,
        gain_mode="manual",
        gain=30.0,
    )

    with patch("spectrace.capture.pluto.adi.Pluto") as mock_pluto:
        sdr = PlutoSDR(uri="ip:test-device")
        sdr.connect()
        sdr.configure_rx(config)

        device = mock_pluto.return_value

        assert device.gain_control_mode_chan0 == "manual"
        assert device.rx_hardwaregain_chan0 == 30.0


def test_configure_rx_requires_connection():
    """Verify that RX configuration requires an established connection."""
    config = PlutoRXConfig(
        center_frequency=2_437_000_000,
        sample_rate=2_000_000,
        rf_bandwidth=1_500_000,
    )
    sdr = PlutoSDR()

    with pytest.raises(
        PlutoConnectionError,
        match="Cannot configure PlutoSDR before establishing a connection",
    ):
        sdr.configure_rx(config)

def test_configure_rx_failure():
    """Verify that hardware configuration failures raise a Spectrace-specific error."""
    config = PlutoRXConfig(
        center_frequency=2_437_000_000,
        sample_rate=2_000_000,
        rf_bandwidth=1_500_000,
    )

    with patch("spectrace.capture.pluto.adi.Pluto") as mock_pluto:
        device = mock_pluto.return_value

        # Simulate pyadi-iio rejecting a hardware setting.
        type(device).rx_lo = property(
            fset=lambda self, value: (_ for _ in ()).throw(
                ValueError("Invalid frequency")
            )
        )

        sdr = PlutoSDR(uri="ip:test-device")
        sdr.connect()

        with pytest.raises(
            PlutoConfigurationError,
            match="Could not apply receive configuration",
        ):
            sdr.configure_rx(config)

def test_manual_gain_requires_value():
    """Verify that manual gain mode requires an explicit gain value."""
    config = PlutoRXConfig(
        center_frequency=2_437_000_000,
        sample_rate=2_000_000,
        rf_bandwidth=1_500_000,
        gain_mode="manual",
    )

    with patch("spectrace.capture.pluto.adi.Pluto"):
        sdr = PlutoSDR(uri="ip:test-device")
        sdr.connect()

        with pytest.raises(
            PlutoConfigurationError,
            match="Manual RX gain mode requires a gain value",
        ):
            sdr.configure_rx(config)

def test_capture_returns_iq_samples():
    """Verify that capture returns IQ samples provided by the PlutoSDR."""
    expected_samples = np.array(
    [
        1.0 + 2.0j,
        3.0 + 4.0j,
        5.0 + 6.0j,
    ]
)

    with patch("spectrace.capture.pluto.adi.Pluto") as mock_pluto:
        device = mock_pluto.return_value
        device.rx.return_value = expected_samples

        sdr = PlutoSDR(uri="ip:test-device")
        sdr.connect()

        samples = sdr.capture()

        device.rx.assert_called_once_with()
        assert isinstance(samples, np.ndarray)
        np.testing.assert_array_equal(samples, expected_samples)

def test_capture_failure():
    """Verify that SDR capture failures raise a Spectrace-specific error."""
    with patch("spectrace.capture.pluto.adi.Pluto") as mock_pluto:
        device = mock_pluto.return_value
        device.rx.side_effect = RuntimeError("SDR receive failed")

        sdr = PlutoSDR(uri="ip:test-device")
        sdr.connect()

        with pytest.raises(
            PlutoCaptureError,
            match="Could not capture IQ samples",
        ):
            sdr.capture()

def test_capture_requires_connection():
    """Verify that IQ capture requires an established SDR connection."""
    sdr = PlutoSDR(uri="ip:test-device")

    with pytest.raises(
        PlutoConnectionError,
        match="Cannot capture IQ samples before establishing a connection",
    ):
        sdr.capture()