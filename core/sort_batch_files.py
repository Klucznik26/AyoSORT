import os
import shutil
from pathlib import Path


class BatchFiles:
    @staticmethod
    def create_directories(base_path: str | Path, subdirs: list[str]) -> None:
        base = Path(base_path)
        base.mkdir(parents=True, exist_ok=True)
        for subdir in subdirs:
            (base / subdir).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def copy_image(src_path: str | Path, dest_path: str | Path) -> Path:
        """Copy an image without ever replacing an existing file.

        The destination is reserved atomically.  This avoids both accidental
        overwrites and races with another running AyoSORT instance.
        """
        source = Path(src_path)
        requested = Path(dest_path)
        requested.parent.mkdir(parents=True, exist_ok=True)

        for index in range(10_000):
            candidate = requested if index == 0 else requested.with_name(f"{requested.stem}_{index}{requested.suffix}")
            try:
                descriptor = os.open(candidate, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o666)
            except FileExistsError:
                continue

            try:
                with source.open("rb") as input_file, os.fdopen(descriptor, "wb") as output_file:
                    shutil.copyfileobj(input_file, output_file, length=1024 * 1024)
                shutil.copystat(source, candidate)
                return candidate
            except Exception:
                try:
                    candidate.unlink()
                except OSError:
                    pass
                raise

        raise FileExistsError(f"Unable to find a free destination name for {requested.name}")
