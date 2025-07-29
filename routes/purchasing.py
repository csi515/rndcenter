from flask import Blueprint, render_template, request, jsonify, send_file
from datetime import datetime
import os
import uuid
import math
import json
import io
from database import db, PurchaseRequest, ProjectType

purchasing_bp = Blueprint('purchasing', __name__)

# 커스텀 JSON 인코더 (NaN, inf 값을 안전하게 처리)
class SafeJSONEncoder(json.JSONEncoder):
    def encode(self, obj):
        if isinstance(obj, dict):
            obj = self._clean_dict(obj)
        elif isinstance(obj, list):
            obj = [self._clean_value(item) for item in obj]
        return super().encode(obj)
    
    def _clean_dict(self, d):
        cleaned = {}
        for k, v in d.items():
            cleaned[k] = self._clean_value(v)
        return cleaned
    
    def _clean_value(self, value):
        if isinstance(value, float):
            if math.isnan(value) or math.isinf(value):
                return 0
        elif isinstance(value, dict):
            return self._clean_dict(value)
        elif isinstance(value, list):
            return [self._clean_value(item) for item in value]
        elif value is None:
            return ''
        return value

# 안전한 jsonify 함수
def safe_jsonify(data):
    json_str = json.dumps(data, cls=SafeJSONEncoder, ensure_ascii=False)
    from flask import Response
    return Response(json_str, mimetype='application/json')

@purchasing_bp.route('/requests')
def purchase_requests():
    requests = PurchaseRequest.query.order_by(PurchaseRequest.request_date.desc()).all()
    requests_list = []
    for r in requests:
        requests_list.append({
            'id': r.request_id,
            'item': r.item_name,
            'spec': getattr(r, 'spec', ''),
            'item_number': getattr(r, 'item_number', ''),
            'unit': getattr(r, 'unit', ''),
            'project_type': getattr(r, 'project_type', ''),
            'required_qty': r.quantity,
            'safety_stock': getattr(r, 'safety_stock', 0),
            'purchase_qty': r.quantity,
            'unit_price': float(r.unit_price) if r.unit_price else 0,
            'total_price': float(r.total_price) if r.total_price else 0,
            'purchase_status': r.status,
            'note': getattr(r, 'notes', ''),
            'reason': getattr(r, 'reason', ''),
            'requester': r.requester,
            'request_date': r.request_date.strftime('%Y-%m-%d') if r.request_date else ''
        })
    # project_types는 별도 구현 필요
    return render_template('purchasing/requests.html', requests=requests_list, project_types=[])

@purchasing_bp.route('/requests/add', methods=['POST'])
def add_purchase_request():
    try:
        data = request.json if request.is_json else request.form
        now = datetime.now()
        req = PurchaseRequest(
            request_id=str(uuid.uuid4()),
            item_name=data.get('item',''),
            quantity=float(data.get('purchase_qty',0)),
            unit_price=float(data.get('unit_price',0)),
            total_price=float(data.get('purchase_qty',0)) * float(data.get('unit_price',0)),
            status=data.get('purchase_status','대기'),
            notes=data.get('note',''),
            reason=data.get('reason',''),
            requester=data.get('requester',''),
            request_date=now.date()
        )
        db.session.add(req)
        db.session.commit()
        return safe_jsonify({'success': True, 'data': {
            'id': req.request_id,
            'item': req.item_name,
            'purchase_qty': req.quantity,
            'unit_price': float(req.unit_price) if req.unit_price else 0,
            'total_price': float(req.total_price) if req.total_price else 0,
            'purchase_status': req.status,
            'note': req.notes,
            'reason': req.reason,
            'requester': req.requester,
            'request_date': req.request_date.strftime('%Y-%m-%d') if req.request_date else ''
        }})
    except Exception as e:
        db.session.rollback()
        return safe_jsonify({'success': False, 'error': str(e)})

@purchasing_bp.route('/requests/update/<req_id>', methods=['POST'])
def update_purchase_request(req_id):
    try:
        req = PurchaseRequest.query.filter_by(request_id=req_id).first()
        if not req:
            return safe_jsonify({'success': False, 'error': '해당 요청 없음'})
        data = request.json if request.is_json else request.form
        req.item_name = data.get('item', req.item_name)
        req.quantity = float(data.get('purchase_qty', req.quantity))
        req.unit_price = float(data.get('unit_price', req.unit_price))
        req.total_price = req.quantity * req.unit_price
        req.status = data.get('purchase_status', req.status)
        req.notes = data.get('note', req.notes)
        req.reason = data.get('reason', req.reason)
        req.requester = data.get('requester', req.requester)
        db.session.commit()
        return safe_jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return safe_jsonify({'success': False, 'error': str(e)})

@purchasing_bp.route('/requests/delete/<req_id>', methods=['POST'])
def delete_purchase_request(req_id):
    try:
        req = PurchaseRequest.query.filter_by(request_id=req_id).first()
        if req:
            db.session.delete(req)
            db.session.commit()
        return safe_jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return safe_jsonify({'success': False, 'error': str(e)})

@purchasing_bp.route('/requests/list', methods=['GET'])
def list_purchase_requests():
    query = PurchaseRequest.query
    item = request.args.get('item')
    spec = request.args.get('spec')
    requester = request.args.get('requester')
    project_type = request.args.get('project_type')
    if item:
        query = query.filter(PurchaseRequest.item_name.contains(item))
    # spec, project_type 등은 모델에 필드가 있으면 추가
    if requester:
        query = query.filter(PurchaseRequest.requester.contains(requester))
    # project_type 필드는 필요시 모델에 추가
    results = query.all()
    result_list = []
    for r in results:
        result_list.append({
            'id': r.request_id,
            'item': r.item_name,
            'purchase_qty': r.quantity,
            'unit_price': float(r.unit_price) if r.unit_price else 0,
            'total_price': float(r.total_price) if r.total_price else 0,
            'purchase_status': r.status,
            'note': r.notes,
            'reason': r.reason,
            'requester': r.requester,
            'request_date': r.request_date.strftime('%Y-%m-%d') if r.request_date else ''
        })
    return safe_jsonify(result_list)

@purchasing_bp.route('/requests/summary', methods=['GET'])
def purchase_summary():
    total_count = PurchaseRequest.query.count()
    total_price = db.session.query(db.func.sum(PurchaseRequest.total_price)).scalar() or 0
    return safe_jsonify({'total_count': total_count, 'total_price': float(total_price)})

# 국책과제 종류 관리
@purchasing_bp.route('/project-types/list')
def list_project_types():
    types = ProjectType.query.all()
    result = []
    for t in types:
        result.append({'id': t.id, 'project_type': t.project_type})
    return safe_jsonify(result)

@purchasing_bp.route('/project-types/add', methods=['POST'])
def add_project_type():
    new_type = request.json.get('project_type')
    if ProjectType.query.filter_by(project_type=new_type).first():
        return safe_jsonify({'success': False, 'error': '이미 존재하는 국책과제 종류입니다.'})
    import uuid
    t = ProjectType(id=str(uuid.uuid4()), project_type=new_type)
    db.session.add(t)
    db.session.commit()
    return safe_jsonify({'success': True, 'data': {'id': t.id, 'project_type': t.project_type}})

@purchasing_bp.route('/project-types/delete/<type_id>', methods=['POST'])
def delete_project_type(type_id):
    t = ProjectType.query.filter_by(id=type_id).first()
    if t:
        db.session.delete(t)
        db.session.commit()
    return safe_jsonify({'success': True})

@purchasing_bp.route('/requests/toggle-status/<req_id>', methods=['POST'])
def toggle_purchase_status(req_id):
    try:
        print(f"구매 상태 변경 요청: {req_id}")
        
        # 데이터베이스에서 요청 찾기
        request = PurchaseRequest.query.filter_by(request_id=req_id).first()
        if not request:
            print(f"해당 ID를 찾을 수 없음: {req_id}")
            return safe_jsonify({'success': False, 'error': '해당 요청을 찾을 수 없습니다.'})
        
        current_status = request.status if request.status else '대기'
        print(f"현재 상태: {current_status}")
        
        # 상태 순환: 대기 -> 완료 -> 취소 -> 대기
        if current_status == '대기':
            new_status = '완료'
        elif current_status == '완료':
            new_status = '취소'
        else:
            new_status = '대기'
        
        print(f"새 상태: {new_status}")
        
        request.status = new_status
        db.session.commit()
        print("데이터베이스 저장 완료")
        
        return safe_jsonify({'success': True, 'new_status': new_status})
        
    except Exception as e:
        print(f"구매 상태 변경 에러: {str(e)}")
        import traceback
        traceback.print_exc()
        return safe_jsonify({'success': False, 'error': str(e)})

@purchasing_bp.route('/requests/export-excel', methods=['GET'])
def export_purchase_requests_excel():
    try:
        # 데이터베이스에서 데이터 읽기
        query = PurchaseRequest.query
        
        # 필터링 (URL 파라미터 적용)
        item = request.args.get('item')
        spec = request.args.get('spec')
        requester = request.args.get('requester')
        project_type = request.args.get('project_type')
        
        if item:
            query = query.filter(
                db.or_(
                    PurchaseRequest.item_name.contains(item),
                    PurchaseRequest.spec.contains(item)
                )
            )
        if spec:
            query = query.filter(PurchaseRequest.spec.contains(spec))
        if requester:
            query = query.filter(PurchaseRequest.requester.contains(requester))
        if project_type:
            query = query.filter(PurchaseRequest.project_type == project_type)
        
        requests = query.all()
        
        if not requests:
            return safe_jsonify({'success': False, 'error': '내보낼 데이터가 없습니다.'})
        
        # Excel 파일 생성
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment
        
        wb = Workbook()
        ws = wb.active
        ws.title = "구매요청목록"
        
        # 헤더 설정
        headers = ['품목', '사양', '품목번호', '단위', '국책과제', '구매수량', '단가', '총가격', '비고', '사유', '요청자', '요청일', '구매여부']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center')
        
        # 데이터 입력
        for row, req in enumerate(requests, 2):
            ws.cell(row=row, column=1, value=req.item_name or '')
            ws.cell(row=row, column=2, value=getattr(req, 'spec', '') or '')
            ws.cell(row=row, column=3, value=getattr(req, 'item_number', '') or '')
            ws.cell(row=row, column=4, value=getattr(req, 'unit', '') or '')
            ws.cell(row=row, column=5, value=getattr(req, 'project_type', '') or '')
            ws.cell(row=row, column=6, value=req.quantity or 0)
            ws.cell(row=row, column=7, value=float(req.unit_price) if req.unit_price else 0)
            ws.cell(row=row, column=8, value=float(req.total_price) if req.total_price else 0)
            ws.cell(row=row, column=9, value=getattr(req, 'notes', '') or '')
            ws.cell(row=row, column=10, value=getattr(req, 'reason', '') or '')
            ws.cell(row=row, column=11, value=req.requester or '')
            ws.cell(row=row, column=12, value=req.request_date.strftime('%Y-%m-%d') if req.request_date else '')
            ws.cell(row=row, column=13, value=req.status or '대기')
        
        # 숫자 컬럼 포맷팅
        for col in ['구매수량', '단가', '총가격']:
            if col in df_export.columns:
                df_export[col] = pd.to_numeric(df_export[col], errors='coerce').fillna(0)
        
        # BytesIO 메모리 버퍼에 엑셀 파일 생성
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_export.to_excel(writer, sheet_name='구매요청내역', index=False)
            try:
                worksheet = writer.sheets['구매요청내역']
                from openpyxl.styles import Font, PatternFill, Alignment
                header_font = Font(bold=True, color='FFFFFF')
                header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
                for cell in worksheet[1]:
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.alignment = Alignment(horizontal='center')
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            except Exception as style_error:
                print(f"스타일링 에러 (무시됨): {style_error}")
        output.seek(0)
        filename = f"구매요청내역_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        print(f"엑셀 내보내기 에러: {str(e)}")
        import traceback
        traceback.print_exc()
        return safe_jsonify({'success': False, 'error': str(e)})
