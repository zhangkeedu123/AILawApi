from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from ..models.spider_model import SpiderCustomer
from ..schemas.spider_schema import SpiderCreate, SpiderUpdate, SpiderRead
from ..deps import db_dep
from ..common.pagination import Paginated, PageMeta
from ..common.params import PageParams
from ..services.spider_service import list_spider_customers_service

router = APIRouter(prefix="/spider-customers", tags=["SpiderCustomer"])

@router.get("/", response_model=Paginated[SpiderRead])
def list_spider_customers(
    page_params: PageParams = Depends(),
    name: str | None = Query(None, description="姓名/公司名(模糊)"),
    city: str | None = Query(None, description="城市(模糊)"),
    platform: str | None = Query(None, description="平台"),
    status: str | None = Query(None, description="状态"),
    db: Session = Depends(db_dep),
):
    items, total = list_spider_customers_service(
        db, name=name, city=city, platform=platform, status=status,
        page=page_params.page, page_size=page_params.page_size
    )
    return {"meta": PageMeta(total=total, page=page_params.page, page_size=page_params.page_size), "items": items}

@router.get("/{item_id}", response_model=SpiderRead)
def get_spider_customer(item_id: int, db: Session = Depends(db_dep)):
    obj = db.get(SpiderCustomer, item_id)
    if not obj:
        raise HTTPException(404, "SpiderCustomer not found")
    return obj

@router.post("/", response_model=SpiderRead)
def create_spider_customer(payload: SpiderCreate, db: Session = Depends(db_dep)):
    obj = SpiderCustomer(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.put("/{item_id}", response_model=SpiderRead)
def update_spider_customer(item_id: int, payload: SpiderUpdate, db: Session = Depends(db_dep)):
    obj = db.get(SpiderCustomer, item_id)
    if not obj:
        raise HTTPException(404, "SpiderCustomer not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{item_id}")
def delete_spider_customer(item_id: int, db: Session = Depends(db_dep)):
    obj = db.get(SpiderCustomer, item_id)
    if not obj:
        raise HTTPException(404, "SpiderCustomer not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}
