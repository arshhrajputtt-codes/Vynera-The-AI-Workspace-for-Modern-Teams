from fastapi import Depends, HTTPException, status

from app.core.exceptions import ForbiddenError
from app.core.identity_client import IdentityClient
from app.dependencies.auth import CurrentUser, get_current_user

_identity_client = IdentityClient()


def require_workspace_role(minimum_role: str = "member"):
    """
    Usage: Depends(require_workspace_role("admin")) on any route with a
    `workspace_id` path parameter. Raises 403 if the caller isn't at least
    `minimum_role` in that workspace.
    """

    def dependency(
        workspace_id: int,
        current_user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        try:
            _identity_client.require_role(workspace_id, current_user.token, minimum_role)
        except ForbiddenError as exc:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
        return current_user

    return dependency
