from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi import FastAPI, HTTPException
import pandas as pd
import os


app = FastAPI(
        title="API Données de Validations de Titre de Transports",
        description="Une API sécurisée par clé pour servir les données de validations de titre de transport en Ile-de-France et de stations/gares."    
)

@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API des données de validation de titre de transport en Ile-de-France !"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Data API"}

"""
products = [
    {
        "id": 1,
        "name": "Laptop",
        "category": "Electronics",
        "price": 999.99,
        "stock": 15
    },
    {
        "id": 2,
        "name": "Coffee Maker",
        "category": "Appliances",
        "price": 79.99,
        "stock": 30
    },
    {
        "id": 3,
        "name": "Desk Chair",
        "category": "Furniture",
        "price": 199.99,
        "stock": 10
    },
    {
        "id": 4,
        "name": "Wireless Mouse",
        "category": "Electronics",
        "price": 29.99,
        "stock": 50
    },
    {
        "id": 5,
        "name": "Notebook",
        "category": "Stationery",
        "price": 5.99,
        "stock": 100
    }
]
"""


def load_products_from_csv(filepath: str = "data/products.csv"):
    products = pd.read_csv(filepath)
    return products.to_dict(orient="records")
# Load products at startup
products = load_products_from_csv()



# Modèle Pydantic pour produit.
class Product(BaseModel):
    id: int
    name: str
    category: str
    price: float
    stock: int


# Endpoint pour récupérer les données.
from typing import Optional

@app.get(
        "/products",
        response_model=dict,
        summary="Get all products",
        description="Retrieve a list of all products. Optionally filter by category using a query parameter."
)
async def get_all_products(category: Optional[str] = None):
    if category:
        filtered_products = [p for p in products if p["category"].lower() == category.lower()]
        return {"products": filtered_products, "count": len(filtered_products)}
    return {"products": products, "count": len(products)}



# Endpoint pour récupérer un élément.
@app.get(
        "/products/{product_id}", 
         response_model=Product,
         summary="Get a specific product",
         description="Retrieve a specific product based on product_id."
)
async def get_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")



# Création d'un Endpoint POST.
@app.post("/products", response_model=Product)
async def create_product(product: Product):
    for existing_product in products:
        if existing_product["id"] == product.id:
            raise HTTPException(status_code=400, detail="Product ID already exists")

    product_dict = product.dict()
    products.append(product_dict)
    return product
