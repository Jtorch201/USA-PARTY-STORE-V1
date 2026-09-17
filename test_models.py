"""
Quick manual check that the models work end-to-end:
add items, place an order (one delivery, one pickup), query it back.

Not a formal test suite yet -- just a sanity check for step 2.
"""

from datetime import date, datetime

from database import SessionLocal, init_db
from models import Item, Order, OrderItem, ItemType, FulfillmentType, OrderStatus

init_db()
session = SessionLocal()

# --- Add some items ---
chair = Item(name="Folding Chair - White", type=ItemType.CHAIR, price_per_day=1.50, quantity_available=200)
table = Item(name="6ft Rectangular Table", type=ItemType.TABLE, price_per_day=12.00, quantity_available=30)
session.add_all([chair, table])
session.commit()

print("Items in store:")
for item in session.query(Item).all():
    print(" ", item)

# --- Place a delivery order ---
delivery_order = Order(
    customer_name="Jane Doe",
    contact_info="555-123-4567",
    event_date=date(2026, 10, 3),
    fulfillment_type=FulfillmentType.DELIVERY,
    dropoff_time=datetime(2026, 10, 3, 9, 0),
    pickup_by_time=datetime(2026, 10, 3, 20, 0),
    status=OrderStatus.CONFIRMED,
)
session.add(delivery_order)
session.commit()

session.add_all([
    OrderItem(order_id=delivery_order.id, item_id=chair.id, quantity=50),
    OrderItem(order_id=delivery_order.id, item_id=table.id, quantity=6),
])
session.commit()

# --- Place a self-pickup order ---
pickup_order = Order(
    customer_name="Marcus Lee",
    contact_info="marcus@example.com",
    event_date=date(2026, 10, 5),
    fulfillment_type=FulfillmentType.PICKUP,
    pickup_time=datetime(2026, 10, 5, 14, 30),
    status=OrderStatus.PENDING,
)
session.add(pickup_order)
session.commit()

session.add(OrderItem(order_id=pickup_order.id, item_id=chair.id, quantity=20))
session.commit()

# --- Query it all back ---
print("\nAll orders:")
for order in session.query(Order).all():
    print(" ", order)
    for oi in order.order_items:
        print("     -", oi.quantity, "x", oi.item.name)
    if order.fulfillment_type == FulfillmentType.PICKUP:
        print("     customer arriving at:", order.pickup_time.strftime("%b %d, %Y %I:%M %p"))
    else:
        print(
            "     dropoff:", order.dropoff_time.strftime("%b %d, %Y %I:%M %p"),
            "| pickup-by:", order.pickup_by_time.strftime("%b %d, %Y %I:%M %p"),
        )

session.close()
