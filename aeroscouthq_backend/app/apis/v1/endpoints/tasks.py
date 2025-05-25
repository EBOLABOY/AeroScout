# app/apis/v1/endpoints/tasks.py
from fastapi import APIRouter, HTTPException, status, Depends
from celery.result import AsyncResult
from app.celery_worker import celery_app # Your Celery app instance
from app.apis.v1.schemas import UserResponse # For auth dependency
from app.core.dependencies import get_current_active_user # For auth

router = APIRouter()

@router.get("/results/{task_id}", summary="Get Celery task status and result", response_model=dict) # Added response_model for clarity
async def get_task_status_and_result(
    task_id: str,
    current_user: UserResponse = Depends(get_current_active_user) # Secure this endpoint
):
    """
    Retrieve the status and result of a Celery task.
    Requires authentication.
    """
    task_result = AsyncResult(task_id, app=celery_app)

    if task_result.state == 'PENDING':
        return {"task_id": task_id, "status": "PENDING", "message": "Task is currently pending execution."}
    elif task_result.state == 'STARTED':
        # You might want to include metadata if your task provides it during STARTED state
        meta = task_result.info if isinstance(task_result.info, dict) else {}
        return {"task_id": task_id, "status": "STARTED", "message": "Task has started processing.", "meta": meta}
    elif task_result.state == 'SUCCESS':
        # Ensure the result is JSON-serializable if it's complex
        result_data = task_result.result
        return {"task_id": task_id, "status": "SUCCESS", "result": result_data}
    elif task_result.state == 'FAILURE':
        # Log the failure internally
        # print(f"Task {task_id} failed. Result: {task_result.result}, Traceback: {task_result.traceback}") # Consider logging framework
        # Return a structured error message to the client
        # Avoid exposing raw tracebacks or sensitive error details
        error_info = {
            "type": str(type(task_result.result).__name__), # Exception type
            "message": "Task execution failed.", # Generic message
            # "details": str(task_result.result) # Potentially sensitive, consider omitting or sanitizing for client
        }
        # It's better to raise HTTPException for failures so FastAPI handles the response status code correctly.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"task_id": task_id, "status": "FAILURE", "error": error_info, "message": "Task encountered an error."}
        )
    elif task_result.state == 'RETRY':
        # You might want to include metadata if your task provides it during RETRY state
        meta = task_result.info if isinstance(task_result.info, dict) else {}
        return {"task_id": task_id, "status": "RETRY", "message": "Task is scheduled for retry.", "meta": meta}
    else: # Covers REVOKED, etc.
        return {"task_id": task_id, "status": task_result.state, "message": f"Task is in state: {task_result.state}"}