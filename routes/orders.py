from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db
from models.order import Order
from models.order_item import OrderItem
from models.menu_item import MenuItem
from datetime import datetime

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')

@orders_bp.route('/')
def list_orders():
    orders = Order.query.all()
    return render_template('orders.html', orders=orders)

@orders_bp.route('/create', methods=['GET', 'POST'])
def create_order():
    if request.method == 'POST':
        waiter_id = session.get('user_id')
        status = 'pending'
        total_amount = float(request.form.get('total_amount', 0.0))
        
        order = Order(
            waiter_id=waiter_id, 
            status=status, 
            total_amount=total_amount, 
            order_time=datetime.utcnow()
        )
        db.session.add(order)
        db.session.flush() 
        
        item_ids = request.form.getlist('item_ids[]')
        quantities = request.form.getlist('quantities[]')
        notes = request.form.getlist('notes[]')
        
        for i in range(len(item_ids)):
            menu_item_id = item_ids[i]
            quantity = int(quantities[i])
            note = notes[i] if i < len(notes) else ""
            
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=menu_item_id,
                quantity=quantity,
                note=note
            )
            db.session.add(order_item)
        
        db.session.commit()
        flash('Đơn hàng được tạo thành công', 'success')
        return redirect(url_for('orders.list_orders'))
        
    menu_items = MenuItem.query.all()
    return render_template('create_order.html', menu_items=menu_items)

@orders_bp.route('/<int:order_id>')
def view_order(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('order_detail.html', order=order)
