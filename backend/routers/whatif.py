# routers/whatif.py - API endpoint for the What-If campus savings calculator simulator.

from fastapi import APIRouter
from schemas import WhatIfInput, WhatIfResponse
from services.whatif_service import simulate_whatif

router = APIRouter(prefix="/whatif", tags=["What-If"])


@router.post("", response_model=WhatIfResponse)
def simulate_savings(input_data: WhatIfInput):
    """
    Simulates potential electricity, CO2, and Rupee savings from:
    1. Powering down computer lab PCs earlier
    2. Installing rooftop solar panels (with payback period)
    3. Replacing old fluorescent lights with LED tubes
    """
    result = simulate_whatif(input_data)
    return result
