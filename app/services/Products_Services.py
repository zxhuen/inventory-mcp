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


def add_product_service(db: Session, create: PersonCreate):
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


def edit_person_services(db: Session, person_id: int, edit_product: ProductCreate):
    try:
        product = edit_product_repo(db, person_id)

        if product is None:
            raise HTTPException(status_code=404, detail="no product found")

        product.name = edit_product.name
        product.description = edit_product.description
        product.price = edit_product.price
        product.stock = edit_product.stock

        db.commit()
        db.refresh(product)

        return product

    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to update person with ID=%s", person_id)
        db.rollback()
        raise


def delete_person_services(db: Session, person_id: int):
    logger.info("Deleting person with ID=%s", person_id)

    try:
        person = delete_person_repo(db, person_id)

        if person is None:
            logger.warning("Person with ID=%s not found", person_id)
            raise HTTPException(status_code=404, detail="no person found")

        db.delete(person)
        db.commit()

        logger.info("Successfully deleted person with ID=%s", person_id)
        return person

    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to delete person with ID=%s", person_id)
        db.rollback()
        raise
