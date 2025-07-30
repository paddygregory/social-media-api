#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from sqlmodel import create_engine, SQLModel
from app.models import User

load_dotenv()

engine = create_engine(os.getenv("SQL_KEY"), echo=True)

print("🗑️  Dropping user table...")
# Drop the user table
try:
    SQLModel.metadata.tables["user"].drop(engine)
    print("✅ User table dropped!")
except Exception as e:
    print(f"⚠️  Table might not exist: {e}")

print("🔧 Recreating user table with new schema...")
# Recreate it with the new schema
SQLModel.metadata.create_all(engine)
print("✅ User table recreated with stripe_customer_id field!")

print("⚠️  NOTE: All existing users have been deleted. You'll need to re-register.") 