from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Location(BaseModel):
    lat: float
    lon: float
    name: str

@app.get("/locations", response_model=List[Location])
def get_locations():
    return [
        {"lat": 45.5236, "lon": -122.6750, "name": "Portland, OR"},
        {"lat": 45.5316, "lon": -122.6850, "name": "Location 2"},
        {"lat": 45.5416, "lon": -122.6950, "name": "Location 3"}
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
