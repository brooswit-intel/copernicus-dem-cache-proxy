# copernicus-dem-cache-proxy

One of four independently configurable/deployable byte-range caching proxies
for MINECRAFT-577 (Build S3 range-cache proxies for regional elevation
refiners, shared delivery Story MINECRAFT-571). This repo covers Copernicus
DEM GLO-30 only; USGS 3DEP, Canada HRDEM and Antarctica REMA are each their
own separate repo/service, sharing only the `range_cache_proxy.py` cache
core (vendored, not a runtime dependency between them).

Pinned source: Earth Platform `combined-73` (= release 0.1.0-alpha.73,
commit `88b13c33954550c6ac660dceb743a4288a9aafac`),
`geography/src/main/java/io/earthplatform/geography/globe/CopernicusSource.java`.

## Upstream contract

- Fixed, allowlisted upstream: `https://copernicus-dem-30m.s3.amazonaws.com/`
  (the exact default from `CopernicusSource.AWS_COPERNICUS`; override via
  `COPERNICUS_DEM_CACHE_UPSTREAM`, default untouched when unset).
- Path: `{cell}/{cell}.tif` where `cell` is
  `Copernicus_DSM_COG_10_{N|S}{lat}_00_{E|W}{lon}_00_DEM`, one
  cloud-optimised GeoTIFF per 1x1 degree square (`CopernicusSource.uri()`).
- The mod (`RangeFiles`) only reads a COG's header and the blocks a caller
  touches via `Range`, never a whole-file GET. This proxy caches at that
  same granularity.
- Verified live against the real bucket (anonymous, read-only,
  no-sign-request): `Accept-Ranges: bytes`, 206 with a correct
  `Content-Range`, 416 on an out-of-bounds range, 304 on a matching
  `If-None-Match`, and a plain (non-multipart) ETag.
- Attribution: "produced using Copernicus WorldDEM-30 (c) DLR e.V.
  2010-2014 and (c) Airbus Defence and Space GmbH 2014-2018 provided under
  COPERNICUS by the European Union and ESA; all rights reserved"
  (`CopernicusSource.ATTRIBUTION`, preserved unchanged). Terms: Copernicus
  Programme open-data policy, free/open access, attribution required; no
  caching restriction found -- the same conclusion MINECRAFT-573 reached
  for the Copernicus-sourced JRC surface water layer.

## Contract this proxy keeps

- Loopback-only bind (`127.0.0.1`).
- Request path validated against the exact `{cell}/{cell}.tif` shape -- no
  arbitrary URL forwarding.
- SQLite cache keyed by `(path, byte-range)`, restart-persistent, bounded
  with LRU eviction.
- Concurrent misses for the same exact range single-flight to one upstream
  request.
- A transient upstream failure (5xx, connection error) is retried 3x with
  backoff and never cached; a truncated transfer is never cached; an
  upstream that answers 200 instead of 206 to a range request is never
  trusted or sliced as if it had honored the range.
- Genuine upstream 404/403/416 are passed through verbatim and never
  cached as success.
- Dedicated `/__health` probe: TTL 0, a fresh `Range: bytes=0-0` read of a
  real always-present object on every call, never served from the ordinary
  data cache -- so proxy-process liveness is distinguished from upstream
  reachability, and a fixture upstream outage is reflected without a direct
  bypass.
- `/__stats` reports cold/warm/upstream request and byte counters.

## Run

```
python3 -m unittest test_proxy -v   # 17 tests, local mock upstream only
python3 proxy.py                     # serves on 127.0.0.1:8104 by default
```

## Status

No live-provider traffic beyond the read-only verification probes recorded
on MINECRAFT-577; no merge/release/Zippy action. Tested against a local mock
upstream only. Mod-side wiring is tracked on MINECRAFT-580, the coordinated
alpha.73 integration lane -- not duplicated here.
