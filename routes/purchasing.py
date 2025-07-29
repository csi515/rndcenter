from flask import Blueprint, render_template, request, jsonify, send_file
from csv_manager import csv_manager
from datetime import datetime
import os
import uuid
import math
import json
import pandas as pd
import io
from database import db, PurchaseRequest, ProjectType

purchasing_bp = Blueprint('purchasing', __name__)

PURCHASE_CSV = 'purchase_requests.csv'
PROJECT_TYPE_CSV = 'project_types.csv'

PURCHASE_FIELDS = [
    'id','item','spec','item_number','unit','project_type','required_qty','safety_stock','purchase_qty','unit_price','total_price','purchase_status','note','reason','requester','request_date'
]

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

# CSV 파일 자동 생성
for fname, fields in [
    (PURCHASE_CSV, PURCHASE_FIELDS),
    (PROJECT_TYPE_CSV, ['id','project_type'])
]:
    path = os.path.join('data', fname)
    if not os.path.exists(path):
        import pandas as pd
        pd.DataFrame(columns=fields).to_csv(path, index=False, encoding='utf-8-sig')

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
        import pandas as pd
        df = csv_manager.read_csv(PURCHASE_CSV)
        print(f"CSV 읽기 완료, 총 {len(df)}개 행")
        
        # purchase_status 컬럼이 없으면 추가
        if 'purchase_status' not in df.columns:
            print("purchase_status 컬럼이 없어서 추가합니다.")
            df['purchase_status'] = '대기'
        
        idx = df.index[df['id']==req_id].tolist()
        if not idx:
            print(f"해당 ID를 찾을 수 없음: {req_id}")
            return safe_jsonify({'success': False, 'error': '해당 요청을 찾을 수 없습니다.'})
        
        i = idx[0]
        print(f"찾은 인덱스: {i}")
        
        current_status = str(df.at[i, 'purchase_status']) if pd.notna(df.at[i, 'purchase_status']) else '대기'
        print(f"현재 상태: {current_status}")
        
        # 상태 순환: 대기 -> 완료 -> 취소 -> 대기
        if current_status == '대기':
            new_status = '완료'
        elif current_status == '완료':
            new_status = '취소'
        else:
            new_status = '대기'
        
        print(f"새 상태: {new_status}")
        
        df.at[i, 'purchase_status'] = new_status
        csv_manager.write_csv(PURCHASE_CSV, df)
        print("CSV 저장 완료")
        
        return safe_jsonify({'success': True, 'new_status': new_status})
        
    except Exception as e:
        print(f"구매 상태 변경 에러: {str(e)}")
        import traceback
        traceback.print_exc()
        return safe_jsonify({'success': False, 'error': str(e)})

@purchasing_bp.route('/requests/export-excel', methods=['GET'])
def export_purchase_requests_excel():
    try:
        # CSV 데이터 읽기
        df = csv_manager.read_csv(PURCHASE_CSV)
        
        if df.empty:
            return safe_jsonify({'success': False, 'error': '내보낼 데이터가 없습니다.'})
        
        # purchase_status 컬럼이 없으면 추가
        if 'purchase_status' not in df.columns:
            df['purchase_status'] = '대기'
        
        # 필터링 (URL 파라미터 적용)
        item = request.args.get('item')
        spec = request.args.get('spec')
        requester = request.args.get('requester')
        project_type = request.args.get('project_type')
        
        if item:
            df = df[df['item_name'].fillna('').str.contains(item, na=False) | df['item'].fillna('').str.contains(item, na=False) | df['spec'].fillna('').str.contains(item, na=False)]
        if spec:
            df = df[df['spec'].str.contains(spec, na=False)]
        if requester:
            df = df[df['requester'].str.contains(requester, na=False)]
        if project_type:
            df = df[df['project_type'] == project_type]
        
        # 실제 CSV 헤더에 맞는 컬럼 매핑
        column_mapping = {
            'item_name': '품목',
            'spec': '사양',
            'item_number': '품목번호',
            'unit': '단위',
            'project_type': '국책과제',
            'quantity': '구매수량',
            'unit_price': '단가',
            'total_price': '총가격',
            'notes': '비고',
            'reason': '사유',
            'requester': '요청자',
            'request_date': '요청일',
            'purchase_status': '구매여부'
        }
        
        # 실제로 존재하는 컬럼만 추출
        export_columns = [col for col in column_mapping.keys() if col in df.columns]
        df_export = df[export_columns].copy()
        
        # 컬럼명을 한글로 변경
        df_export.rename(columns=column_mapping, inplace=True)
        
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
