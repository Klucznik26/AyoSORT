from pathlib import Path
import shutil


class BatchFiles:
    @staticmethod
    def create_directories(base_path: str | Path, subdirs: list[str]) -> None:
        base = Path(base_path)
        base.mkdir(parents=True, exist_ok=True)
        for subdir in subdirs:
            (base / subdir).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def copy_image(src_path: str | Path, dest_path: str | Path) -> None:
        shutil.copy2(src_path, dest_path)
