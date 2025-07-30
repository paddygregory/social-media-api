
import stripe, os
from fastapi import APIRouter, HTTPException, Request
from dotenv import load_dotenv
from app.models import User, Feedback
from app.database import engine
from sqlmodel import Session, select
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
            price_id = os.getenv("STRIPE_PRICE_PRO")
            limit = 30
        elif tier == "unlimited":
            price_id = os.getenv("STRIPE_PRICE_UNLIMITED")
            limit = 300
        else:
            raise HTTPException(status_code=400, detail="Invalid tier")

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            line_items=[{
                "price": price_id,
                "quantity": 1
            }],
            metadata={"user_id": str(user_id), "tier": tier},
            success_url=os.getenv("STRIPE_SUCCESS_URL"),
            cancel_url=os.getenv("STRIPE_CANCEL_URL"),
        )
        return {"checkout_url": session.url}
    except Exception as e:
        print(f"❌ CRASH inside create_checkout: {e}")
        raise HTTPException(status_code=500, detail=str(e))
           

@payments_router.post("/billing-portal/{user_id}")
def create_billing_portal(user_id: int):
    try:
        with Session(engine) as session:
            user = session.get(User, user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            
            if not user.stripe_customer_id:
                
                customer = stripe.Customer.create(
                    email=user.email,
                    name=user.name,
                    metadata={"user_id": str(user.id)}
                )
                user.stripe_customer_id = customer.id
                session.add(user)
                session.commit()
            else:
                # Get existing customer
                customer = stripe.Customer.retrieve(user.stripe_customer_id)
            
            
            portal_session = stripe.billing_portal.Session.create(
                customer=customer.id,
                return_url=os.getenv("STRIPE_RETURN_URL", "http://localhost:3000/account")
            )
            
            return {"portal_url": portal_session.url}
            
    except Exception as e:
        print(f"❌ CRASH inside billing portal: {e}")
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
        customer_id = session_obj.get("customer")

        print(f"➡️ Upgrading user {user_id} to {tier}...")

        with Session(engine) as session:
            user = session.get(User, int(user_id))  
            if user:
                user.tier = tier
                user.stripe_customer_id = customer_id
                session.add(user)
                session.commit()
                print(f"✅ User {user_id} upgraded to {tier}")

    elif event["type"] == "customer.subscription.updated":
        subscription = event["data"]["object"]
        customer_id = subscription["customer"]
        
        with Session(engine) as session:
            user = session.exec(select(User).where(User.stripe_customer_id == customer_id)).first()
            if user:
                if subscription["status"] == "canceled":
                    user.tier = "free"
                elif subscription["status"] == "active":
                    
                    pass
                session.add(user)
                session.commit()
                print(f"✅ User {user.id} subscription updated")

    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        customer_id = subscription["customer"]
        
        with Session(engine) as session:
            user = session.exec(select(User).where(User.stripe_customer_id == customer_id)).first()
            if user:
                user.tier = "free"
                session.add(user)
                session.commit()
                print(f"✅ User {user.id} downgraded to free")
        
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
