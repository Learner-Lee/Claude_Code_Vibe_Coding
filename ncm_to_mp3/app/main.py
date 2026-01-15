"""
NCM to MP3 WebUI - FastAPI Backend
"""
import os
import uuid
import asyncio
import shutil
from pathlib import Path
from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configuration
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Ensure directories exist
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

app = FastAPI(title="NCM to MP3 Converter", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class ConversionTask(BaseModel):
    task_id: str
    status: str
    message: str
    files: List[str] = []


# Store task status in memory (use Redis for production)
tasks: dict[str, ConversionTask] = {}


def cleanup_old_files(directory: Path, max_age_hours: int = 24):
    """Clean up files older than max_age_hours"""
    import time
    current_time = time.time()
    for file_path in directory.iterdir():
        if file_path.is_file():
            file_age = current_time - file_path.stat().st_mtime
            if file_age > max_age_hours * 3600:
                file_path.unlink()


async def run_ncmdump(task_id: str, input_files: List[Path], output_dir: Path):
    """Run ncmdump command asynchronously"""
    try:
        tasks[task_id].status = "processing"
        tasks[task_id].message = "Converting files..."

        converted_files = []
        for input_file in input_files:
            # Run ncmdump for each file
            cmd = f'ncmdump "{input_file}" -o "{output_dir}"'
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                # Find the output file
                stem = input_file.stem
                for ext in ['.mp3', '.flac']:
                    output_file = output_dir / f"{stem}{ext}"
                    if output_file.exists():
                        converted_files.append(output_file.name)
                        break
            else:
                error_msg = stderr.decode() if stderr else "Unknown error"
                tasks[task_id].message = f"Error converting {input_file.name}: {error_msg}"

        if converted_files:
            tasks[task_id].status = "completed"
            tasks[task_id].message = f"Successfully converted {len(converted_files)} file(s)"
            tasks[task_id].files = converted_files
        else:
            tasks[task_id].status = "failed"
            if "Error" not in tasks[task_id].message:
                tasks[task_id].message = "No files were converted"

    except Exception as e:
        tasks[task_id].status = "failed"
        tasks[task_id].message = str(e)


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main page"""
    html_path = TEMPLATES_DIR / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.post("/api/upload")
async def upload_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...)
):
    """Upload NCM files and start conversion"""
    task_id = str(uuid.uuid4())
    task_upload_dir = UPLOAD_DIR / task_id
    task_output_dir = OUTPUT_DIR / task_id

    task_upload_dir.mkdir(exist_ok=True)
    task_output_dir.mkdir(exist_ok=True)

    input_files = []
    for file in files:
        if not file.filename.endswith('.ncm'):
            continue

        file_path = task_upload_dir / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        input_files.append(file_path)

    if not input_files:
        raise HTTPException(status_code=400, detail="No valid NCM files uploaded")

    # Create task
    tasks[task_id] = ConversionTask(
        task_id=task_id,
        status="pending",
        message=f"Queued {len(input_files)} file(s) for conversion",
        files=[]
    )

    # Start conversion in background
    background_tasks.add_task(run_ncmdump, task_id, input_files, task_output_dir)

    return {"task_id": task_id, "message": f"Uploaded {len(input_files)} file(s)"}


@app.get("/api/status/{task_id}")
async def get_status(task_id: str):
    """Get conversion task status"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]


@app.get("/api/download/{task_id}/{filename}")
async def download_file(task_id: str, filename: str):
    """Download converted file"""
    file_path = OUTPUT_DIR / task_id / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/octet-stream"
    )


@app.get("/api/download-all/{task_id}")
async def download_all(task_id: str):
    """Download all converted files as zip"""
    import zipfile
    import io

    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = tasks[task_id]
    if task.status != "completed":
        raise HTTPException(status_code=400, detail="Task not completed")

    task_output_dir = OUTPUT_DIR / task_id
    zip_path = OUTPUT_DIR / f"{task_id}.zip"

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for filename in task.files:
            file_path = task_output_dir / filename
            if file_path.exists():
                zipf.write(file_path, filename)

    return FileResponse(
        path=str(zip_path),
        filename="converted_files.zip",
        media_type="application/zip"
    )


@app.delete("/api/cleanup/{task_id}")
async def cleanup_task(task_id: str):
    """Clean up task files"""
    task_upload_dir = UPLOAD_DIR / task_id
    task_output_dir = OUTPUT_DIR / task_id
    zip_path = OUTPUT_DIR / f"{task_id}.zip"

    if task_upload_dir.exists():
        shutil.rmtree(task_upload_dir)
    if task_output_dir.exists():
        shutil.rmtree(task_output_dir)
    if zip_path.exists():
        zip_path.unlink()

    if task_id in tasks:
        del tasks[task_id]

    return {"message": "Cleaned up successfully"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
