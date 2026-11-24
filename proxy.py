"""Entrypoint: loopback-only byte-range cache proxy for Copernicus DEM GLO-30.

Run: python3 proxy.py
Env overrides: COPERNICUS_DEM_CACHE_UPSTREAM, COPERNICUS_DEM_CACHE_PORT, COPERNICUS_DEM_CACHE_DB
"""
import os

from range_cache_proxy import run_server
from source import SOURCE

if __name__ == "__main__":
    port = int(os.environ.get("COPERNICUS_DEM_CACHE_PORT", "8104"))
    db = os.environ.get("COPERNICUS_DEM_CACHE_DB", "copernicus-dem-cache.sqlite3")
    server, proxy = run_server(SOURCE, db, port)
    print(f"copernicus-dem cache proxy on http://127.0.0.1:{port} -> upstream {proxy.upstream_base}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        proxy.close()
