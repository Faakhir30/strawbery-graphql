from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schemas.trip import TripCreate, TripUpdate

async def get_trip_by_id(db: AsyncIOMotorDatabase, trip_id: str):
    trip = await db["trips"].find_one({"_id": ObjectId(trip_id)})
    if trip:
        trip["_id"] = str(trip["_id"])
        return trip
    raise HTTPException(status_code=404, detail="Trip not found")

async def create_trip(db: AsyncIOMotorDatabase, trip_data: TripCreate, user_id: str):
    trip = trip_data.dict()
    trip["user_id"] = user_id
    trip["created_date"] = datetime.combine(datetime.now().date(), datetime.min.time())

    # Convert date fields to datetime
    trip["start_date"] = datetime.combine(trip_data.start_date, datetime.min.time())
    trip["end_date"] = datetime.combine(trip_data.end_date, datetime.min.time())

    result = await db["trips"].insert_one(trip)
    new_trip = await db["trips"].find_one({"_id": result.inserted_id})
    if new_trip:
        new_trip["_id"] = str(new_trip["_id"])
    return new_trip



async def update_trip(db: AsyncIOMotorDatabase, trip_id: str, trip_data: TripUpdate):
    update_data = trip_data.dict(exclude_unset=True)
    result = await db["trips"].update_one({"_id": ObjectId(trip_id)}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Trip not found")
    updated_trip = await db["trips"].find_one({"_id": ObjectId(trip_id)})
    updated_trip["_id"] = str(updated_trip["_id"])
    return updated_trip

async def delete_trip(db: AsyncIOMotorDatabase, trip_id: str):
    result = await db["trips"].delete_one({"_id": ObjectId(trip_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Trip not found")
    return {"message": "Trip deleted successfully"}
