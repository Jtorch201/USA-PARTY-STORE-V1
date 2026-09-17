"""
Flask routes for the USA Party Store ordering app.

Pages:
  GET  /                -> redirect to /items
  GET  /items            -> browse available chairs/tables
  GET  /order/new         -> order form
  POST /order/new         -> process the submitted order
  GET  /order/<id>        -> confirmation / receipt page
"""

from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, abort
from sqlalchemy.orm import joinedload

from database import SessionLocal, init_db
from models import Item, Order, OrderItem, ItemType, FulfillmentType, OrderStatus

app = Flask(__name__)


@app.template_filter("clock12")
def clock12(dt):
    """Display a datetime in 12-hour format, e.g. 'Oct 03, 2026 09:00 AM'."""
    if dt is None:
        return ""
    return dt.strftime("%b %d, %Y %I:%M %p")


@app.route("/")
def index():
    return redirect(url_for("list_items"))


@app.route("/items")
def list_items():
    session = SessionLocal()
    items = session.query(Item).all()
    session.close()
    return render_template("items.html", items=items)


@app.route("/order/new", methods=["GET"])
def new_order_form():
    session = SessionLocal()
    items = session.query(Item).all()
    session.close()
    return render_template("order_form.html", items=items)


@app.route("/order/new", methods=["POST"])
def create_order():
    session = SessionLocal()

    fulfillment_type = request.form.get("fulfillment_type")  # "delivery" or "pickup"

    order = Order(
        customer_name=request.form.get("customer_name"),
        contact_info=request.form.get("contact_info"),
        event_date=datetime.strptime(request.form.get("event_date"), "%Y-%m-%d").date(),
        fulfillment_type=FulfillmentType(fulfillment_type),
        status=OrderStatus.PENDING,
    )

    if fulfillment_type == "delivery":
        order.dropoff_time = datetime.strptime(request.form.get("dropoff_time"), "%Y-%m-%dT%H:%M")
        order.pickup_by_time = datetime.strptime(request.form.get("pickup_by_time"), "%Y-%m-%dT%H:%M")
    else:
        order.pickup_time = datetime.strptime(request.form.get("pickup_time"), "%Y-%m-%dT%H:%M")

    session.add(order)
    session.commit()  # commit now so order.id is assigned

    # Items: form fields are named like "qty_<item_id>"
    items = session.query(Item).all()
    for item in items:
        qty_raw = request.form.get(f"qty_{item.id}", "0")
        qty = int(qty_raw) if qty_raw.isdigit() else 0
        if qty > 0:
            session.add(OrderItem(order_id=order.id, item_id=item.id, quantity=qty))

    session.commit()
    order_id = order.id
    session.close()

    return redirect(url_for("order_confirmation", order_id=order_id))


@app.route("/order/<int:order_id>")
def order_confirmation(order_id):
    session = SessionLocal()
    order = (
        session.query(Order)
        .options(joinedload(Order.order_items).joinedload(OrderItem.item))
        .filter(Order.id == order_id)
        .first()
    )
    session.close()
    if order is None:
        abort(404)
    return render_template("confirmation.html", order=order)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
