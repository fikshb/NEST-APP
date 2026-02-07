from pydantic import BaseModel


class UnitOccupancy(BaseModel):
    available: int
    reserved: int
    occupied: int


class DealStatusChart(BaseModel):
    in_progress: int
    invoice_requested: int
    completed: int


class DashboardSummary(BaseModel):
    deals_in_progress: int
    deals_blocked: int
    deals_awaiting_action: int
    deals_completed: int
    unit_occupancy: UnitOccupancy
    deal_status_chart: DealStatusChart
