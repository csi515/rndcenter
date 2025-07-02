from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from csv_manager import csv_manager
from datetime import datetime
from database import db, SafetyMaterial

safety_bp = Blueprint('safety', __name__)

@safety_bp.route('/materials')
def materials():
    """안전 교육자료 목록 페이지"""
    materials = SafetyMaterial.query.order_by(SafetyMaterial.created_date.desc()).all()
    return render_template('safety/materials.html', materials=materials)

@safety_bp.route('/api/materials')
def api_materials():
    """교육자료 목록 API"""
    try:
        materials = SafetyMaterial.query.order_by(SafetyMaterial.created_date.desc()).all()
        materials_list = []
        
        for material in materials:
            materials_list.append({
                'id': material.id,
                'title': material.title,
                'content': material.content,
                'link': material.link,
                'created_date': material.created_date.strftime('%Y-%m-%d %H:%M:%S') if material.created_date else '',
                'updated_date': material.updated_date.strftime('%Y-%m-%d %H:%M:%S') if material.updated_date else ''
            })
        
        return jsonify({
            'success': True,
            'materials': materials_list
        })
    except Exception as e:
        print(f"Error in api_materials: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'교육자료 목록을 불러오는 중 오류가 발생했습니다: {str(e)}'
        }), 500

@safety_bp.route('/api/materials/add', methods=['POST'])
def api_add_material():
    """교육자료 추가 API"""
    try:
        title = request.form.get('title')
        content = request.form.get('content')
        link = request.form.get('link', '')
        
        if not title or not content:
            return jsonify({
                'success': False,
                'message': '제목과 내용은 필수 입력 항목입니다.'
            }), 400
        
        new_material = SafetyMaterial(
            title=title,
            content=content,
            link=link
        )
        
        db.session.add(new_material)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '교육자료가 성공적으로 추가되었습니다.',
            'material': {
                'id': new_material.id,
                'title': new_material.title,
                'content': new_material.content,
                'link': new_material.link
            }
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error in api_add_material: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'교육자료 추가 중 오류가 발생했습니다: {str(e)}'
        }), 500

@safety_bp.route('/api/materials/<int:material_id>', methods=['PUT'])
def api_update_material(material_id):
    """교육자료 수정 API"""
    try:
        material = SafetyMaterial.query.get_or_404(material_id)
        
        title = request.form.get('title')
        content = request.form.get('content')
        link = request.form.get('link', '')
        
        if not title or not content:
            return jsonify({
                'success': False,
                'message': '제목과 내용은 필수 입력 항목입니다.'
            }), 400
        
        material.title = title
        material.content = content
        material.link = link
        material.updated_date = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '교육자료가 성공적으로 수정되었습니다.'
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error in api_update_material: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'교육자료 수정 중 오류가 발생했습니다: {str(e)}'
        }), 500

@safety_bp.route('/api/materials/<int:material_id>', methods=['DELETE'])
def api_delete_material(material_id):
    """교육자료 삭제 API"""
    try:
        material = SafetyMaterial.query.get_or_404(material_id)
        
        db.session.delete(material)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '교육자료가 성공적으로 삭제되었습니다.'
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error in api_delete_material: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'교육자료 삭제 중 오류가 발생했습니다: {str(e)}'
        }), 500

@safety_bp.route('/accidents')
def accidents():
    accidents_data = csv_manager.read_csv('accidents.csv')
    accidents_list = accidents_data.to_dict('records') if not accidents_data.empty else []
    return render_template('safety/accidents.html', accidents=accidents_list)

@safety_bp.route('/accidents/add', methods=['POST'])
def add_accident():
    data = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'incident_date': request.form.get('incident_date'),
        'location': request.form.get('location'),
        'description': request.form.get('description'),
        'severity': request.form.get('severity'),
        'involved_person': request.form.get('involved_person'),
        'cause': request.form.get('cause', ''),
        'action_taken': request.form.get('action_taken', ''),
        'prevention_measures': request.form.get('prevention_measures', ''),
        'status': request.form.get('status', '조사중'),
        'reporter': request.form.get('reporter'),
        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if csv_manager.append_to_csv('accidents.csv', data):
        flash('사고 보고서가 성공적으로 등록되었습니다.', 'success')
    else:
        flash('사고 보고서 등록 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('safety.accidents'))

@safety_bp.route('/education')
def education():
    education_data = csv_manager.read_csv('education.csv')
    education_list = education_data.to_dict('records') if not education_data.empty else []
    return render_template('safety/education.html', education=education_list)

@safety_bp.route('/education/add', methods=['POST'])
def add_education():
    data = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'trainee_name': request.form.get('trainee_name'),
        'course_name': request.form.get('course_name'),
        'course_date': request.form.get('course_date'),
        'duration': request.form.get('duration'),
        'instructor': request.form.get('instructor'),
        'completion_status': request.form.get('completion_status', '완료'),
        'score': request.form.get('score', ''),
        'certificate_issued': request.form.get('certificate_issued', 'N'),
        'notes': request.form.get('notes', ''),
        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if csv_manager.append_to_csv('education.csv', data):
        flash('교육 이력이 성공적으로 추가되었습니다.', 'success')
    else:
        flash('교육 이력 추가 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('safety.education'))

@safety_bp.route('/excellence')
def excellence():
    excellence_data = csv_manager.read_csv('excellence.csv')
    excellence_list = excellence_data.to_dict('records') if not excellence_data.empty else []
    return render_template('safety/excellence.html', excellence=excellence_list)

@safety_bp.route('/procedures')
def procedures():
    procedures_data = csv_manager.read_csv('procedures.csv')
    procedures_list = procedures_data.to_dict('records') if not procedures_data.empty else []
    return render_template('safety/procedures.html', procedures=procedures_list)

@safety_bp.route('/procedures/add', methods=['POST'])
def add_procedure():
    data = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'title': request.form.get('title'),
        'category': request.form.get('category'),
        'description': request.form.get('description'),
        'file_link': request.form.get('file_link'),
        'version': request.form.get('version', '1.0'),
        'created_by': request.form.get('created_by'),
        'review_date': request.form.get('review_date'),
        'status': request.form.get('status', '유효'),
        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if csv_manager.append_to_csv('procedures.csv', data):
        flash('작업절차서가 성공적으로 추가되었습니다.', 'success')
    else:
        flash('작업절차서 추가 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('safety.procedures'))
