
from fastapi import APIRouter

from app.schemas.valuation import ValuationInput, ValuationResult
from app.services.dcf import calculate_dcf

router = APIRouter(prefix="/api/valuation", tags=["Valuation"])


@router.post("/dcf", response_model=ValuationResult)
def calculate_valuation(data: ValuationInput) -> ValuationResult:
    return calculate_dcf(data)
