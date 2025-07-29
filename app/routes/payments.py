
import stripe, os
from fastapi import APIRouter, HTTPException, Request
from dotenv import load_dotenv
from app.models import User, Feedback
from app.database import engine
from sqlmodel import Session
from pydantic import BaseModel

load_dotenv()
stripe.api_key = os.getenv("STRIPE_API_KEY")
payments_router = APIRouter()

class FeedbackInput(BaseModel):
    name: str
    email: str
    feedback: str

@payments_router.post("/checkout/{user_id}")
def create_checkout(user_id: int, tier: str = "pro"):
    try:
        if tier == "pro":
            price = 500
            limit = 30
        elif tier == "unlimited":
            price = 1000
            limit = 300
        else:
            raise HTTPException(status_code=400, detail="Invalid tier")
        session = stripe.checkout.Session.create(
            payment_method_types = ["card"],
            mode = "payment",
            line_items = [{
                "price_data": {
                    "currency": "usd",
                    "unit_amount": price,
                    "product_data": {
                        "name": f"{tier.capitalize()} Plan- {limit} Posts/Month",
                    },
                }, 
                "quantity": 1,
            }],
            metadata={"user_id": str(user_id), "tier": tier},
            success_url=os.getenv("STRIPE_SUCCESS_URL"),
            cancel_url=os.getenv("STRIPE_CANCEL_URL"),
        )
        return {"checkout_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@payments_router.post("/webhook")
async def stripe_webhook(request: Request):
    print("📩 Stripe webhook received")

    try:
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        secret = os.getenv("STRIPE_WEBHOOK_SECRET")

        event = stripe.Webhook.construct_event(payload, sig_header, secret)
        print(f"✅ Stripe event type: {event['type']} — ID: {event['id']}")

    except Exception as e:
        print(f"❌ CRASH inside webhook: {e}")
        raise HTTPException(status_code=400, detail=f"Webhook error: {str(e)}")

    if event["type"] == "checkout.session.completed":
        session_obj = event["data"]["object"]
        user_id = session_obj["metadata"].get("user_id")
        tier = session_obj["metadata"].get("tier")

        print(f"➡️ Upgrading user {user_id} to {tier}...")

        with Session(engine) as session:
            user = session.get(User, int(user_id))  
            if user:
                user.tier = tier
                session.add(user)
                session.commit()
                print(f"✅ User {user_id} upgraded to {tier}")
        
    return {"status": "success"}

@payments_router.post("/feedback")
def feedback(feedback_input: FeedbackInput):
    with Session(engine) as session:
        try:
            feedback = Feedback(
                name=feedback_input.name,
                email=feedback_input.email,
                feedback=feedback_input.feedback
            )
            session.add(feedback)
            session.commit()
            session.refresh(feedback)
            return {"status": "success", "id": feedback.id}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

