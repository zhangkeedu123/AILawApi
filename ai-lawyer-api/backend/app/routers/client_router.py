from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from ..models.client_model import Client
from ..schemas.client_schema import ClientCreate, ClientUpdate, ClientRead
from ..deps import db_dep
from ..common.pagination import Paginated, PageMeta
from ..common.params import PageParams
from ..services.client_service import list_clients_service

router = APIRouter(prefix="/clients", tags=["Client"])

@router.get("/", response_model=Paginated[ClientRead])
def list_clients(
    page_params: PageParams = Depends(),
    name: str | None = Query(None, description="客户名称(模糊)"),
    type_: str | None = Query(None, alias="type", description="客户类型"),
    status: str | None = Query(None, description="状态"),
    phone: str | None = Query(None, description="电话(模糊)"),
    email: str | None = Query(None, description="邮箱(模糊)"),
    db: Session = Depends(db_dep),
):
    items, total = list_clients_service(
        db, name=name, type_=type_, status=status, phone=phone, email=email,
        page=page_params.page, page_size=page_params.page_size
    )
    return {"meta": PageMeta(total=total, page=page_params.page, page_size=page_params.page_size), "items": items}

@router.get("/{client_id}", response_model=ClientRead)
def get_client(client_id: int, db: Session = Depends(db_dep)):
    obj = db.get(Client, client_id)
    if not obj:
        raise HTTPException(404, "Client not found")
    return obj

@router.post("/", response_model=ClientRead)
def create_client(payload: ClientCreate, db: Session = Depends(db_dep)):
    obj = Client(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.put("/{client_id}", response_model=ClientRead)
def update_client(client_id: int, payload: ClientUpdate, db: Session = Depends(db_dep)):
    obj = db.get(Client, client_id)
    if not obj:
        raise HTTPException(404, "Client not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{client_id}")
def delete_client(client_id: int, db: Session = Depends(db_dep)):
    obj = db.get(Client, client_id)
    if not obj:
        raise HTTPException(404, "Client not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}
