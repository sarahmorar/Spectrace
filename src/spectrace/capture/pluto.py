"""ADALM-Pluto SDR connection management for Spectrace."""


from dataclasses import dataclass

import adi


class PlutoConnectionError(RuntimeError):
    """Raised when Spectrace cannot establish a connection to a PlutoSDR."""


class PlutoConfigurationError(RuntimeError):
    """Raised when Spectrace cannot apply configuration to a PlutoSDR."""


class PlutoCaptureError(RuntimeError):
    """Raised when Spectrace cannot capture IQ samples from a PlutoSDR."""  


@dataclass
class PlutoRXConfig:
    """Configuration parameters for the PlutoSDR receive path."""

    center_frequency: int
    sample_rate: int
    rf_bandwidth: int
    gain_mode: str = "slow_attack"
    gain: float | None = None
    buffer_size: int = 4096


class PlutoSDR:
    """Manage a connection to an ADALM-Pluto compatible SDR."""

    def __init__(self, uri: str | None = None) -> None:
        """Initialize a PlutoSDR connection configuration.

        Args:
            uri: Optional libiio URI used to connect to the SDR.
        """
        self.uri = uri
        self.device = None

    def connect(self) -> None:
        """Connect to the configured PlutoSDR.

        Raises:
            PlutoConnectionError: If the SDR connection cannot be established.
        """
        try:
            if self.uri is None:
                self.device = adi.Pluto()
            else:
                self.device = adi.Pluto(uri=self.uri)
        except Exception as exc:
            raise PlutoConnectionError(
                f"Could not connect to PlutoSDR using URI: {self.uri or 'auto'}"
            ) from exc
        
    def configure_rx(self, config: PlutoRXConfig) -> None:
        """Apply receive configuration parameters to the PlutoSDR.

        Args:
            config: Receive parameters to apply to the SDR.

        Raises:
            PlutoConnectionError: If the SDR is not connected.
            PlutoConfigurationError: If the RX configuration cannot be applied.
        """
        if self.device is None:
            raise PlutoConnectionError(
                "Cannot configure PlutoSDR before establishing a connection."
            )

        if config.gain_mode == "manual" and config.gain is None:
            raise PlutoConfigurationError(
                "Manual RX gain mode requires a gain value."
            )

        try:
            self.device.rx_lo = config.center_frequency
            self.device.sample_rate = config.sample_rate
            self.device.rx_rf_bandwidth = config.rf_bandwidth
            self.device.gain_control_mode_chan0 = config.gain_mode
            self.device.rx_buffer_size = config.buffer_size

            if config.gain_mode == "manual":
                self.device.rx_hardwaregain_chan0 = config.gain
        except Exception as exc:
            raise PlutoConfigurationError(
                "Could not apply receive configuration to PlutoSDR."
            ) from exc

    def capture(self):
        """Capture one buffer of IQ samples from the PlutoSDR.

        Returns:
            IQ samples captured from the SDR.

        Raises:
            PlutoConnectionError: If the SDR is not connected.
            PlutoCaptureError: If IQ samples cannot be captured.
        """
        if self.device is None:
            raise PlutoConnectionError(
                "Cannot capture IQ samples before establishing a connection."
            )

        try:
            return self.device.rx()
        except Exception as exc:
            raise PlutoCaptureError(
                "Could not capture IQ samples from PlutoSDR."
            ) from exc