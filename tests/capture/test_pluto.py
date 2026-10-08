"""Tests for PlutoSDR connection management."""

from unittest.mock import patch

import pytest

from spectrace.capture.pluto import PlutoConnectionError, PlutoSDR


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