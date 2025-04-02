from datetime import datetime
from models import db

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)  
    served_at = db.Column(db.DateTime, nullable=True)  

    def __repr__(self):
        return f"<OrderItem Order:{self.order_id} MenuItem:{self.menu_item_id}>"
