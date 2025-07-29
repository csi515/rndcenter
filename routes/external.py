from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db, Contact
from datetime import datetime

external_bp = Blueprint('external', __name__)

@external_bp.route('/contacts')
def contacts():
    contacts = Contact.query.order_by(Contact.created_date.desc()).all()
    contacts_json = [
        {
            'id': c.id,
            'contact_id': c.contact_id,
            'name': c.name,
            'company': c.company,
            'position': c.position,
            'department': c.department,
            'phone': c.phone,
            'email': c.email,
            'address': c.address,
            'category': c.category,
            'relationship': c.relationship,
            'notes': c.notes,
            'created_date': c.created_date.strftime('%Y-%m-%d') if c.created_date else ''
        }
        for c in contacts
    ]
    return render_template('external/contacts.html', contacts=contacts, contacts_json=contacts_json)

@external_bp.route('/contacts/add', methods=['POST'])
def add_contact():
    try:
        from datetime import datetime
        import uuid
        contact = Contact(
            contact_id=str(uuid.uuid4()),
            name=request.form.get('name'),
            company=request.form.get('company'),
            position=request.form.get('position'),
            department=request.form.get('department', ''),
            phone=request.form.get('phone'),
            email=request.form.get('email'),
            address=request.form.get('address', ''),
            category=request.form.get('category', '협력업체'),
            relationship=request.form.get('relationship', ''),
            notes=request.form.get('notes', ''),
            created_date=datetime.now()
        )
        db.session.add(contact)
        db.session.commit()
        flash('명함이 성공적으로 추가되었습니다.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'명함 추가 중 오류가 발생했습니다: {str(e)}', 'error')
    return redirect(url_for('external.contacts'))

@external_bp.route('/contacts/update/<int:contact_id>', methods=['POST'])
def update_contact(contact_id):
    try:
        contact = Contact.query.get(contact_id)
        if not contact:
            flash('명함을 찾을 수 없습니다.', 'error')
            return redirect(url_for('external.contacts'))
        contact.name = request.form.get('name')
        contact.company = request.form.get('company')
        contact.position = request.form.get('position')
        contact.department = request.form.get('department')
        contact.phone = request.form.get('phone')
        contact.email = request.form.get('email')
        contact.address = request.form.get('address')
        contact.category = request.form.get('category')
        contact.relationship = request.form.get('relationship')
        contact.notes = request.form.get('notes')
        db.session.commit()
        flash('명함 정보가 성공적으로 수정되었습니다.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'명함 정보 수정 중 오류가 발생했습니다: {str(e)}', 'error')
    return redirect(url_for('external.contacts'))

@external_bp.route('/contacts/delete/<int:contact_id>')
def delete_contact(contact_id):
    try:
        contact = Contact.query.get(contact_id)
        if not contact:
            flash('명함을 찾을 수 없습니다.', 'error')
            return redirect(url_for('external.contacts'))
        db.session.delete(contact)
        db.session.commit()
        flash('명함이 성공적으로 삭제되었습니다.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'명함 삭제 중 오류가 발생했습니다: {str(e)}', 'error')
    return redirect(url_for('external.contacts'))
