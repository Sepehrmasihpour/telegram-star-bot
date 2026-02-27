from fastapi.responses import RedirectResponse
from fastapi import APIRouter

router = APIRouter()


@router.get(path="/", response_class=RedirectResponse, include_in_schema=False)
async def redirect_index():
    """Redirect root to read-only docs."""
    return "/redoc"
