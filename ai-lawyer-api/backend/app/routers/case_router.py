from fastapi import APIRouter, HTTPException, Depends, Query
from ..schemas.case_schema import CaseCreate, CaseUpdate, CaseRead
from ..common.pagination import Paginated, PageMeta
from ..common.params import PageParams
from ..services import case_service

router = APIRouter(prefix="/cases", tags=["Case"])


@router.get("/", response_model=Paginated[CaseRead])
async def list_cases(
    page_params: PageParams = Depends(),
    name: str | None = Query(None, description="案件名称(模糊)"),
    status: str | None = Query(None, description="案件状态"),
    location: str | None = Query(None, description="地点(模糊)"),
    plaintiff: str | None = Query(None, description="原告(模糊)"),
    defendant: str | None = Query(None, description="被告(模糊)"),
):
    items, total = await case_service.list_cases_service(
        name=name, status=status, location=location, plaintiff=plaintiff, defendant=defendant,
        page=page_params.page, page_size=page_params.page_size,
    )
    return {"meta": PageMeta(total=total, page=page_params.page, page_size=page_params.page_size), "items": items}


@router.get("/{case_id}", response_model=CaseRead)
async def get_case(case_id: int):
    obj = await case_service.get_case_by_id(case_id)
    if not obj:
        raise HTTPException(404, "Case not found")
    return obj


@router.post("/", response_model=CaseRead)
async def create_case(payload: CaseCreate):
    obj = await case_service.create_case(payload.model_dump())
    return obj


@router.put("/{case_id}", response_model=CaseRead)
async def update_case(case_id: int, payload: CaseUpdate):
    obj = await case_service.update_case(case_id, payload.model_dump(exclude_unset=True))
    if not obj:
        raise HTTPException(404, "Case not found")
    return obj


@router.delete("/{case_id}")
async def delete_case(case_id: int):
    ok = await case_service.delete_case(case_id)
    if not ok:
        raise HTTPException(404, "Case not found")
    return {"ok": True}

