from uuid import UUID
from decimal import Decimal

from app.services.Products_Services import (
    add_product_service,
    list_product_services,
    edit_product_services,
    delete_product_services,
    search_product_name,
)

from app.schemas.Products import ProductCreate
from app.core.database import SessionLocal

from mcp.server.fastmcp import FastMCP


def register_product_tools(mcp: FastMCP):

    @mcp.tool()
    def add_product(
        name: str,
        description: str,
        price: float,
        stock: int,
    ):
        """
        Add a new product to the inventory.

        Args:
            name: Product name.
            description: Product description.
            price: Product price.
            stock: Number of products currently in stock.
        """

        db = SessionLocal()

        try:
            product_data = ProductCreate(
                name=name,
                description=description,
                price=Decimal(str(price)),
                stock=stock,
            )

            product = add_product_service(db, product_data)

            return {
                "id": str(product.id),
                "name": product.name,
                "description": product.description,
                "price": str(product.price),
                "stock": product.stock,
            }

        finally:
            db.close()

    @mcp.tool()
    def list_products():
        """
        Get all products in the inventory.
        """

        db = SessionLocal()

        try:
            products = list_product_services(db)

            return [
                {
                    "id": str(product.id),
                    "name": product.name,
                    "description": product.description,
                    "price": str(product.price),
                    "stock": product.stock,
                }
                for product in products
            ]

        finally:
            db.close()

    @mcp.tool()
    def edit_product(
        product_id: str,
        name: str,
        description: str,
        price: float,
        stock: int,
    ):
        """
        Edit an existing product.

        Args:
            product_id: UUID of the product to edit.
            name: New product name.
            description: New product description.
            price: New product price.
            stock: New stock quantity.
        """

        db = SessionLocal()

        try:
            product_data = ProductCreate(
                name=name,
                description=description,
                price=Decimal(str(price)),
                stock=stock,
            )

            product = edit_product_services(
                db,
                UUID(product_id),
                product_data,
            )

            return {
                "id": str(product.id),
                "name": product.name,
                "description": product.description,
                "price": str(product.price),
                "stock": product.stock,
            }

        finally:
            db.close()

    @mcp.tool()
    def delete_product(product_id: str):
        """
        Delete a product from the inventory.

        Args:
            product_id: UUID of the product to delete.
        """

        db = SessionLocal()

        try:
            product = delete_product_services(
                db,
                UUID(product_id),
            )

            return {
                "success": True,
                "deleted_product": {
                    "id": str(product.id),
                    "name": product.name,
                },
            }

        finally:
            db.close()

    @mcp.tool()
    def lookup_product_by_name(name: str):
        """
        STRICTLY FOR name-based product lookup only.

        Use this tool only when the user explicitly asks to find a product by
        name, partial name, or search for a specific matching product.

        IMPORTANT: Do NOT use this tool when the user asks to add, create,
        update, delete, or list products. If the request includes add/update/
        delete intent, do not call this tool even if the message includes a
        product name.

        Args:
            name: The exact or partial product name to look up.
        """

        db = SessionLocal()

        try:
            products = search_product_name(db, name)

            return [
                {
                    "id": str(product.id),
                    "name": product.name,
                    "description": product.description,
                    "price": str(product.price),
                    "stock": product.stock,
                }
                for product in products
            ]

        finally:
            db.close()
