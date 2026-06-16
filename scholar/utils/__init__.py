"""scholar.utils — shared utility belt."""
from .logger import get_logger
from .paths import (
    get_data_dir, get_config_dir, get_cache_dir,
    get_log_dir, get_output_dir, get_models_dir,
    get_db_path, get_plugins_dir,
)
from .helpers import (
    slugify, truncate, clean_text, file_hash,
    safe_filename, timestamped_name, human_size,
    chunk_text,
)

__all__ = [
    "get_logger",
    "get_data_dir", "get_config_dir", "get_cache_dir",
    "get_log_dir", "get_output_dir", "get_models_dir",
    "get_db_path", "get_plugins_dir",
    "slugify", "truncate", "clean_text", "file_hash",
    "safe_filename", "timestamped_name", "human_size",
    "chunk_text",
]
