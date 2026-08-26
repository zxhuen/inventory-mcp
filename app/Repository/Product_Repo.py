from uuid import UUID

from sqlalchemy.orm import Session
from app.models.Person import Person
from app.models.Products import Product
from app.schemas.Person import PersonCreate, PersonResponse
from app.schemas.Products import ProductCreate


def get_products_repo(db: Session):
    return db.query(Product).all()


def edit_product_repo(db: Session, product_id: UUID):
    product_from_db = db.query(Product).filter(Product.id == product_id).first()
    return product_from_db


def delete_product_repo(db: Session, person_id: int):
    person = db.query(Person).filter(Person.id == person_id).first()

    return person
