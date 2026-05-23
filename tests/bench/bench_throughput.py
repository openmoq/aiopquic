"""Stream throughput benchmark — bulk client→server send over loopback."""
import time

import pytest

from _helpers import (
    SPSC_EVT_STREAM_DATA, SPSC_EVT_STREAM_FIN,
)


@pytest.mark.bench
@pytest.mark.parametrize("size_kb", [64, 1024, 32 * 1024],
                         ids=["64KB", "1MB", "32MB"])
def test_bench_stream_throughput(benchmark, big_ring_pair, size_kb):
    """Client sends size_kb of data on a fresh stream + FIN; server fully receives.

    Reports seconds per round; throughput = size_kb*1024 / mean_seconds.
    """
    server, client, client_cnx, _ = big_ring_pair
    payload = b"x" * (size_kb * 1024)
    stream_id_box = [0]

    def round_trip():
        sid = stream_id_box[0]
        stream_id_box[0] += 4
        client.tx_send_stream(client_cnx, sid, payload, end_stream=True)
        received = 0
        deadline = time.monotonic() + 60.0
        while received < len(payload) and time.monotonic() < deadline:
            for ev in server.drain_rx():
                if ev[0] in (SPSC_EVT_STREAM_DATA, SPSC_EVT_STREAM_FIN) \
                        and ev[1] == sid and ev[2] is not None:
                    received += len(ev[2])
        assert received == len(payload), \
            f"got {received}/{len(payload)} bytes on sid={sid}"

    benchmark.pedantic(round_trip, rounds=3, iterations=1, warmup_rounds=1)
