"""This proxy's fixed, allowlisted upstream and native request shape.

Inventoried from Earth Platform 0.1.0-alpha.73 (tag combined-73 / commit
88b13c33954550c6ac660dceb743a4288a9aafac),
geography/src/main/java/io/earthplatform/geography/globe/CopernicusSource.java
(`private URI uri(String name) { return base.resolve(name + "/" + name + ".tif"); }`):
the mod reads one cloud-optimised GeoTIFF per 1x1 degree square from the
public AWS Open Data bucket, named
Copernicus_DSM_COG_10_{N|S}{lat}_00_{E|W}{lon}_00_DEM/<same>.tif. Live checks
against the bucket below confirm Accept-Ranges: bytes, 206 Partial Content
with a correct Content-Range, 416 on an out-of-bounds range, 304 on a
matching If-None-Match, and a plain (non-multipart) ETag. Terms: Copernicus
Programme open-data policy (free, open access, attribution required -- the
mod already embeds CopernicusSource.ATTRIBUTION, preserved here); no caching
restriction found.
"""
import re

from range_cache_proxy import SourceConfig

_PATH_RE = re.compile(
    r"^/(Copernicus_DSM_COG_10_[NS]\d{2}_00_[EW]\d{3}_00_DEM)/\1\.tif$"
)


def _validate_path(path: str):
    return path.lstrip("/") if _PATH_RE.match(path) else None


SOURCE = SourceConfig(
    name="copernicus-dem",
    dataset_id="copernicus-glo30-v1",
    default_upstream="https://copernicus-dem-30m.s3.amazonaws.com/",
    upstream_env_var="COPERNICUS_DEM_CACHE_UPSTREAM",
    validate_path=_validate_path,
    probe_path="/Copernicus_DSM_COG_10_N00_00_E006_00_DEM/Copernicus_DSM_COG_10_N00_00_E006_00_DEM.tif",
)
