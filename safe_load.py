# main.py
from typing import Union, List
from pathlib import Path

# Your existing imports (adjust to match kmp4 package names)
from kmp4.scheduler import TrickleScheduler, FirstCall, TrickleComposer, FirstCallComposer, Overwrite, Chunked
from kmp4.line import Lambda, Line

try:
    import yaml  # requires PyYAML
except ImportError as e:
    raise ImportError("PyYAML is not installed. Run: python -m pip install PyYAML") from e

def get_lines_from_yaml(path: Union[str, Path]) -> List[Line]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"YAML config not found: {p}")
    with p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    seqs = data.get("sequences", [])
    if not isinstance(seqs, list):
        raise ValueError("Expected 'sequences' to be a list in YAML.")
    return [Line.from_config(d) for d in seqs]

def load_all_config_dirs(root: Union[str, Path]) -> List[Path]:
    r = Path(root)
    return [p for p in r.iterdir() if p.is_dir()]

def get_lines_from_config_dir(path: Union[str, Path]) -> List[Line]:
    return [Line.from_config_dir(f) for f in load_all_config_dirs(path)]
