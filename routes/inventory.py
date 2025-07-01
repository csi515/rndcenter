from flask import Blueprint, render_template, request, redirect, url_for, flash
from csv_manager import csv_manager
from datetime import datetime

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/current')
def current_inventory():
    inventory_data = csv_manager.read_csv('inventory.csv')
    inventory_list = inventory_data.to_dict('records') if not inventory_data.empty else []
    
    # 장소별 필터링을 위한 고유 장소 목록
    locations = ['1층 창고', '자료실', '가스보관실', '열분석실']
    
    return render_template('inventory/current.html', 
                         inventory=inventory_list,
                         locations=locations)

@inventory_bp.route('/add', methods=['POST'])
def add_inventory():
    data = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'item_name': request.form.get('item_name'),
        'quantity': int(request.form.get('quantity', 0)),
        'unit': request.form.get('unit'),
        'location': request.form.get('location'),
        'category': request.form.get('category', ''),
        'supplier': request.form.get('supplier', ''),
        'purchase_date': request.form.get('purchase_date'),
        'expiry_date': request.form.get('expiry_date', ''),
        'min_stock': int(request.form.get('min_stock', 5)),
        'notes': request.form.get('notes', ''),
        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if csv_manager.append_to_csv('inventory.csv', data):
        flash('재고 항목이 성공적으로 추가되었습니다.', 'success')
    else:
        flash('재고 항목 추가 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('inventory.current_inventory'))

@inventory_bp.route('/update_quantity/<int:index>', methods=['POST'])
def update_quantity(index):
    new_quantity = int(request.form.get('quantity', 0))
    old_quantity = int(request.form.get('old_quantity', 0))
    change = new_quantity - old_quantity
    
    # 재고 수량 업데이트
    data = {
        'quantity': new_quantity,
        'updated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if csv_manager.update_row('inventory.csv', index, data):
        # 입출고 기록 생성
        inventory_data = csv_manager.read_csv('inventory.csv')
        if not inventory_data.empty and index < len(inventory_data):
            item_name = inventory_data.iloc[index]['item_name']
            
            transaction_data = {
                'id': datetime.now().strftime('%Y%m%d%H%M%S'),
                'item_name': item_name,
                'transaction_type': '입고' if change > 0 else '출고',
                'quantity': abs(change),
                'before_quantity': old_quantity,
                'after_quantity': new_quantity,
                'user': request.form.get('user', '시스템'),
                'notes': request.form.get('notes', '수량 조정'),
                'transaction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            csv_manager.append_to_csv('입출고기록.csv', transaction_data)
        
        flash('재고 수량이 성공적으로 업데이트되었습니다.', 'success')
    else:
        flash('재고 수량 업데이트 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('inventory.current_inventory'))

@inventory_bp.route('/filter/<location>')
def filter_by_location(location):
    inventory_data = csv_manager.read_csv('inventory.csv')
    
    if not inventory_data.empty:
        filtered_data = inventory_data[inventory_data['location'] == location]
        inventory_list = filtered_data.to_dict('records')
    else:
        inventory_list = []
    
    locations = ['1층 창고', '자료실', '가스보관실', '열분석실']
    
    return render_template('inventory/current.html', 
                         inventory=inventory_list,
                         locations=locations,
                         selected_location=location)
