<div dir="rtl" align="right">

# MinerU Local GPU

استخراج محلی متن، فرمول، جدول و تصویر از PDF و اسناد Office با MinerU و GPU. هیچ API یا سرویس ابری لازم نیست.

## خروجی

MinerU برای هر سند در `output/<نام‌سند>/vlm/` این فایل‌ها را می‌سازد:

- `<نام‌سند>.md`: متن و ساختار استخراج‌شده
- `images/`: تصاویر و شکل‌های استخراج‌شده
- `<نام‌سند>_content_list_v2.json`: بلوک‌های ساختاریافته با مختصات
- `<نام‌سند>_layout.pdf`: PDF همراه با تشخیص layout

## نصب و دانلود مدل

ابتدا محیط مجازی و MinerU را نصب کنید. برای اجرا روی GPU، نسخهٔ CUDAدار PyTorch باید با درایور NVIDIA شما سازگار باشد.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -U mineru
```

مدل‌ها را **یک‌بار** دانلود کنید. برای PDFهای ریاضی و محتوای پیچیده، مدل `vlm` لازم است:

```powershell
# ModelScope - انتخاب پیش‌فرض این پروژه
.\.venv\Scripts\mineru-models-download.exe -s modelscope -m vlm

# یا Hugging Face
.\.venv\Scripts\mineru-models-download.exe -s huggingface -m vlm
```

برای دریافت همهٔ مدل‌ها (`pipeline` و `vlm`) از `-m all` استفاده کنید. دانلود اول ممکن است چند گیگابایت باشد؛ مدل‌ها در cache محلی ذخیره می‌شوند و در اجراهای بعدی دوباره دانلود نمی‌شوند.

## اجرای سریع

فایل PDF را روی [`extract-pdf.bat`](extract-pdf.bat) بکشید، یا در PowerShell اجرا کنید:

```powershell
.\extract-pdf.bat "C:\path\to\document.pdf"
```

خروجی در پوشهٔ `output` قرار می‌گیرد. اسکریپت به‌طور پیش‌فرض از GPU (`cuda`) و مدل محلی `vlm-engine` استفاده می‌کند.

## بهترین تنظیم برای هر نوع سند

| سند | Backend | دلیل |
| --- | --- | --- |
| کتاب، جزوه، فرمول و جدول | `vlm-engine` | بهترین دقت برای ساختار، فرمول و OCR |
| فایل ساده و طولانی | `pipeline` | سریع‌تر، با دقت کمتر برای فرمول و جدول |
| فایل پیچیده با VRAM کافی | `hybrid-engine` | دقت بالاتر، مصرف VRAM بیشتر |

اجرای مستقیم:

```powershell
$env:MINERU_DEVICE_MODE = 'cuda'
$env:MINERU_MODEL_SOURCE = 'modelscope'
$env:MINERU_TASK_RESULT_TIMEOUT_SECONDS = '43200' # 12 hours
.\.venv\Scripts\mineru.exe -p "C:\path\to\document.pdf" -o .\output -b vlm-engine
```

## نکات عملی برای سرعت و دقت

1. **PDF ریاضی سنگین:** از `vlm-engine` استفاده کنید. روی GPU با 8GB VRAM ممکن است چند ساعت طول بکشد؛ مدل را متوقف نکنید.
2. **PDF بزرگ:** ابتدا با بازهٔ صفحه اجرا کنید تا سریع‌تر بازخورد بگیرید:

```powershell
.\.venv\Scripts\mineru.exe -p "C:\path\to\document.pdf" -o .\output -b vlm-engine -s 0 -e 9
```

`-s` و `-e` صفرمبنایی هستند. برای کل سند این دو گزینه را حذف کنید.

3. **خطای timeout:** MinerU به‌طور پیش‌فرض بعد از 3600 ثانیه منتظر نتیجه نمی‌ماند. این پروژه مقدار `MINERU_TASK_RESULT_TIMEOUT_SECONDS=43200` را تنظیم می‌کند. برای اسناد خیلی سنگین، آن را بیشتر کنید.
4. **حافظهٔ GPU:** قبل از اجرا `nvidia-smi` را بررسی کنید و برنامه‌های GPU-محور دیگر را ببندید. 8GB VRAM در این نصب با `batch_size=4` اجرا می‌شود.
5. **مدل:** اگر مدل را پیشاپیش دانلود نکرده باشید، MinerU در اجرای اول تلاش می‌کند آن را دانلود کند. دانلود دستی بخش قبل، اجرای اول را قابل‌پیش‌بینی‌تر می‌کند.

## MCP برای Codex / Claude Code

سرور [`mineru_mcp_server.py`](mineru_mcp_server.py) دو ابزار می‌دهد:

- `mineru_info`: بررسی MinerU و CUDA
- `extract_document`: تبدیل سند به Markdown، JSON و تصاویر

نمونهٔ تست اتصال:

```powershell
.\.venv\Scripts\python.exe .\test_mcp_client.py
```

سرور برای PDFهای سنگین، timeout داخلی MinerU را 12 ساعت و timeout فرایند را کمی بیشتر تنظیم می‌کند.

## بررسی GPU

```powershell
nvidia-smi
.\.venv\Scripts\python.exe -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

## ساختار پروژه

```text
extract-pdf.bat       launcher ویندوز
mineru_mcp_server.py  سرور MCP محلی
test_mcp_client.py    تست MCP
output/               خروجی‌ها (در Git نادیده گرفته می‌شود)
```

</div>
