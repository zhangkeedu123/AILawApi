from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from ..models.firm_model import Firm
from ..schemas.firm_schema import FirmCreate, FirmUpdate, FirmRead
from ..deps import db_dep
from ..common.pagination import Paginated, PageMeta
from ..common.params import PageParams
from ..services.firm_service import list_firms_service

router = APIRouter(prefix="/firms", tags=["Firm"])

@router.get("/", response_model=Paginated[FirmRead])
def list_firms(
    page_params: PageParams = Depends(),
    name: str | None = Query(None, description="律所名称(模糊)"),
    city: str | None = Query(None, description="城市(模糊)"),
    status: str | None = Query(None, description="状态"),
    package: str | None = Query(None, description="套餐"),
    db: Session = Depends(db_dep),
):
    items, total = list_firms_service(
        db, name=name, city=city, status=status, package=package,
        page=page_params.page, page_size=page_params.page_size
    )
    return {"meta": PageMeta(total=total, page=page_params.page, page_size=page_params.page_size), "items": items}

@router.get("/{firm_id}", response_model=FirmRead)
def get_firm(firm_id: int, db: Session = Depends(db_dep)):
    obj = db.get(Firm, firm_id)
    if not obj:
        raise HTTPException(404, "Firm not found")
    return obj

@router.post("/", response_model=FirmRead)
def create_firm(payload: FirmCreate, db: Session = Depends(db_dep)):
    obj = Firm(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.put("/{firm_id}", response_model=FirmRead)
def update_firm(firm_id: int, payload: FirmUpdate, db: Session = Depends(db_dep)):
    obj = db.get(Firm, firm_id)
    if not obj:
        raise HTTPException(404, "Firm not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{firm_id}")
def delete_firm(firm_id: int, db: Session = Depends(db_dep)):
    obj = db.get(Firm, firm_id)
    if not obj:
        raise HTTPException(404, "Firm not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}
