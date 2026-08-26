from sqlalchemy.orm import Session
from app.Repository import (
    create_person_repo,
    get_person_repo,
    edit_person_repo,
    delete_person_repo,
)
from app.schemas import PersonCreate
from fastapi import HTTPException
import logging
from app.models.Products import Product

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


def list_person_services(db: Session):
    logger.info("Fetching all persons")

    try:
        persons = get_person_repo(db)
        logger.info("Retrieved %d person(s)", len(persons))
        return persons

    except Exception:
        logger.exception("Failed to retrieve persons")
        raise


def edit_person_services(db: Session, person_id: int, edit_person: PersonCreate):
    logger.info("Updating person with ID=%s", person_id)

    try:
        person = edit_person_repo(db, person_id, edit_person)

        if person is None:
            logger.warning("Person with ID=%s not found", person_id)
            raise HTTPException(status_code=404, detail="no person found")

        person.last_name = edit_person.last_name
        person.first_name = edit_person.first_name
        person.middle_name = edit_person.middle_name
        person.age = edit_person.age

        db.commit()
        db.refresh(person)

        logger.info("Successfully updated person with ID=%s", person_id)
        return person

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
