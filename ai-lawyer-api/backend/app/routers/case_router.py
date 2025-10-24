from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from ..models.case_model import Case
from ..schemas.case_schema import CaseCreate, CaseUpdate, CaseRead
from ..deps import db_dep
from ..common.pagination import Paginated, PageMeta
from ..common.params import PageParams
from ..services.case_service import list_cases_service

router = APIRouter(prefix="/cases", tags=["Case"])

@router.get("/", response_model=Paginated[CaseRead])
def list_cases(
    page_params: PageParams = Depends(),
    name: str | None = Query(None, description="案件名称(模糊)"),
    status: str | None = Query(None, description="案件状态"),
    location: str | None = Query(None, description="地点(模糊)"),
    plaintiff: str | None = Query(None, description="原告(模糊)"),
    defendant: str | None = Query(None, description="被告(模糊)"),
    db: Session = Depends(db_dep),
):
    items, total = list_cases_service(
        db, name=name, status=status, location=location, plaintiff=plaintiff, defendant=defendant,
        page=page_params.page, page_size=page_params.page_size
    )
    return {"meta": PageMeta(total=total, page=page_params.page, page_size=page_params.page_size), "items": items}

@router.get("/{case_id}", response_model=CaseRead)
def get_case(case_id: int, db: Session = Depends(db_dep)):
    obj = db.get(Case, case_id)
    if not obj:
        raise HTTPException(404, "Case not found")
    return obj

@router.post("/", response_model=CaseRead)
def create_case(payload: CaseCreate, db: Session = Depends(db_dep)):
    obj = Case(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.put("/{case_id}", response_model=CaseRead)
def update_case(case_id: int, payload: CaseUpdate, db: Session = Depends(db_dep)):
    obj = db.get(Case, case_id)
    if not obj:
        raise HTTPException(404, "Case not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{case_id}")
def delete_case(case_id: int, db: Session = Depends(db_dep)):
    obj = db.get(Case, case_id)
    if not obj:
        raise HTTPException(404, "Case not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}
