from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from database import db, InventoryItem, InventoryTransaction
import uuid
from datetime import datetime

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except Exception:
        return None

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/current')
def current_inventory():
    inventory = InventoryItem.query.order_by(InventoryItem.created_date.desc()).all()
    inventory_list = []
    for i in inventory:
        inventory_list.append({
            'id': i.id,
            'item_id': i.item_id,
            'item_name': i.name,
            'quantity': i.quantity,
            'unit': i.unit,
            'location': i.location,
            'category': i.category,
            'supplier': i.supplier,
            'purchase_date': i.purchase_date.strftime('%Y-%m-%d') if i.purchase_date else '',
            'expiry_date': i.expiry_date.strftime('%Y-%m-%d') if i.expiry_date else '',
            'min_stock': i.min_quantity,
            'notes': i.storage_condition,
            'created_date': i.created_date.strftime('%Y-%m-%d') if i.created_date else ''
        })
    locations = ['1층 창고', '자료실', '가스보관실', '열분석실']
    return render_template('inventory/current.html', inventory=inventory_list, locations=locations)

@inventory_bp.route('/add', methods=['POST'])
def add_inventory():
    try:
        item = InventoryItem(
            item_id=str(uuid.uuid4()),
            name=request.form.get('item_name'),
            quantity=int(request.form.get('quantity', 0)),
            unit=request.form.get('unit'),
            location=request.form.get('location'),
            category=request.form.get('category', ''),
            supplier=request.form.get('supplier', ''),
            purchase_date=parse_date(request.form.get('purchase_date')),
            expiry_date=parse_date(request.form.get('expiry_date')),
            min_quantity=int(request.form.get('min_stock', 5)),
            storage_condition=request.form.get('notes', ''),
            created_date=datetime.now()
        )
        db.session.add(item)
        db.session.commit()
        flash('재고 항목이 성공적으로 추가되었습니다.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'재고 항목 추가 중 오류가 발생했습니다: {str(e)}', 'error')
    return redirect(url_for('inventory.current_inventory'))

@inventory_bp.route('/update_quantity/<int:index>', methods=['POST'])
def update_quantity(index):
    try:
        inventory = InventoryItem.query.order_by(InventoryItem.created_date.desc()).all()
        item = inventory[index]
        new_quantity = int(request.form.get('quantity', 0))
        old_quantity = item.quantity
        change = new_quantity - old_quantity
        item.quantity = new_quantity
        db.session.commit()
        # 입출고 기록 생성
        transaction = InventoryTransaction(
            id=str(uuid.uuid4()),
            item_id=item.item_id,
            item_name=item.name,
            transaction_type='입고' if change > 0 else '출고',
            quantity=abs(change),
            before_quantity=old_quantity,
            after_quantity=new_quantity,
            user=request.form.get('user', '시스템'),
            notes=request.form.get('notes', '수량 조정'),
            transaction_date=datetime.now()
        )
        db.session.add(transaction)
        db.session.commit()
        flash('재고 수량이 성공적으로 업데이트되었습니다.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'재고 수량 업데이트 중 오류가 발생했습니다: {str(e)}', 'error')
    return redirect(url_for('inventory.current_inventory'))

@inventory_bp.route('/filter/<location>')
def filter_by_location(location):
    inventory = InventoryItem.query.filter_by(location=location).order_by(InventoryItem.created_date.desc()).all()
    inventory_list = []
    for i in inventory:
        inventory_list.append({
            'id': i.id,
            'item_id': i.item_id,
            'item_name': i.name,
            'quantity': i.quantity,
            'unit': i.unit,
            'location': i.location,
            'category': i.category,
            'supplier': i.supplier,
            'purchase_date': i.purchase_date.strftime('%Y-%m-%d') if i.purchase_date else '',
            'expiry_date': i.expiry_date.strftime('%Y-%m-%d') if i.expiry_date else '',
            'min_stock': i.min_quantity,
            'notes': i.storage_condition,
            'created_date': i.created_date.strftime('%Y-%m-%d') if i.created_date else ''
        })
    locations = ['1층 창고', '자료실', '가스보관실', '열분석실']
    return render_template('inventory/current.html', inventory=inventory_list, locations=locations, selected_location=location)

@inventory_bp.route('/api/add', methods=['POST'])
def api_add_inventory():
    data = request.get_json()
    try:
        item = InventoryItem(
            item_id=data.get('item_id') or str(uuid.uuid4()),
            name=data.get('name'),
            category='',
            quantity=0,
            unit='',
            min_quantity=int(data.get('min_quantity', 0)),
            supplier='',
            location='',
            purchase_date=None,
            expiry_date=None,
            storage_condition='',
            created_date=datetime.now()
        )
        # 사양(spec) 필드는 DB에 없으므로 storage_condition에 임시 저장
        if data.get('spec'):
            item.storage_condition = data['spec']
        db.session.add(item)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@inventory_bp.route('/api/list')
def api_inventory_list():
    items = InventoryItem.query.order_by(InventoryItem.created_date.desc()).all()
    result = []
    for i in items:
        result.append({
            'id': i.id,
            'name': i.name,
            'spec': i.storage_condition,
            'item_id': i.item_id,
            'min_quantity': i.min_quantity
        })
    return jsonify(result)

@inventory_bp.route('/api/update', methods=['POST'])
def api_update_inventory():
    data = request.get_json()
    try:
        item = InventoryItem.query.get(int(data.get('id')))
        if not item:
            return jsonify({'success': False, 'message': '해당 품목을 찾을 수 없습니다.'})
        item.name = data.get('name')
        item.item_id = data.get('item_id')
        item.min_quantity = int(data.get('min_quantity', 0))
        # 사양(spec)은 storage_condition에 저장
        item.storage_condition = data.get('spec', '')
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@inventory_bp.route('/api/delete', methods=['POST'])
def api_delete_inventory():
    data = request.get_json()
    try:
        item = InventoryItem.query.get(int(data.get('id')))
        if not item:
            return jsonify({'success': False, 'message': '해당 품목을 찾을 수 없습니다.'})
        db.session.delete(item)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})
