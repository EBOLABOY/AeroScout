from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status

from app.core.security import verify_password, get_password_hash, create_access_token
from app.database.crud import user_crud, invitation_crud
from app.apis.v1.schemas import UserCreate, UserResponse, Token


async def register_user(user_in: UserCreate) -> UserResponse:
    """
    Registers a new user after validating the invitation code and email uniqueness.
    Hashes the password before storing.
    Marks the invitation code as used.
    """
    # 1. Validate invitation code
    invitation = await invitation_crud.get_invitation_code(user_in.invitation_code)
    if not invitation or invitation.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or used invitation code",
        )

    # 2. Check if email is already registered
    existing_user = await user_crud.get_user_by_email(user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # 3. Hash the password
    hashed_password = get_password_hash(user_in.password)

    # 4. Create the user
    # Create a dictionary excluding the invitation code for user creation
    user_data = user_in.model_dump(exclude={"invitation_code"})
    user_data["hashed_password"] = hashed_password
    new_user_id = await user_crud.create_user(user_data)

    # 5. Mark invitation code as used
    await invitation_crud.mark_invitation_code_as_used(invitation["id"], new_user_id) # Use invitation ID and new_user_id

    # 6. Fetch the newly created user details
    created_user = await user_crud.get_user_by_id(new_user_id)
    if not created_user:
        # This should ideally not happen if create_user was successful
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve created user",
        )

    # 7. Return UserResponse
    # Convert the database model/dict to UserResponse Pydantic model
    # Assuming get_user_by_id returns a dict or compatible object
    return UserResponse.model_validate(created_user)


async def authenticate_user(email: str, password: str) -> Optional[dict]:
    """
    Authenticates a user based on email and password.
    Updates the last login time upon successful authentication.
    """
    # 1. Get user by email
    user = await user_crud.get_user_by_email(email)

    # 2. Check if user exists and password matches
    if not user or not verify_password(password, user["hashed_password"]): # Assuming user is a dict
        return None

    # 3. Update last login time
    await user_crud.update_last_login(user["id"]) # Assuming user dict has 'id'

    # 4. Return user data (as dict, as specified)
    # Ensure the returned dict structure is appropriate for token creation later
    return dict(user) # Convert RowProxy or similar to dict if necessary