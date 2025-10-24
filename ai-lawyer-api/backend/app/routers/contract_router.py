from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from ..models.contract_model import Contract
from ..schemas.contract_schema import ContractCreate, ContractUpdate, ContractRead
from ..deps import db_dep
from ..common.pagination import Paginated, PageMeta
from ..common.params import PageParams
from ..services.contract_service import list_contracts_service

router = APIRouter(prefix="/contracts", tags=["Contract"])

@router.get("/", response_model=Paginated[ContractRead])
def list_contracts(
    page_params: PageParams = Depends(),
    customer: str | None = Query(None, description="客户名称(模糊)"),
    type_: str | None = Query(None, alias="type", description="合同类型"),
    status: str | None = Query(None, description="状态"),
    upload_date_from: str | None = Query(None, description="上传日期(起) YYYY-MM-DD"),
    upload_date_to: str | None = Query(None, description="上传日期(止) YYYY-MM-DD"),
    db: Session = Depends(db_dep),
):
    items, total = list_contracts_service(
        db, customer=customer, type_=type_, status=status,
        upload_date_from=upload_date_from, upload_date_to=upload_date_to,
        page=page_params.page, page_size=page_params.page_size
    )
    return {"meta": PageMeta(total=total, page=page_params.page, page_size=page_params.page_size), "items": items}

@router.get("/{contract_id}", response_model=ContractRead)
def get_contract(contract_id: int, db: Session = Depends(db_dep)):
    obj = db.get(Contract, contract_id)
    if not obj:
        raise HTTPException(404, "Contract not found")
    return obj

@router.post("/", response_model=ContractRead)
def create_contract(payload: ContractCreate, db: Session = Depends(db_dep)):
    obj = Contract(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.put("/{contract_id}", response_model=ContractRead)
def update_contract(contract_id: int, payload: ContractUpdate, db: Session = Depends(db_dep)):
    obj = db.get(Contract, contract_id)
    if not obj:
        raise HTTPException(404, "Contract not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{contract_id}")
def delete_contract(contract_id: int, db: Session = Depends(db_dep)):
    obj = db.get(Contract, contract_id)
    if not obj:
        raise HTTPException(404, "Contract not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}
