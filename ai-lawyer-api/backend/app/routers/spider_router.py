from fastapi import APIRouter, HTTPException, Depends, Query
from ..schemas.spider_schema import SpiderCreate, SpiderUpdate, SpiderRead
from ..common.pagination import Paginated, PageMeta
from ..common.params import PageParams
from ..services import spider_service

router = APIRouter(prefix="/spider-customers", tags=["SpiderCustomer"])


@router.get("/", response_model=Paginated[SpiderRead])
async def list_spider_customers(
    page_params: PageParams = Depends(),
    name: str | None = Query(None, description="姓名/公司(模糊)"),
    city: str | None = Query(None, description="城市(模糊)"),
    platform: str | None = Query(None, description="平台"),
    status: str | None = Query(None, description="状态"),
):
    items, total = await spider_service.list_spider_customers_service(
        name=name, city=city, platform=platform, status=status,
        page=page_params.page, page_size=page_params.page_size,
    )
    return {"meta": PageMeta(total=total, page=page_params.page, page_size=page_params.page_size), "items": items}


@router.get("/{item_id}", response_model=SpiderRead)
async def get_spider_customer(item_id: int):
    obj = await spider_service.get_spider_customer_by_id(item_id)
    if not obj:
        raise HTTPException(404, "SpiderCustomer not found")
    return obj


@router.post("/", response_model=SpiderRead)
async def create_spider_customer(payload: SpiderCreate):
    obj = await spider_service.create_spider_customer(payload.model_dump())
    return obj


@router.put("/{item_id}", response_model=SpiderRead)
async def update_spider_customer(item_id: int, payload: SpiderUpdate):
    obj = await spider_service.update_spider_customer(item_id, payload.model_dump(exclude_unset=True))
    if not obj:
        raise HTTPException(404, "SpiderCustomer not found")
    return obj


@router.delete("/{item_id}")
async def delete_spider_customer(item_id: int):
    ok = await spider_service.delete_spider_customer(item_id)
    if not ok:
        raise HTTPException(404, "SpiderCustomer not found")
    return {"ok": True}

