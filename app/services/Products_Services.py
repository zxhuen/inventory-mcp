from uuid import UUID

from sqlalchemy.orm import Session
from app.Repository.Product_Repo import (
    get_products_repo,
    edit_product_repo,
    delete_product_repo,
)
from app.schemas import PersonCreate
from fastapi import HTTPException
import logging
from app.models.Products import Product
from app.schemas.Products import ProductCreate

logger = logging.getLogger(__name__)


def add_product_service(db: Session, create: ProductCreate):
    try:
        product = Product(
            name=create.name,
            description=create.description,
            price=create.price,
            stock=create.stock,
        )

        db.add(product)
        db.commit()
        db.refresh(product)

        return product

    except Exception:
        logger.exception("Failed to create person")
        db.rollback()
        raise


def list_product_services(db: Session):
    logger.info("Fetching all persons")

    try:
        products = get_products_repo(db)
        logger.info("Retrieved %d person(s)", len(products))
        return products

    except Exception:
        logger.exception("Failed to retrieve persons")
        raise


def edit_product_services(db: Session, product_id: UUID, edit_product: ProductCreate):
    try:
        with db.begin():
            product = edit_product_repo(db, product_id)

            if product is None:
                raise HTTPException(status_code=404, detail="no product found")

            product.name = edit_product.name
            product.description = edit_product.description
            product.price = edit_product.price
            product.stock = edit_product.stock

        db.refresh(product)

        return product

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise


def delete_product_services(db: Session, product_id: UUID):

    try:
        product = delete_product_repo(db, product_id)

        if product is None:
            raise HTTPException(status_code=404, detail="no product found")

        db.delete(product)
        db.commit()

        return product

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise


def search_product_name(db: Session, name: str):
    try:
        products = get_products_repo(db)
        if products is None:
            raise HTTPException(status_code=401, detail="no product found")
        return products

    except Exception:
        raise
