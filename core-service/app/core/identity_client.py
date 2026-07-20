import httpx

from app.core.config import settings
from app.core.exceptions import ForbiddenError

_ROLE_RANK = {"member": 0, "admin": 1, "owner": 2}


class IdentityClient:
    """
    Talks to identity-service for the one thing core-service doesn't own
    data for: "is this user allowed into this workspace, and at what role".

    Everything else about the user (email, id) already comes from the JWT
    itself, so most requests never need this client at all.
    """

    def __init__(self, base_url: str | None = None, timeout: float = 5.0):
        self.base_url = base_url or settings.IDENTITY_SERVICE_URL
        self.timeout = timeout

    def get_my_role(self, workspace_id: int, bearer_token: str) -> str:
        url = f"{self.base_url}/workspaces/{workspace_id}/members/me"
        headers = {"Authorization": f"Bearer {bearer_token}"}

        try:
            response = httpx.get(url, headers=headers, timeout=self.timeout)
        except httpx.RequestError as exc:
            raise ForbiddenError(
                "Could not verify workspace access (identity-service unreachable)"
            ) from exc

        if response.status_code == 403 or response.status_code == 404:
            raise ForbiddenError("You are not a member of this workspace")

        response.raise_for_status()
        return response.json()["role"]

    def require_role(self, workspace_id: int, bearer_token: str, minimum_role: str) -> str:
        role = self.get_my_role(workspace_id, bearer_token)
        if _ROLE_RANK.get(role, -1) < _ROLE_RANK[minimum_role]:
            raise ForbiddenError(f"This action requires the '{minimum_role}' role or higher")
        return role
