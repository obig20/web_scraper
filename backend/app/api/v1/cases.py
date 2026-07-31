"""Case management endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import DbSession
from app.models.case import Case
from app.schemas.case import CaseCreate, CaseRead, CaseSummary
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/cases", tags=["Cases"])


@router.get("", response_model=PaginatedResponse[CaseSummary])
async def list_cases(db: DbSession, page: int = 1, page_size: int = 20):
    offset = (page - 1) * page_size
    all_cases = (await db.execute(select(Case).order_by(Case.created_at.desc()))).scalars().all()
    items = all_cases[offset : offset + page_size]
    return PaginatedResponse(
        items=items,
        total=len(all_cases),
        page=page,
        page_size=page_size,
        pages=max(1, (len(all_cases) + page_size - 1) // page_size),
    )


@router.post("", response_model=CaseRead, status_code=status.HTTP_201_CREATED)
async def create_case(data: CaseCreate, db: DbSession):
    existing = await db.execute(select(Case).where(Case.slug == data.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Case slug already exists")
    case = Case(**data.model_dump())
    db.add(case)
    await db.flush()
    return case


@router.get("/{case_id}", response_model=CaseRead)
async def get_case(case_id: UUID, db: DbSession):
    case = await db.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case
