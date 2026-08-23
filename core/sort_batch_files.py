# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Klucznik MZ
import errno
import os
import shutil
import tempfile
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
        """Copy an image crash-safely without replacing an existing file.

        Data first lands in a hidden ``.part`` file in the destination
        directory.  Only a fully flushed copy is atomically published under
        its final name, so an interrupted large copy never looks complete.
        """
        source = Path(src_path)
        requested = Path(dest_path)
        requested.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=requested.parent,
                prefix=f".{requested.stem}-",
                suffix=f"{requested.suffix}.part",
                delete=False,
            ) as output_file:
                temporary_path = Path(output_file.name)
                with source.open("rb") as input_file:
                    shutil.copyfileobj(input_file, output_file, length=1024 * 1024)
                output_file.flush()
                os.fsync(output_file.fileno())
            shutil.copystat(source, temporary_path)
            with temporary_path.open("rb") as completed_file:
                os.fsync(completed_file.fileno())

            for index in range(10_000):
                candidate = (
                    requested if index == 0 else requested.with_name(f"{requested.stem}_{index}{requested.suffix}")
                )
                try:
                    os.link(temporary_path, candidate)
                except FileExistsError:
                    continue
                except OSError as exc:
                    unsupported = {errno.EPERM, errno.EXDEV, errno.ENOSYS}
                    if hasattr(errno, "EOPNOTSUPP"):
                        unsupported.add(errno.EOPNOTSUPP)
                    if exc.errno not in unsupported:
                        raise
                    try:
                        descriptor = os.open(candidate, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o666)
                    except FileExistsError:
                        continue
                    os.close(descriptor)
                    try:
                        os.replace(temporary_path, candidate)
                    except Exception:
                        candidate.unlink(missing_ok=True)
                        raise
                    temporary_path = None
                    BatchFiles._fsync_directory(candidate.parent)
                    return candidate
                else:
                    temporary_path.unlink()
                    temporary_path = None
                    BatchFiles._fsync_directory(candidate.parent)
                    return candidate

            raise FileExistsError(f"Unable to find a free destination name for {requested.name}")
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    @staticmethod
    def _fsync_directory(directory: Path) -> None:
        if not hasattr(os, "O_DIRECTORY"):
            return
        try:
            descriptor = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
        except OSError:
            return
        try:
            os.fsync(descriptor)
        except OSError:
            pass
        finally:
            os.close(descriptor)
