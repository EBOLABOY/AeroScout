import logging # Add logging
from fastapi import APIRouter, Depends, Body, HTTPException, status # Add status

from app.core.dependencies import get_current_active_user, RateLimiter
# Remove direct service import: from app.services import kiwi_flight_service
from app.core.tasks import find_flights_task, _find_flights_task_async, find_flights_sync_async # Import the Celery task and internal function
from app.apis.v1.schemas import UserResponse, FlightSearchRequest, AsyncTaskResponse, FlightSearchResponse # Import response schemas

router = APIRouter()
logger = logging.getLogger(__name__) # Add logger

@router.post("/search", response_model=AsyncTaskResponse, status_code=status.HTTP_202_ACCEPTED) # Change response model and status code
async def search_flights_async( # Rename function for clarity
    request_body: FlightSearchRequest = Body(...),
    current_user: UserResponse = Depends(get_current_active_user),
    _ = Depends(RateLimiter(limit_type="flight")) # Apply flight-specific rate limiting
):
    """
    Submits a flight search task to the background queue.

    Requires authentication and is rate-limited.
    Returns a task ID for polling the result later.
    """
    try:
        # Convert Pydantic model to dict for Celery serialization
        search_params_dict = request_body.model_dump()

        # Add user info if needed by the task (optional, depends on task implementation)
        # search_params_dict['user_id'] = current_user.id

        # Send task to Celery queue
        task = find_flights_task.delay(search_params_dict=search_params_dict)
        logger.info(f"Submitted flight search task {task.id} for user {current_user.email}")

        return AsyncTaskResponse(task_id=task.id)

    except Exception as e:
        logger.error(f"Error submitting flight search task for user {current_user.email}: {e}", exc_info=True)
        # Catch potential errors during task submission
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to submit flight search task.")

@router.post("/search-sync", response_model=FlightSearchResponse, status_code=status.HTTP_200_OK)
async def search_flights_sync(
    request_body: FlightSearchRequest = Body(...),
    current_user: UserResponse = Depends(get_current_active_user),
    _ = Depends(RateLimiter(limit_type="flight")) # Apply flight-specific rate limiting
):
    """
    Performs a synchronous flight search and returns results immediately.

    Requires authentication and is rate-limited.
    This endpoint directly executes the search without using the task queue.
    """
    try:
        # Convert Pydantic model to dict
        search_params_dict = request_body.model_dump()
        
        logger.info(f"Starting synchronous flight search for user {current_user.email}")
        
        # Call the internal async function directly
        result = await find_flights_sync_async(search_params_dict)
        
        logger.info(f"Completed synchronous flight search for user {current_user.email}")
        
        return result

    except Exception as e:
        logger.error(f"Error in synchronous flight search for user {current_user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Flight search failed: {str(e)}"
        )