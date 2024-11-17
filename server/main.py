from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional


from utils import tokenizer, qdrant


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/search")
def search(
    query: str,
    category: Optional[str] = None,
    brand_name: Optional[str] = None,
    status: Optional[str] = None,
    gender: Optional[str] = None,
    price_from: Optional[float] = None,
    price_to: Optional[float] = None,
    region: Optional[str] = None,
):
    try:
        query_vector = tokenizer.get_text_vector(query)
        results = qdrant.search(
            query_vector,
            category=category,
            brand_name=brand_name,
            status=status,
            gender=gender,
            price_from=price_from,
            price_to=price_to,
            region=region,
        )
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/categories")
def get_categories():
    return {"categories": qdrant.get_all_possible_values("category_name")}


@app.get("/brands")
def get_brand_names():
    return {"brands": qdrant.get_all_possible_values("brand_name")}


@app.get("/genders")
def get_genders():
    return {"genders": qdrant.get_all_possible_values("gender")}


@app.get("/statuses")
def get_statuses():
    return {"statuses": qdrant.get_all_possible_values("status")}


@app.get("/regions")
def get_regions():
    return {"regions": qdrant.get_all_possible_values("region")}
