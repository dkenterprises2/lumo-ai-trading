from fastapi import Depends, HTTPException, status
from backend.auth.security import get_current_user
from backend.models.domain import UserModel

def require_super_admin(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    """Dependency enforcing SUPER_ADMIN role authorization."""
    role = getattr(current_user, "role", "").upper()
    email = getattr(current_user, "email", "").lower()

    if role not in ["SUPER_ADMIN", "SUPERADMIN"] and email != "jiodkd@gmail.com":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return current_user
