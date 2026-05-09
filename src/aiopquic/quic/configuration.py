"""QUIC configuration — matches qh3.quic.configuration API."""

from dataclasses import dataclass, field


@dataclass
class QuicConfiguration:
    """Configuration for a QUIC connection.

    Defaults tuned for streaming-media workloads (MoQT, WT). Override
    individual fields where a different policy is needed.
    """
    alpn_protocols: list[str] | None = None
    idle_timeout: float = 60.0
    is_client: bool = True
    # Initial flow-control windows advertised to the peer at handshake.
    # The peer is bound by spec to never send more than max_stream_data
    # bytes unconsumed on a single stream (and max_data across all
    # streams) until we extend MAX_STREAM_DATA. The C-side per-stream
    # RX byte ring is sized to match this advertised cap at allocation
    # time, so the spec-permitted worst case (peer fills the entire
    # window before we drain a byte) is handled correctly. As the
    # consumer drains bytes the picoquic worker thread extends the
    # cap via picoquic_open_flow_control. Higher caps tolerate larger
    # peer bursts before backpressure kicks in; lower caps reduce
    # per-stream memory and bufferbloat.
    max_data: int = 16 * 1024 * 1024
    max_stream_data: int = 16 * 1024 * 1024
    # 65535: the QUIC max for the DATAGRAM frame extension (RFC 9221).
    # Enables datagrams by default (h3zero only advertises h3_datagram
    # + webtransport_max_sessions when this is non-zero).
    max_datagram_frame_size: int | None = 65535
    server_name: str | None = None
    certificate_file: str | None = None
    private_key_file: str | None = None
    verify_mode: int | None = None
    # NSS Key Log Format file (Wireshark-compatible). When set, picoquic
    # writes TLS secrets per connection so packet captures can be
    # decrypted offline. Honors the SSLKEYLOGFILE env var as a default.
    secrets_log_file: str | None = None
    # Congestion-control algorithm for picoquic to use on this transport.
    # None defers to picoquic's compile-time default (newreno). Common
    # values: "newreno" (loss-based, default), "cubic" (loss-based,
    # widely deployed), "bbr" (delay-based, high-BDP friendly), "bbr1"
    # (older BBRv1), "prague" (L4S/ECN), "dcubic", "fast". The string
    # is passed verbatim to picoquic_set_default_congestion_algorithm_by_name;
    # an unknown name falls back to the compile-time default.
    congestion_control_algorithm: str | None = None
    # SPSC TX/RX event ring capacity (entries — must be a power of 2).
    # Each event is an ~64 B notification between the picoquic worker
    # thread and the asyncio drain. Sized for the worst-case burst of
    # stream_data / stream_fin notifications between asyncio drain
    # cycles. None defers to the compile-time default (262144 — about
    # 16 MiB per ring). Bump higher for sustained multi-Gbps workloads
    # with high stream-churn rates (e.g. one stream per video frame
    # group); lower to reduce memory footprint when stream rate is
    # low. Below ~16384 entries, multi-Gbps stream-churn workloads
    # exhibit silent stream-data event drops on the receiver — the
    # bytes are buffered on the per-stream ring, but the asyncio loop
    # is never notified about them, so short streams whose only
    # notifications fall in the overflow window are silently lost.
    event_ring_capacity: int | None = None

    def load_cert_chain(self, certfile: str, keyfile: str | None = None,
                        password: str | None = None) -> None:
        """Load certificate and private key files."""
        self.certificate_file = certfile
        if keyfile is not None:
            self.private_key_file = keyfile

    def load_verify_locations(self, cafile: str | None = None,
                              capath: str | None = None,
                              cadata: bytes | None = None) -> None:
        """Load CA certificates for peer verification."""
        pass  # picoquic uses system CA store by default
