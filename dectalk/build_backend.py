from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


class DectalkBuildError(RuntimeError):
    pass


def native_library_name() -> str:
    if sys.platform == "darwin":
        return "libdectalk.dylib"
    if sys.platform == "win32":
        return "dectalk.dll"
    return "libdectalk.so"


def native_bundle_dir() -> Path:
    return Path(__file__).resolve().parent / "native_bin"


def build_backend(
    *,
    force: bool = False,
    original_repo: str | Path | None = None,
    output_dir: str | Path | None = None,
) -> Path:
    """Build the original DECtalk engine into this Python package.

    The checked-out original repository is left untouched.  We archive the
    buildable CMake branch into dectalk-python/build, patch that temporary copy
    for headless Linux, and copy only the runtime files used by ctypes.
    """

    package_root = Path(__file__).resolve().parents[1]
    workspace_root = package_root.parent
    repo = Path(original_repo) if original_repo is not None else workspace_root / "original" / "dectalk"
    out_dir = Path(output_dir) if output_dir is not None else native_bundle_dir()
    lib_name = native_library_name()

    if not force and _is_complete_bundle(out_dir, lib_name):
        return out_dir

    if sys.platform == "win32":
        raise DectalkBuildError("native DECtalk auto-build is currently implemented for Unix-like systems")
    if not repo.exists():
        raise DectalkBuildError(f"original DECtalk repository was not found: {repo}")
    if shutil.which("git") is None:
        raise DectalkBuildError("git is required to export original/dectalk origin/cmake")
    if shutil.which("cmake") is None:
        raise DectalkBuildError("cmake is required to build the original DECtalk backend")
    if shutil.which("tar") is None:
        raise DectalkBuildError("tar is required to unpack the original DECtalk archive")

    build_area = package_root / "build"
    source_dir = build_area / "dectalk-native-src"
    build_dir = build_area / "dectalk-native-build"

    if force:
        shutil.rmtree(source_dir, ignore_errors=True)
        shutil.rmtree(build_dir, ignore_errors=True)

    if not (source_dir / "CMakeLists.txt").exists():
        shutil.rmtree(source_dir, ignore_errors=True)
        source_dir.mkdir(parents=True)
        _export_cmake_branch(repo, source_dir)
        _patch_headless_linux_build(source_dir)

    build_dir.mkdir(parents=True, exist_ok=True)
    _run(["cmake", "-S", str(source_dir), "-B", str(build_dir), "-DCMAKE_BUILD_TYPE=Release"])
    jobs = str(max(1, os.cpu_count() or 1))
    _run(["cmake", "--build", str(build_dir), "--target", "dict", "-j", jobs])
    _run(["cmake", "--build", str(build_dir), "--target", "say", "-j", jobs])

    runtime_dir = build_dir / "bin"
    library_dir = build_dir / "lib"
    built_lib = library_dir / lib_name
    built_conf = runtime_dir / "DECtalk.conf"
    built_dict = runtime_dir / "dic" / "dtalk_us.dic"
    for required in (built_lib, built_conf, built_dict):
        if not required.exists():
            raise DectalkBuildError(f"DECtalk build did not produce {required}")

    if out_dir.exists():
        shutil.rmtree(out_dir)
    (out_dir / "dic").mkdir(parents=True)
    shutil.copy2(built_lib, out_dir / lib_name)
    shutil.copy2(built_conf, out_dir / "DECtalk.conf")
    shutil.copy2(built_dict, out_dir / "dic" / "dtalk_us.dic")
    say = runtime_dir / "say"
    if say.exists():
        shutil.copy2(say, out_dir / "say")

    for path in out_dir.iterdir():
        if path.is_file():
            path.chmod(path.stat().st_mode | 0o755)
    return out_dir


def _is_complete_bundle(bundle_dir: Path, lib_name: str) -> bool:
    return (
        (bundle_dir / lib_name).exists()
        and (bundle_dir / "DECtalk.conf").exists()
        and (bundle_dir / "dic" / "dtalk_us.dic").exists()
    )


def _export_cmake_branch(repo: Path, source_dir: Path) -> None:
    archive = subprocess.Popen(
        ["git", "-C", str(repo), "archive", "--format=tar", "origin/cmake"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert archive.stdout is not None
    unpack = subprocess.run(
        ["tar", "-x", "-C", str(source_dir)],
        stdin=archive.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    archive.stdout.close()
    _, archive_stderr = archive.communicate()
    if archive.returncode != 0:
        raise DectalkBuildError(archive_stderr.decode(errors="replace"))
    if unpack.returncode != 0:
        raise DectalkBuildError(unpack.stderr)


def _patch_headless_linux_build(source_dir: Path) -> None:
    root_cmake = source_dir / "src" / "CMakeLists.txt"
    text = root_cmake.read_text(encoding="utf-8")
    text = text.replace(
        "  if (NOT APPLE)\n"
        "    add_subdirectory(samplosf/src/speak)\n"
        "    add_subdirectory(samplosf/src/windict)\n"
        "  endif()\n",
        "  # The Python package only needs the engine, dictionary builder, and\n"
        "  # sample say frontend.  GTK demos are intentionally skipped.\n",
    )
    root_cmake.write_text(text, encoding="utf-8")

    dapi_cmake = source_dir / "src" / "dapi" / "src" / "CMakeLists.txt"
    text = dapi_cmake.read_text(encoding="utf-8")
    text = text.replace(
        "  if (APPLE)\n"
        "    list(APPEND DAPI_LINK_LIBS portaudio \"-framework CoreAudio\" \"-framework AudioToolbox\")\n"
        "  else()\n"
        "    # Assume that non-Apple machines are Linux.\n"
        "    list(APPEND DAPI_LINK_LIBS pulse-simple pulse)\n"
        "    list(APPEND DAPI_DEFINES USE_PULSEAUDIO)\n"
        "  endif()\n",
        "  if (APPLE)\n"
        "    list(APPEND DAPI_LINK_LIBS portaudio \"-framework CoreAudio\" \"-framework AudioToolbox\")\n"
        "  else()\n"
        "    list(APPEND DAPI_DEFINES DISABLE_AUDIO)\n"
        "  endif()\n",
    )
    text = text.replace(
        "  list(APPEND DAPI_SOURCE_FILES nt/linux_audio.c api/init.c osf/loadable.c osf/dtmmio.c)",
        "  list(APPEND DAPI_SOURCE_FILES nt/disable_audio.c api/init.c osf/loadable.c osf/dtmmio.c)",
    )
    dapi_cmake.write_text(text, encoding="utf-8")

    disable_audio = source_dir / "src" / "dapi" / "src" / "nt" / "disable_audio.c"
    text = disable_audio.read_text(encoding="utf-8")
    if "#include <string.h>" not in text:
        text = text.replace('#include "disable_audio.h"\n', '#include "disable_audio.h"\n#include <string.h>\n')
    text = text.replace("UINT32 waveOutGetDevCaps(UINT32 uDeviceID", "UINT32 waveOutGetDevCaps(UINT16 uDeviceID")
    text = text.replace("DWORD OSS_wodMessage(UINT16 wDevID,", "DWORD OSS_wodMessage(void *WOutDev,")
    if "OSS_WaveInit" not in text:
        text += "\nLONG OSS_WaveInit(void)\n{\n  return 0;\n}\n"
    disable_audio.write_text(text, encoding="utf-8")


def _run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    if proc.returncode != 0:
        raise DectalkBuildError(
            "command failed: "
            + " ".join(cmd)
            + "\n"
            + proc.stdout
            + "\n"
            + proc.stderr
        )


if __name__ == "__main__":
    print(build_backend(force="--force" in sys.argv))
