#!/usr/bin/env python
"""Local MinerU MCP server.

Exposes the locally installed MinerU (running its 1.2B VLM on the local GPU) as MCP tools,
so any Claude Code chat can parse PDFs/images/Office docs without any cloud service or API key.
Under the hood it calls the verified `mineru` CLI in this folder's virtual environment.

IMPORTANT (stdio MCP): this process speaks the MCP protocol over stdout, so the MinerU
subprocess output is fully captured (never inherited) to avoid corrupting the channel.
"""
import os
import glob
import json
import subprocess
from pathlib import Path

from mcp.server.fastmcp import FastMCP

BASE = Path(__file__).resolve().parent
MINERU_EXE = str(BASE / ".venv" / "Scripts" / "mineru.exe")
VENV_PY = str(BASE / ".venv" / "Scripts" / "python.exe")
DEFAULT_OUT = str(BASE / "output")

mcp = FastMCP("mineru")


def _find_latest(output_dir: str, stem: str, pattern: str):
    matches = glob.glob(os.path.join(output_dir, stem, "**", pattern), recursive=True)
    return max(matches, key=os.path.getmtime) if matches else None


@mcp.tool()
def extract_document(
    file_path: str,
    backend: str = "vlm-engine",
    output_dir: str = "",
    start_page: int = -1,
    end_page: int = -1,
) -> dict:
    """Parse / convert / OCR a LOCAL document (PDF, image, DOCX, PPTX, XLSX) into Markdown
    plus structured JSON, using the locally installed MinerU and its 1.2B VLM on the local GPU.

    Use this whenever the user wants to extract text, tables, or figures from a document,
    convert a PDF to markdown, or OCR a scanned file. Runs fully locally (no cloud, no API key).

    Returns: markdown text, a structured content list (typed blocks — title/paragraph/table/image —
    each with bounding boxes; tables are returned as HTML), and the paths of the output files.

    Args:
        file_path: Absolute path to the input file (or a directory of files).
        backend: 'vlm-engine' (default, high-accuracy VLM on GPU), 'pipeline' (lighter/faster),
                 or 'hybrid-engine' (highest accuracy, more VRAM).
        output_dir: Folder for results. Defaults to the MinerU/output folder.
        start_page: First page (0-based) for PDFs; -1 means from the beginning.
        end_page: Last page (0-based) for PDFs; -1 means to the end.
    """
    src = Path(file_path)
    if not src.exists():
        return {"status": "error", "error": f"File not found: {file_path}"}

    out = output_dir.strip() or DEFAULT_OUT
    os.makedirs(out, exist_ok=True)

    cmd = [MINERU_EXE, "-p", str(src), "-o", out, "-b", backend]
    if start_page >= 0:
        cmd += ["-s", str(start_page)]
    if end_page >= 0:
        cmd += ["-e", str(end_page)]

    env = dict(os.environ)
    env["MINERU_DEVICE_MODE"] = "cuda"
    env.setdefault("MINERU_MODEL_SOURCE", "modelscope")
    # MinerU defaults to one hour. Dense math PDFs can legitimately exceed that.
    env.setdefault("MINERU_TASK_RESULT_TIMEOUT_SECONDS", "43200")

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=43800)
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": "MinerU timed out after 12 hours."}

    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "")[-2000:]
        return {"status": "error", "returncode": proc.returncode, "log_tail": tail}

    stem = src.stem
    md_path = _find_latest(out, stem, f"{stem}.md") or _find_latest(out, stem, "*.md")
    cl_path = (_find_latest(out, stem, "*content_list_v2.json")
               or _find_latest(out, stem, "*content_list.json"))

    markdown = Path(md_path).read_text(encoding="utf-8", errors="replace") if md_path else ""
    content_list = None
    if cl_path:
        try:
            content_list = json.loads(Path(cl_path).read_text(encoding="utf-8", errors="replace"))
        except Exception:
            content_list = None

    return {
        "status": "ok",
        "input": str(src),
        "backend": backend,
        "output_dir": os.path.dirname(md_path) if md_path else out,
        "markdown_path": md_path,
        "content_list_path": cl_path,
        "markdown": markdown,
        "content_list": content_list,
    }


@mcp.tool()
def mineru_info() -> dict:
    """Report local MinerU status: the MinerU version and whether the GPU (CUDA) is available."""
    info = {"mineru_exe": MINERU_EXE}
    try:
        v = subprocess.run([MINERU_EXE, "--version"], capture_output=True, text=True, timeout=60)
        info["version"] = (v.stdout or v.stderr).strip()
    except Exception as e:
        info["version_error"] = str(e)
    try:
        c = subprocess.run(
            [VENV_PY, "-c",
             "import torch;print(torch.cuda.is_available(), "
             "torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'none')"],
            capture_output=True, text=True, timeout=120)
        info["cuda"] = c.stdout.strip()
    except Exception as e:
        info["cuda_error"] = str(e)
    return info


if __name__ == "__main__":
    mcp.run()
