#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from sqlmodel import create_engine, text

load_dotenv()

engine = create_engine(os.getenv("SQL_KEY"), echo=True)

print("🔧 Adding stripe_customer_id column to user table...")

try:
    with engine.connect() as connection:
        # Add the new column
        connection.execute(text("""
            ALTER TABLE "user" 
            ADD COLUMN stripe_customer_id VARCHAR NULL;
        """))
        connection.commit()
    
    print("✅ Successfully added stripe_customer_id column!")
    print("✅ Existing users preserved with NULL stripe_customer_id")
    
except Exception as e:
    if "already exists" in str(e).lower():
        print("⚠️  Column already exists!")
    else:
        print(f"❌ Error: {e}")
        print("💡 Try Option 1 (drop/recreate) if this fails") 