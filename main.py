from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId  # Pour travailler avec ObjectId
from typing import List, Optional

app = FastAPI()

# Connexion MongoDB
MONGO_URI = "mongodb+srv://rami2000:0000rami@cluster0.ey222.mongodb.net/"
client = AsyncIOMotorClient(MONGO_URI)
db = client["test"]

# Modèles Pydantic
class User(BaseModel):
    name: str
    email: str
    password: str
    role: str

class Chambre(BaseModel):
    typeChambre: str
    imageChambre: List[str]
    hotel_id: str
    

class Hotel(BaseModel):
    nomHotel: str
    imageHotel:List[str]
    adresse: str
    classement: int
    chambres: Optional[List[Chambre]] = []
    description:List[str]
    paye_id: str
    

class Offre(BaseModel):
    prixParNuit: float
    promotion: float

class Reservation(BaseModel):
    dateReservation: str
    montantTotal: float
    destination: str
    description: str
    placesDisponibles: int
    dateDepart: str
    dateRetour: str
    typeReservation: str
    prix: float

class Avis(BaseModel):
    note: int
    commentaire: str
    dateAvis: str
    user_id: str

class Paye(BaseModel):
    nompaye: str
    imagepaye: str
  
    


# Middleware CORS pour permettre l'accès depuis Angular (http://localhost:4200)
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:4200",  # URL de votre application Angular
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Autoriser les origines
    allow_credentials=True,
    allow_methods=["*"],  # Autoriser toutes les méthodes
    allow_headers=["*"],  # Autoriser tous les en-têtes
)

# Routes CRUD

# Users
@app.post("/users/", response_model=dict)
async def create_user(user: User):
    result = await db.users.insert_one(user.dict())
    return {"id": str(result.inserted_id)}

@app.get("/users/", response_model=List[User])
async def get_users():
    users = await db.users.find().to_list(100)
    return users
@app.post("/payes/", response_model=dict)
async def create_paye(paye: Paye):
    result = await db.payes.insert_one(paye.dict())
    return {"id": str(result.inserted_id)}

@app.get("/payes/", response_model=List[Paye])
async def get_payes():
    payes = await db.payes.find().to_list(100)
    return payes


# Hotels
@app.post("/hotels/", response_model=dict)
async def create_hotel(hotel: Hotel):
    Paye = await db.payes.find_one({"_id": ObjectId(hotel.paye_id)})
    if not Paye:
        raise HTTPException(status_code=404, detail="paye not found")
    result = await db.hotels.insert_one(hotel.dict())
    return {"id": str(result.inserted_id)}

@app.get("/hotels/", response_model=List[Hotel])
async def get_hotels():
    hotels = await db.hotels.find().to_list(100)
    return hotels

@app.get("/hotels/{hotel_id}/", response_model=Hotel)
async def get_hotel_with_chambres(hotel_id: str):
    hotel = await db.hotels.find_one({"_id": ObjectId(hotel_id)})  # Utilisation de ObjectId pour la recherche
    if hotel:
        chambres = await db.chambres.find({"hotel_id": hotel_id}).to_list(100)
        hotel["chambres"] = chambres
        return hotel
    raise HTTPException(status_code=404, detail="Hotel not found")

# Chambres
@app.post("/chambres/", response_model=dict)
async def create_chambre(chambre: Chambre):
    hotel_id = chambre.hotel_id
    hotel = await db.hotels.find_one({"_id": ObjectId(hotel_id)})

    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    
    result = await db.chambres.insert_one(chambre.dict())

    update_result = await db.hotels.update_one(
        {"_id": ObjectId(hotel_id)},
        {"$push": {"chambres": chambre.dict()}}
    )
    return {"id": str(result.inserted_id)}

@app.get("/chambres/", response_model=List[Chambre])
async def get_chambres():
    chambres = await db.chambres.find().to_list(100)
    return chambres

# Offres
@app.post("/offres/", response_model=dict)
async def create_offre(offre: Offre):
    result = await db.offres.insert_one(offre.dict())
    return {"id": str(result.inserted_id)}

@app.get("/offres/", response_model=List[Offre])
async def get_offres():
    offres = await db.offres.find().to_list(100)
    return offres

# Réservations
@app.post("/reservations/", response_model=dict)
async def create_reservation(reservation: Reservation):
    result = await db.reservations.insert_one(reservation.dict())
    return {"id": str(result.inserted_id)}

@app.get("/reservations/", response_model=List[Reservation])
async def get_reservations():
    reservations = await db.reservations.find().to_list(100)
    return reservations

# Avis
@app.post("/avis/", response_model=dict)
async def create_avis(avis: Avis):
    user = await db.users.find_one({"_id": ObjectId(avis.user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    result = await db.avis.insert_one(avis.dict())
    return {"id": str(result.inserted_id)}

@app.get("/avis/", response_model=List[Avis])
async def get_avis():
    avis = await db.avis.find().to_list(100)
    return avis
