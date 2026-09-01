from uuid import UUID

from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.Products_Services import (
    add_product_service,
    list_product_services,
    edit_product_services,
    delete_product_services,
    search_product_name,
)
from app.schemas.Products import ProductCreate
from app.core.limiter import limiter

router = APIRouter(prefix="/Product", tags=["Product"])


@router.post("/add-product")
@limiter.limit("10/minute")
def add_product(
    request: Request, Product: ProductCreate, db: Session = Depends(get_db)
):
    return add_product_service(db, Product)


@router.get("/list-product")
@limiter.limit("10/minute")
def list_product(request: Request, db: Session = Depends(get_db)):
    return list_product_services(db)


@router.put("/edit-product")
@limiter.limit("10/minute")
def edit_product(
    request: Request,
    product_id: UUID,
    product: ProductCreate,
    db: Session = Depends(get_db),
):
    edited_product = edit_product_services(db, product_id, product)

    return edited_product


@router.delete("/delete-product")
@limiter.limit("10/minute")
def delete_product(request: Request, product_id: UUID, db: Session = Depends(get_db)):
    product = delete_product_services(db, product_id)

    return product


@router.get("/search-product")
@limiter.limit("10/minute")
def get_product(request: Request, name: str, db: Session = Depends(get_db)):
    return search_product_name(db, name)
