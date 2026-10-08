"""ADALM-Pluto SDR connection management for Spectrace."""

import adi


class PlutoConnectionError(RuntimeError):
    """Raised when Spectrace cannot establish a connection to a PlutoSDR."""


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