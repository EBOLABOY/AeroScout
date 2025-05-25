import secrets
import string
from typing import Optional

from fastapi import HTTPException, status

from app.database.crud import invitation_crud


def _generate_invitation_code(length: int = 10) -> str:
    """Generates a random alphanumeric invitation code."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


async def create_new_invitation_code(created_by_user_id: Optional[int] = None) -> str:
    """
    Generates a new unique invitation code and stores it in the database.
    """
    while True:
        code = _generate_invitation_code()
        # Check if the generated code already exists
        existing_code = await invitation_crud.get_invitation_code(code)
        if not existing_code:
            break # Unique code found

    # Store the new code
    await invitation_crud.create_invitation_code(code, created_by_user_id)
    return code


async def validate_invitation_code(code: str) -> bool:
    """
    Validates if an invitation code exists and is not used.
    """
    invitation = await invitation_crud.get_invitation_code(code)
    return invitation is not None and not invitation.is_used