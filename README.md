# MinerU Local GPU

Local extraction of text, formulas, tables, and images from PDFs and Office documents with MinerU and an NVIDIA GPU. No cloud service or API key is required.

## Output

For each input document, MinerU creates files under `output/<document-name>/vlm/`:

- `<document-name>.md`: extracted text and document structure
- `images/`: extracted figures and images
- `<document-name>_content_list_v2.json`: structured blocks with bounding boxes
- `<document-name>_layout.pdf`: PDF with detected layout annotations

## Installation and Model Download

Create a virtual environment and install MinerU. For GPU inference, install a CUDA-enabled PyTorch build compatible with your NVIDIA driver.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install --upgrade mineru
```

Download the models once. The `vlm` model is required for math-heavy or complex documents:

```powershell
# ModelScope: the default source used by this project
.\.venv\Scripts\mineru-models-download.exe -s modelscope -m vlm

# Or Hugging Face
.\.venv\Scripts\mineru-models-download.exe -s huggingface -m vlm
```

Use `-m all` to download both `pipeline` and `vlm` models. The first download may be several GB; models are cached locally and reused on later runs.

## Quick Start

Drag a PDF onto [`extract-pdf.bat`](extract-pdf.bat), or run:

```powershell
.\extract-pdf.bat "C:\path\to\document.pdf"
```

Results are written to `output`. The launcher uses GPU (`cuda`) and the local `vlm-engine` backend by default.

## Best Backend for Each Document

| Document type | Backend | Why |
| --- | --- | --- |
| Books, notes, formulas, and tables | `vlm-engine` | Best accuracy for structure, formulas, and OCR |
| Simple and long documents | `pipeline` | Faster, with lower formula/table accuracy |
| Complex documents with sufficient VRAM | `hybrid-engine` | Higher accuracy, more VRAM usage |

Direct execution:

```powershell
$env:MINERU_DEVICE_MODE = 'cuda'
$env:MINERU_MODEL_SOURCE = 'modelscope'
$env:MINERU_TASK_RESULT_TIMEOUT_SECONDS = '43200' # 12 hours
.\.venv\Scripts\mineru.exe -p "C:\path\to\document.pdf" -o .\output -b vlm-engine
```

## Practical Performance Tips

1. **Math-heavy PDFs:** Use `vlm-engine`. On an 8 GB GPU, dense documents can take hours; do not stop the process early.
2. **Large PDFs:** Start with a page range for a fast quality check:

```powershell
.\.venv\Scripts\mineru.exe -p "C:\path\to\document.pdf" -o .\output -b vlm-engine -s 0 -e 9
```

`-s` and `-e` are zero-based. Omit them to process the entire document.

3. **Timeouts:** MinerU normally stops waiting for a result after 3600 seconds. This project sets `MINERU_TASK_RESULT_TIMEOUT_SECONDS=43200`. Raise it further for exceptionally dense documents.
4. **GPU memory:** Run `nvidia-smi` before processing and close other GPU-intensive programs. This setup uses `batch_size=4` on an 8 GB GPU.
5. **Model caching:** MinerU may download a model on first use if it is not already cached. Downloading it explicitly beforehand makes the first run predictable.

## MCP for Codex / Claude Code

[`mineru_mcp_server.py`](mineru_mcp_server.py) exposes two local MCP tools:

- `mineru_info`: checks MinerU and CUDA availability
- `extract_document`: converts a document to Markdown, JSON, and images

Test the MCP connection:

```powershell
.\.venv\Scripts\python.exe .\test_mcp_client.py
```

The server sets MinerU's result timeout to 12 hours for heavy PDFs and allows a little extra process time.

## Verify GPU Access

```powershell
nvidia-smi
.\.venv\Scripts\python.exe -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

## Project Layout

```text
extract-pdf.bat       Windows launcher
mineru_mcp_server.py  Local MCP server
test_mcp_client.py    MCP connection test
output/               Generated output (ignored by Git)
```
