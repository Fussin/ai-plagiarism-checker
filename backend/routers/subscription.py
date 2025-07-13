from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
import stripe

from backend import models
from backend.database import get_db
from backend.dependencies import get_current_active_user
from backend.config import settings

# Configure Stripe with API key
if settings.STRIPE_API_KEY:
    stripe.api_key = settings.STRIPE_API_KEY
else:
    print("WARNING: STRIPE_API_KEY is not set. Stripe integration will not work.")

router = APIRouter(
    prefix="/api", # Using /api prefix as requested
    tags=["subscription"],
    dependencies=[Depends(get_current_active_user)]
)

# Pydantic model for the request body
class SubscriptionRequest(models.BaseModel):
    plan: str # e.g., "pro_basic" or "pro_advanced"

@router.post("/subscribe")
async def create_checkout_session(
    request: SubscriptionRequest,
    db: Session = Depends(get_db),
    current_user: models.UserDB = Depends(get_current_active_user)
):
    """
    Creates a Stripe Checkout session for a user to subscribe to a new plan.
    """
    if not stripe.api_key:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Payment service is not configured.")

    plan_price_ids = {
        "pro_basic": settings.STRIPE_PRICE_ID_PRO_BASIC,
        "pro_advanced": settings.STRIPE_PRICE_ID_PRO_ADVANCED
    }

    price_id = plan_price_ids.get(request.plan)
    if not price_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid plan specified.")

    # Get or create a Stripe customer
    customer_id = current_user.stripe_customer_id
    if not customer_id:
        try:
            customer = stripe.Customer.create(
                email=current_user.email,
                name=f"User {current_user.id}",
            )
            customer_id = customer.id
            # Save the new customer ID to our database
            current_user.stripe_customer_id = customer_id
            db.commit()
            db.refresh(current_user)
            print(f"Created new Stripe customer {customer_id} for user {current_user.email}")
        except Exception as e:
            print(f"Error creating Stripe customer: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create payment profile.")

    try:
        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[
                {
                    'price': price_id,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=f"{settings.FRONTEND_URL}/subscribe/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/subscribe/cancel",
            # Pass our internal user ID to the session so we can identify the user in webhooks
            metadata={
                'user_id': current_user.id
            }
        )
        return {"checkout_url": checkout_session.url}
    except Exception as e:
        print(f"Error creating Stripe checkout session: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not initiate payment session.")


# This endpoint needs to be public to receive webhooks from Stripe
# We remove the global dependency for this specific route.
@router.post("/webhooks/stripe", include_in_schema=False)
async def stripe_webhook(
    request: Request, # We need the raw request to verify the signature
    db: Session = Depends(get_db)
):
    if not settings.STRIPE_WEBHOOK_SECRET:
        print("ERROR: STRIPE_WEBHOOK_SECRET is not set. Cannot process webhooks.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Webhook service is not configured.")

    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    try:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=sig_header, secret=settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid payload: {e}")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid signature: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Webhook error: {e}")

    # Handle the event
    event_type = event['type']
    data_object = event['data']['object']

    print(f"Received Stripe webhook event: {event_type}")

    if event_type == 'checkout.session.completed':
        session = data_object
        user_id = session.get('metadata', {}).get('user_id')
        if not user_id:
            print(f"Webhook Error: user_id not found in checkout.session.completed metadata. Session ID: {session.id}")
            return {"status": "error", "reason": "user_id missing from metadata"}

        # This event contains the subscription details. We can use these to update our DB.
        # It's often recommended to listen for `customer.subscription.created/updated` instead,
        # as that's the more direct source of truth for the subscription status.
        # But for simplicity, we'll handle the plan update here.

        # Retrieve the line items to find out which plan was purchased
        try:
            line_items = stripe.checkout.Session.list_line_items(session.id, limit=1)
            price_id = line_items.data[0].price.id

            # Find the plan name associated with this price ID
            new_plan = None
            if price_id == settings.STRIPE_PRICE_ID_PRO_BASIC:
                new_plan = "pro_basic"
            elif price_id == settings.STRIPE_PRICE_ID_PRO_ADVANCED:
                new_plan = "pro_advanced"

            if new_plan:
                user = db.query(models.UserDB).filter(models.UserDB.id == int(user_id)).first()
                if user:
                    user.plan = new_plan
                    user.subscription_status = 'active'
                    # Reset usage upon upgrade
                    usage = usage_service.get_or_create_usage_record(db, user)
                    usage.words_scanned = 0
                    usage.humanizer_uses = 0
                    usage.last_reset = datetime.now(timezone.utc)
                    db.commit()
                    print(f"User {user.email} (ID: {user_id}) plan successfully updated to {new_plan}.")
                else:
                    print(f"Webhook Error: User with ID {user_id} not found in database.")
            else:
                print(f"Webhook Warning: No plan configured for price ID {price_id}.")

        except Exception as e:
            print(f"Error processing checkout.session.completed webhook: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error processing webhook.")


    elif event_type in ['customer.subscription.updated', 'customer.subscription.deleted']:
        subscription = data_object
        customer_id = subscription['customer']

        user = db.query(models.UserDB).filter(models.UserDB.stripe_customer_id == customer_id).first()
        if not user:
            print(f"Webhook Error: User with Stripe customer ID {customer_id} not found.")
            return {"status": "error", "reason": "user not found"}

        new_status = subscription['status'] # e.g., 'active', 'past_due', 'canceled'
        user.subscription_status = new_status

        if event_type == 'customer.subscription.deleted' or new_status != 'active':
            # Downgrade user to free plan if subscription is cancelled or payment fails
            user.plan = 'free'
            print(f"User {user.email} subscription status updated to {new_status}. Plan downgraded to free.")
        else:
             # Could also handle plan upgrades/downgrades here by checking the price ID
            print(f"User {user.email} subscription status updated to {new_status}.")

        db.commit()

    else:
        print(f"Unhandled event type {event['type']}")

    return {"status": "success"}

# Need to import Request from FastAPI and other modules
from fastapi import Request
from backend.services import usage_service
from datetime import datetime, timezone
