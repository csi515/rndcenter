from flask import Blueprint, render_template, request, redirect, url_for, flash
from csv_manager import csv_manager
from datetime import datetime

external_bp = Blueprint('external', __name__)

@external_bp.route('/contacts')
def contacts():
    contacts_data = csv_manager.read_csv('contacts.csv')
    contacts_list = contacts_data.to_dict('records') if not contacts_data.empty else []
    return render_template('external/contacts.html', contacts=contacts_list)

@external_bp.route('/contacts/add', methods=['POST'])
def add_contact():
    data = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'name': request.form.get('name'),
        'company': request.form.get('company'),
        'position': request.form.get('position'),
        'department': request.form.get('department', ''),
        'phone': request.form.get('phone'),
        'email': request.form.get('email'),
        'address': request.form.get('address', ''),
        'category': request.form.get('category', '협력업체'),
        'relationship': request.form.get('relationship', ''),
        'notes': request.form.get('notes', ''),
        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if csv_manager.append_to_csv('contacts.csv', data):
        flash('명함이 성공적으로 추가되었습니다.', 'success')
    else:
        flash('명함 추가 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('external.contacts'))

@external_bp.route('/contacts/update/<int:index>', methods=['POST'])
def update_contact(index):
    data = {
        'name': request.form.get('name'),
        'company': request.form.get('company'),
        'position': request.form.get('position'),
        'department': request.form.get('department'),
        'phone': request.form.get('phone'),
        'email': request.form.get('email'),
        'address': request.form.get('address'),
        'category': request.form.get('category'),
        'relationship': request.form.get('relationship'),
        'notes': request.form.get('notes'),
        'updated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if csv_manager.update_row('contacts.csv', index, data):
        flash('명함 정보가 성공적으로 수정되었습니다.', 'success')
    else:
        flash('명함 정보 수정 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('external.contacts'))

@external_bp.route('/contacts/delete/<int:index>')
def delete_contact(index):
    if csv_manager.delete_row('contacts.csv', index):
        flash('명함이 성공적으로 삭제되었습니다.', 'success')
    else:
        flash('명함 삭제 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('external.contacts'))
