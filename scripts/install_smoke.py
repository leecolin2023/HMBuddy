"""安装态 Smoke Test（BUG-017 / T14 / AC-H17）。

在 wheel 安装后的干净环境运行：
    python scripts/install_smoke.py

验证：
1. Built-in plugin manifests 随包分发且可被发现；
2. Registry 注册正常；
3. read_artifact() 可读取样例；
4. desktop / llm / 核心包可导入。
"""
from __future__ import annotations

import sys
from pathlib import Path

EXPECTED_BUILTIN_PLUGINS = {
    "hmbuddy.docx.core",
    "hmbuddy.doc.core",
    "hmbuddy.pdf.core",
    "hmbuddy.xlsx.core",
    "hmbuddy.xls.core",
    "hmbuddy.pptx.core",
    "hmbuddy.text.core",
}


def main() -> int:
    from plugin_runtime import get_default_runtime

    assembly = get_default_runtime()
    loaded_ids = {item.discovered.manifest.id for item in assembly.load_report.loaded}
    missing = EXPECTED_BUILTIN_PLUGINS - loaded_ids
    if missing:
        print(f"FAIL: missing built-in plugins: {sorted(missing)}")
        print(f"load failures: {assembly.load_report.failures}")
        return 1

    from services.artifact_reader import read_artifact

    sample = Path("_install_smoke_sample.txt")
    sample.write_text("安装态 smoke 测试内容", encoding="utf-8")
    try:
        artifact = read_artifact(sample)
    finally:
        sample.unlink(missing_ok=True)
    if artifact.artifact_type != "txt" or not artifact.blocks:
        print(f"FAIL: unexpected artifact: {artifact.artifact_type}")
        return 1
    if artifact.provenance["plugin_id"] != "hmbuddy.text.core":
        print(
            "FAIL: unexpected plugin: "
            f"{artifact.provenance['plugin_id']}"
        )
        return 1

    import desktop.app  # noqa: F401  (CLI/desktop entry point 可 import)
    import llm.client  # noqa: F401
    import plugin_runtime  # noqa: F401
    import workspace  # noqa: F401

    print("install smoke OK:", sorted(loaded_ids))
    return 0


if __name__ == "__main__":
    sys.exit(main())
