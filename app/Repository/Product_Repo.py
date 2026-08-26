from sqlalchemy.orm import Session
from app.models.Person import Person
from app.models.Products import Product
from app.schemas.Person import PersonCreate, PersonResponse


def get_products_repo(db: Session):
    return db.query(Product).all()


def edit_product_repo(db: Session, person_id: int, person: PersonCreate):
    person_from_db = db.query(Person).filter(Person.id == person_id).first()
    return person_from_db


def delete_product_repo(db: Session, person_id: int):
    person = db.query(Person).filter(Person.id == person_id).first()

    return person
