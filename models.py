"""
Data models for the USA Party Store ordering system.

Three core tables:
- Item: things available to rent (chairs, tables)
- Order: one customer's request for a single event
- OrderItem: join table — which items, and how many, are on each order
"""

from datetime import datetime, date
from enum import Enum

from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class ItemType(str, Enum):
    CHAIR = "chair"
    TABLE = "table"


class FulfillmentType(str, Enum):
    DELIVERY = "delivery"   # store drops off and later picks up
    PICKUP = "pickup"       # customer comes to get it themselves


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    OUT = "out"              # items currently with the customer
    RETURNED = "returned"
    CANCELLED = "cancelled"


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)          # e.g. "Folding Chair - White"
    type = Column(SAEnum(ItemType), nullable=False)
    price_per_day = Column(Float, nullable=False)        # flat rate, no weekday/weekend split
    quantity_available = Column(Integer, nullable=False, default=0)

    order_items = relationship("OrderItem", back_populates="item")

    def __repr__(self):
        return f"<Item {self.name} (${self.price_per_day}/day, {self.quantity_available} available)>"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    customer_name = Column(String(100), nullable=False)
    contact_info = Column(String(100), nullable=False)   # phone or email
    event_date = Column(Date, nullable=False)

    fulfillment_type = Column(SAEnum(FulfillmentType), nullable=False)

    # --- Delivery path ---
    dropoff_time = Column(DateTime, nullable=True)        # when the store delivers
    pickup_by_time = Column(DateTime, nullable=True)       # when the driver reclaims items

    # --- Self-pickup path ---
    pickup_time = Column(DateTime, nullable=True)          # when customer says they'll arrive

    status = Column(SAEnum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)

    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order #{self.id} {self.customer_name} - {self.fulfillment_type.value}>"


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)

    order = relationship("Order", back_populates="order_items")
    item = relationship("Item", back_populates="order_items")

    def __repr__(self):
        return f"<OrderItem order={self.order_id} item={self.item_id} qty={self.quantity}>"
