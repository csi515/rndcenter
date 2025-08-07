from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from database import db, SafetyMaterial, Accident, AccidentDocument, SafetyProcedure
import math

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
    """사고관리 페이지"""
    accidents = Accident.query.order_by(Accident.date.desc()).all()
    return render_template('safety/accidents.html', accidents=accidents)

@safety_bp.route('/api/accidents')
def api_accidents():
    """사고 목록 API (DB 기반)"""
    try:
        accidents = Accident.query.order_by(Accident.date.desc()).all()
        accidents_list = []
        for accident in accidents:
                accidents_list.append({
                'id': accident.id,
                'incident_date': accident.date.strftime('%Y-%m-%d') if accident.date else '',
                'location': accident.location or '',
                'involved_person': accident.injured_person or '',
                'incident_type': accident.severity or '',
                'severity': accident.severity or '',
                'description': accident.description or '',
                'immediate_action': accident.action_taken or '',
                'follow_up': '',
                'prevention': '',
                'reporter': '',
                'status': accident.status or '',
                'created_date': accident.created_date.strftime('%Y-%m-%d %H:%M:%S') if accident.created_date else '',
                'documents': [
                    {
                        'id': doc.id,
                        'title': doc.title,
                        'url': doc.url
                    } for doc in getattr(accident, 'documents', [])
                ]
                })
        return jsonify({
            'success': True,
            'accidents': accidents_list
        })
    except Exception as e:
        print(f"Error in api_accidents: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'사고 목록을 불러오는 중 오류가 발생했습니다: {str(e)}'
        }), 500

@safety_bp.route('/api/accidents/<int:accident_id>', methods=['PUT'])
def api_update_accident(accident_id):
    """사고 정보 수정 API"""
    try:
        accident = Accident.query.get_or_404(accident_id)
        
        # 폼 데이터로부터 값 가져오기
        if request.form.get('incident_date'):
            accident.date = datetime.strptime(request.form.get('incident_date'), '%Y-%m-%d').date()
        if request.form.get('location'):
            accident.location = request.form.get('location')
        if request.form.get('involved_person'):
            accident.injured_person = request.form.get('involved_person')
        if request.form.get('severity'):
            accident.severity = request.form.get('severity')
        if request.form.get('description'):
            accident.description = request.form.get('description')
        if request.form.get('immediate_action'):
            accident.action_taken = request.form.get('immediate_action')
        if request.form.get('status'):
            accident.status = request.form.get('status')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '사고 정보가 성공적으로 수정되었습니다.'
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error in api_update_accident: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'사고 정보 수정 중 오류가 발생했습니다: {str(e)}'
        }), 500

@safety_bp.route('/api/accidents/<int:accident_id>', methods=['DELETE'])
def api_delete_accident(accident_id):
    """사고 삭제 API"""
    try:
        accident = Accident.query.get_or_404(accident_id)
        
        # 관련 문서도 함께 삭제
        AccidentDocument.query.filter_by(accident_id=accident_id).delete()
        
        db.session.delete(accident)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '사고 정보가 성공적으로 삭제되었습니다.'
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error in api_delete_accident: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'사고 삭제 중 오류가 발생했습니다: {str(e)}'
        }), 500

@safety_bp.route('/api/accidents/<int:accident_id>/documents', methods=['POST'])
def api_add_accident_document(accident_id):
    """사고 관련 문서 추가 API"""
    try:
        accident = Accident.query.get_or_404(accident_id)
        
        title = request.form.get('title')
        url = request.form.get('url')
        
        if not title or not url:
            return jsonify({
                'success': False,
                'message': '제목과 URL은 필수 입력 항목입니다.'
            }), 400
        
        new_document = AccidentDocument(
            accident_id=accident_id,
            title=title,
            url=url
        )
        
        db.session.add(new_document)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '관련 자료가 성공적으로 추가되었습니다.',
            'document': {
                'id': new_document.id,
                'title': new_document.title,
                'url': new_document.url
            }
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error in api_add_accident_document: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'관련 자료 추가 중 오류가 발생했습니다: {str(e)}'
        }), 500

@safety_bp.route('/api/accidents/<int:accident_id>/documents/<int:document_id>', methods=['DELETE'])
def api_delete_accident_document(accident_id, document_id):
    """사고 관련 문서 삭제 API"""
    try:
        document = AccidentDocument.query.filter_by(
            id=document_id, 
            accident_id=accident_id
        ).first_or_404()
        
        db.session.delete(document)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '관련 자료가 성공적으로 삭제되었습니다.'
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error in api_delete_accident_document: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'관련 자료 삭제 중 오류가 발생했습니다: {str(e)}'
        }), 500

@safety_bp.route('/accidents/add', methods=['POST'])
def add_accident():
    try:
        def parse_date(date_str):
            if not date_str:
                return None
            try:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            except Exception:
                return None
        accident = Accident(
            incident_date=parse_date(request.form.get('incident_date')),
            location=request.form.get('location'),
            involved_person=request.form.get('involved_person'),
            incident_type=request.form.get('incident_type'),
            severity=request.form.get('severity'),
            description=request.form.get('description'),
            immediate_action=request.form.get('immediate_action'),
            follow_up=request.form.get('follow_up'),
            prevention=request.form.get('prevention'),
            reporter=request.form.get('reporter'),
            status=request.form.get('status', '조사중'),
            created_date=datetime.now()
        )
        db.session.add(accident)
        db.session.commit()
        flash('사고 보고서가 성공적으로 등록되었습니다.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'사고 보고서 등록 중 오류가 발생했습니다: {str(e)}', 'error')
    return redirect(url_for('safety.accidents'))

@safety_bp.route('/education')
def education():
    # education_data = csv_manager.read_csv('education.csv')
    # education_list = education_data.to_dict('records') if not education_data.empty else []
    education_list = []
    return render_template('safety/education.html', education=education_list)

@safety_bp.route('/education/add', methods=['POST'])
def add_education():
    # data = {
    #     'id': datetime.now().strftime('%Y%m%d%H%M%S'),
    #     'trainee_name': request.form.get('trainee_name'),
    #     'course_name': request.form.get('course_name'),
    #     'course_date': request.form.get('course_date'),
    #     'duration': request.form.get('duration'),
    #     'instructor': request.form.get('instructor'),
    #     'completion_status': request.form.get('completion_status', '완료'),
    #     'score': request.form.get('score', ''),
    #     'certificate_issued': request.form.get('certificate_issued', 'N'),
    #     'notes': request.form.get('notes', ''),
    #     'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # }
    
    # if csv_manager.append_to_csv('education.csv', data):
    #     flash('교육 이력이 성공적으로 추가되었습니다.', 'success')
    # else:
    #     flash('교육 이력 추가 중 오류가 발생했습니다.', 'error')
    
    flash('교육 이력 기능은 현재 개발 중입니다.', 'info')
    return redirect(url_for('safety.education'))

@safety_bp.route('/procedures')
def procedures():
    """작업절차서 및 위험성평가 페이지"""
    procedures_data = SafetyProcedure.query.order_by(SafetyProcedure.created_date.desc()).all()
    
    # 딕셔너리로 변환하여 JSON 직렬화 가능하게 만들기
    procedures = []
    for proc in procedures_data:
        procedures.append({
            'id': proc.id,
            'title': proc.title,
            'category': proc.category,
            'description': proc.description,
            'version': proc.version,
            'created_by': proc.responsible_person,
            'review_date': proc.review_date.strftime('%Y-%m-%d') if proc.review_date else '',
            'status': proc.status,
            'procedure_link': proc.procedure_link,
            'risk_assessment_link': proc.risk_assessment_link
        })
    
    # 현재 연도 계산
    current_year = datetime.now().year
    
    return render_template('safety/procedures.html', procedures=procedures, current_year=current_year)

@safety_bp.route('/procedures/update', methods=['POST'])
def update_procedure():
    """절차서 수정"""
    try:
        procedure_id = request.form.get('procedure_id')
        procedure = SafetyProcedure.query.get_or_404(procedure_id)
        
        procedure.title = request.form.get('title')
        procedure.category = request.form.get('category')
        procedure.description = request.form.get('description')
        procedure.version = request.form.get('version')
        procedure.responsible_person = request.form.get('created_by')
        procedure.status = request.form.get('status')
        procedure.procedure_link = request.form.get('procedure_link')
        procedure.risk_assessment_link = request.form.get('risk_assessment_link')
        
        # 날짜 처리
        review_date = request.form.get('review_date')
        if review_date:
            procedure.review_date = datetime.strptime(review_date, '%Y-%m-%d').date()
        
        db.session.commit()
        flash('절차서가 성공적으로 수정되었습니다.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'절차서 수정 중 오류가 발생했습니다: {str(e)}', 'error')
    
    return redirect(url_for('safety.procedures'))

@safety_bp.route('/procedures/add', methods=['POST'])
def add_procedure():
    """작업절차서 추가"""
    try:
        new_procedure = SafetyProcedure(
            title=request.form.get('title'),
            category=request.form.get('category'),
            description=request.form.get('description'),
            version=request.form.get('version', '1.0'),
            responsible_person=request.form.get('created_by'),
            review_date=datetime.strptime(request.form.get('review_date'), '%Y-%m-%d').date() if request.form.get('review_date') else None,
            status=request.form.get('status', '유효'),
            procedure_link=request.form.get('procedure_link'),
            risk_assessment_link=request.form.get('risk_assessment_link')
        )
        
        db.session.add(new_procedure)
        db.session.commit()
        
        flash('작업절차서가 성공적으로 추가되었습니다.', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Error adding procedure: {str(e)}")
        flash('작업절차서 추가 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('safety.procedures'))

@safety_bp.route('/procedures/delete/<int:procedure_id>', methods=['POST'])
def delete_procedure(procedure_id):
    try:
        procedure = SafetyProcedure.query.get_or_404(procedure_id)
        db.session.delete(procedure)
        db.session.commit()
        return jsonify({'success': True, 'message': '절차서가 삭제되었습니다.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'삭제 중 오류: {str(e)}'})
