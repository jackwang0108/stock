"""
cache_engin.py 为TuShare API提供了缓存加载与读取功能

    @Time    : 2025/04/23
    @Author  : JackWang
    @File    : cached_api.py
    @IDE     : VsCode
    @Copyright Copyright Shihong Wang (c) 2025 with GNU Public License V3.0
"""

# Standard Library
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

# Third-Party Library
import pandas as pd

# Torch Library

# My Library
from ..utils.config import APIProfile


def _hash_param(api_name: str, params: dict[str, Any]) -> str:
    params_str = json.dumps(params, sort_keys=True)
    return hashlib.md5(f"{api_name}_{params_str}".encode()).hexdigest()


class TushareCacheEngine:
    def __init__(
        self,
        api_profile: APIProfile,
        cache_root: str | Path = Path(__file__).parents[2] / "cache",
    ):
        self.api_profile = api_profile
        self.cache_root = Path(cache_root)
        if not self.cache_root.exists():
            self.cache_root.mkdir(parents=True, exist_ok=True)
        self.cache_root = self.cache_root.resolve()

        self.hit: int = 0
        self.missed: int = 0
        self.expired: int = 0

    def statics(self) -> dict[str, int]:
        """返回缓存命中率"""
        total = self.hit + self.missed + self.expired
        if total == 0:
            return {"hit": 0, "missed": 0, "expired": 0}
        return {
            "hit_rate": round(self.hit / total * 100, 2),
            "miss_rate": round(self.missed / total * 100, 2),
            "expired_rate": round(self.expired / total * 100, 2),
        }

    def _get_cache_path(self, api_name: str, params: dict[str, Any]) -> Path:
        cache_dir: Path = self.cache_root / api_name
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir / f"{_hash_param(api_name, params)}.csv"

    def save_to_cache(
        self, api_name: str, params: dict[str, Any], data: pd.DataFrame
    ) -> pd.DataFrame:
        cache_path = self._get_cache_path(api_name, params)
        data.to_csv(cache_path, index=False, encoding="utf-8")

    def load_from_cache(
        self,
        api_name: str,
        params: dict[str, Any],
    ) -> pd.DataFrame | None:
        cache_path = self._get_cache_path(api_name, params)
        if not cache_path.exists():
            self.missed += 1
            return None

        last_modified_time = datetime.fromtimestamp(cache_path.stat().st_mtime)

        if datetime.now() - last_modified_time > timedelta(
            days=self.api_profile.get_config(api_name).expire_days
        ):
            self.expired += 1
            return None

        self.hit += 1

        try:
            return pd.read_csv(cache_path, encoding="utf-8", dtype=str)
        except pd.errors.EmptyDataError:
            print(f"缓存文件{cache_path}损坏, 修复该文件")
            cache_path.unlink()
            self.missed += 1
            return None


if __name__ == "__main__":
    cache_engine = TushareCacheEngine()
    print(cache_engine.cache_root)
