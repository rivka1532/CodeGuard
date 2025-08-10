import logging
import os
import uuid
from typing import List
import tempfile
import matplotlib
from fastapi import APIRouter, UploadFile, File, Response, HTTPException, Query
from starlette.responses import FileResponse

from app.services.utils import delete_file_later, get_timestamped_filename, save_analysis_to_history

matplotlib.use('Agg')

from app.services.analyzer import analyze_code
from app.services.graph_generator import generate_analysis_graph

logger = logging.getLogger("uvicorn.error")

router = APIRouter()


@router.post("/alerts")
async def get_alerts(files: List[UploadFile] = File(...)):
    all_alerts = []
    full_messages = []

    for file in files:
        content = await file.read()
        try:
            alerts = analyze_code(content.decode("utf-8"), file.filename)
            save_analysis_to_history(file.filename, alerts)

            all_alerts.append({
                "file": file.filename,
                "alerts": alerts
            })
            for alert in alerts:
                full_messages.append(f"{file.filename}: {alert['message']}")
        except Exception as e:
            logger.error(f"Failed to analyze {file.filename}: {e}")
            all_alerts.append({
                "file": file.filename,
                "error": str(e)
            })
            full_messages.append(f"{file.filename}: ERROR - {str(e)}")
    tmp_dir = tempfile.gettempdir()
    filename = get_timestamped_filename()
    alert_file_path = os.path.join(tmp_dir, filename)
    with open(alert_file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(full_messages))
    delete_file_later(alert_file_path, delay=300)
    base_url = "http://localhost:8000"
    download_link = f"{base_url}/download-alerts?filename={filename}"
    return {
        "results": all_alerts,
        "download_link": download_link
    }


STATIC_DIR = "static/graphs"
os.makedirs(STATIC_DIR, exist_ok=True)


@router.post("/analyze-graph")
async def analyze_graph(files: List[UploadFile] = File(...)):
    image_links = []
    files_dict = {}

    if len(files) == 1:
        code = (await files[0].read()).decode("utf-8")
        png_bytes = generate_analysis_graph({files[0].filename: code})
        return Response(content=png_bytes, media_type="image/png")
    else:
        for file in files:
            try:
                code = (await file.read()).decode("utf-8")
                files_dict[file.filename] = code
            except Exception as e:
                logger.error(f"Failed to read file {file.filename}: {e}")
                image_links.append({
                    "file": file.filename,
                    "error": f"Failed to read file: {str(e)}"
                })

        try:
            png_bytes = generate_analysis_graph(files_dict)

            unique_name = f"{uuid.uuid4().hex}.png"
            file_path = os.path.join(STATIC_DIR, unique_name)

            with open(file_path, "wb") as f:
                f.write(png_bytes)

            image_url = f"/static/graphs/{unique_name}"
            image_links.append({
                "file": "all_files",
                "image_url": image_url
            })
        except Exception as e:
            logger.error(f"Graph generation failed: {e}")
            image_links.append({
                "file": "all_files",
                "error": str(e)
            })

        return {"graphs": image_links}

@router.get("/download-alerts", response_class=FileResponse)
def download_alerts(filename: str = Query(...)):
    alert_file_path = os.path.join(tempfile.gettempdir(), filename)

    if not os.path.exists(alert_file_path):
        raise HTTPException(status_code=404, detail="No alerts file found.")

    return FileResponse(
        path=alert_file_path,
        filename=filename,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )