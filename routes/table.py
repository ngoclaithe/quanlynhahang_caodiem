from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import db
from models.order import Order
from models.order_item import OrderItem
from models.menu_item import MenuItem
from datetime import datetime
import time

tables_bp = Blueprint('tables', __name__, url_prefix='/tables')

@tables_bp.route('/')
def table_status():
    now = datetime.now()
    
    table_numbers = range(1, 6)
    
    active_orders = Order.query.filter(Order.status.in_(['pending', 'processing'])).all()
    print(active_orders)
    table_status = {}
    for table in table_numbers:
        order = next((o for o in active_orders if o.table == table), None)
        print(f"Bàn {table}: {order}")  
        
        if order:
            time_elapsed = int((datetime.now() - order.order_time).total_seconds() / 60)
            
            order_items = OrderItem.query.filter_by(order_id=order.id).all()
            
            served_items = [item for item in order_items if item.served_at is not None]
            unserved_items = [item for item in order_items if item.served_at is None]
            
            table_status[table] = {
                'has_order': True,
                'order_id': order.id,
                'order_time': order.order_time,
                'time_elapsed': time_elapsed,
                'status': order.status,
                'total_items': len(order_items),
                'served_items': len(served_items),
                'unserved_items': len(unserved_items)
            }
        else:
            table_status[table] = {
                'has_order': False
            }
    
    return render_template('table.html', table_status=table_status, now=now)
@tables_bp.route('/order/<int:table_number>')
def table_order_details(table_number):
    now = datetime.now()
    
    order = Order.query.filter_by(table=str(table_number)).filter(Order.status.in_(['pending', 'processing'])).first()
    
    if not order:
        flash('Không tìm thấy đơn hàng đang hoạt động cho bàn này', 'warning')
        return redirect(url_for('tables.table_status'))
    
    order_items = OrderItem.query.filter_by(order_id=order.id).all()
    
    items_with_details = []
    for item in order_items:
        menu_item = MenuItem.query.get(item.menu_item_id)
        items_with_details.append({
            'id': item.id,
            'name': menu_item.name,
            'quantity': item.quantity,
            'note': item.note,
            'served_at': item.served_at,
            'is_served': item.served_at is not None
        })
    
    return render_template('table_order_detail.html', 
                          order=order, 
                          items=items_with_details,
                          table_number=table_number,
                          now=now)  

@tables_bp.route('/api/table_status')
def api_table_status():
    table_numbers = range(1, 6)
    active_orders = Order.query.filter(Order.status.in_(['pending', 'processing'])).all()
    
    table_status = {}
    for table in table_numbers:
        order = next((o for o in active_orders if o.table == table), None)
        print(f"Bàn {table}: {order}")  
        
        if order:
            time_elapsed = int((datetime.now() - order.order_time).total_seconds() / 60)
            order_items = OrderItem.query.filter_by(order_id=order.id).all()
            served_items = [item for item in order_items if item.served_at is not None]
            
            table_status[table] = {
                'has_order': True,
                'order_id': order.id,
                'time_elapsed': time_elapsed,
                'status': order.status,
                'total_items': len(order_items),
                'served_items': len(served_items),
                'unserved_items': len(order_items) - len(served_items)
            }
        else:
            table_status[table] = {
                'has_order': False
            }
    
    return jsonify(table_status)
@tables_bp.route('/update_served_status/<int:item_id>', methods=['POST'])
def update_served_status(item_id):
    order_item = OrderItem.query.get_or_404(item_id)
    
    if order_item.served_at is None:
        order_item.served_at = datetime.now()
        db.session.commit()
        flash('Đã cập nhật trạng thái phục vụ của món', 'success')
    else:
        if request.form.get('reset_served') == 'true':
            order_item.served_at = None
            db.session.commit()
            flash('Đã đặt lại trạng thái món thành chưa phục vụ', 'success')
    
    order = Order.query.get(order_item.order_id)
    all_items = OrderItem.query.filter_by(order_id=order.id).all()
    
    if all(item.served_at is not None for item in all_items) and order.status != 'completed':
        # order.status = 'completed'
        # db.session.commit()
        flash('Tất cả các món đã được phục vụ. Đơn hàng đã được đánh dấu là hoàn thành', 'success')
    
    return redirect(url_for('tables.table_order_details', table_number=order.table))