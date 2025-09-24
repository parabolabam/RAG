from fastapi import APIRouter, Depends, HTTPException

from crons.scheduler import (
    KNOWN_JOB_IDS,
    SchedulerNotRunningError,
    UnknownJobError,
    ensure_scheduler_started,
    get_jobs_overview,
    get_scheduler_state,
    pause_job,
    resume_job,
    shutdown_scheduler,
    trigger_job,
)
from senpy_ai_news_report.utils.auth import require_api_token

router = APIRouter(
    prefix="/cron",
    tags=["cron"],
    dependencies=[Depends(require_api_token)],
)


@router.get("/status")
async def cron_status():
    return {"state": get_scheduler_state(), "jobs": get_jobs_overview()}


@router.post("/start")
async def start_scheduler():
    await ensure_scheduler_started(refresh=True)
    return {"state": get_scheduler_state(), "jobs": get_jobs_overview()}


@router.post("/stop")
async def stop_scheduler():
    await shutdown_scheduler()
    return {"state": get_scheduler_state()}


def _validate_job(job_id: str) -> str:
    if job_id not in KNOWN_JOB_IDS:
        raise HTTPException(status_code=404, detail=f"Unknown job '{job_id}'")
    return job_id


@router.post("/jobs/{job_id}/trigger")
async def trigger(job_id: str):
    job = _validate_job(job_id)
    await trigger_job(job)
    return {"job": job, "status": "triggered"}


@router.post("/jobs/{job_id}/pause")
async def pause(job_id: str):
    job = _validate_job(job_id)
    try:
        pause_job(job)
    except SchedulerNotRunningError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except UnknownJobError:
        raise HTTPException(status_code=404, detail=f"Unknown job '{job}'")
    return {"job": job, "status": "paused"}


@router.post("/jobs/{job_id}/resume")
async def resume(job_id: str):
    job = _validate_job(job_id)
    try:
        resume_job(job)
    except SchedulerNotRunningError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except UnknownJobError:
        raise HTTPException(status_code=404, detail=f"Unknown job '{job}'")
    return {"job": job, "status": "running"}
