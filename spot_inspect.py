"""Read-only format triage for a .spot sample; no license extraction or decryption."""
import argparse
import collections
import hashlib
import json
import math
import shutil
import subprocess
from pathlib import Path

def inspect_file(path):
    path = Path(path)
    size = path.stat().st_size
    with path.open("rb") as handle:
        header = handle.read(64)
        handle.seek(max(0, size // 2 - 32768))
        sample = handle.read(65536)
    counts = collections.Counter(sample)
    entropy = -sum((n / len(sample)) * math.log2(n / len(sample)) for n in counts.values()) if sample else 0
    identifier = header[13:25]
    result = {
        "file": path.name,
        "size_bytes": size,
        "first_byte_hex": header[:1].hex(),
        "header_contains_filename_id_at_offset_13": identifier.hex() == path.stem.lower(),
        "header_id_hex": identifier.hex(),
        "entropy_sample_bits_per_byte": round(entropy, 4),
        "standard_media_recognized": False,
        "media_probe": "ffprobe not installed",
        "sha256": None,
        "conclusion": "Structure inspection only; encryption and playback are not determined by this test."
    }
    if shutil.which("ffprobe"):
        command = ["ffprobe", "-v", "error", "-show_entries", "format=format_name", "-of", "default=noprint_wrappers=1", str(path)]
        try:
            response = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=20)
            result["standard_media_recognized"] = response.returncode == 0 and bool(response.stdout.strip())
            result["media_probe"] = (response.stdout.strip() or response.stderr.strip())[:500]
        except (subprocess.TimeoutExpired, OSError) as error:
            result["media_probe"] = str(error)
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspect .spot headers without modifying content")
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    print(json.dumps(inspect_file(args.file), ensure_ascii=False, indent=2))
