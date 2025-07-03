from flask import Blueprint, render_template, request, jsonify, send_file
from csv_manager import csv_manager
from datetime import datetime
import os
import uuid
import math
import json
import pandas as pd
import io

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
    req_df = csv_manager.read_csv(PURCHASE_CSV)
    proj_df = csv_manager.read_csv(PROJECT_TYPE_CSV)
    requests = req_df.to_dict('records') if not req_df.empty else []
    project_types = proj_df['project_type'].tolist() if not proj_df.empty else []
    return render_template('purchasing/requests.html', requests=requests, project_types=project_types)

@purchasing_bp.route('/requests/add', methods=['POST'])
def add_purchase_request():
    try:
        data = request.json if request.is_json else request.form
        now = datetime.now()
        
        def safe_str(val):
            """문자열 필드 안전 처리"""
            if val is None or val == '' or (isinstance(val, float) and (math.isnan(val) or math.isinf(val))):
                return ''
            return str(val).strip()
        
        def safe_num(val):
            """숫자 필드 안전 처리"""
            try:
                if val in [None, '', 'NaN', 'nan'] or (isinstance(val, float) and (math.isnan(val) or math.isinf(val))):
                    return 0.0
                num_val = float(val)
                if math.isnan(num_val) or math.isinf(num_val):
                    return 0.0
                return num_val
            except (ValueError, TypeError):
                return 0.0
        
        # 모든 필드를 안전하게 처리
        req = {
            'id': str(uuid.uuid4()),
            'item': safe_str(data.get('item','')),
            'spec': safe_str(data.get('spec','')),
            'item_number': safe_str(data.get('item_number','')),
            'unit': safe_str(data.get('unit','')),
            'project_type': safe_str(data.get('project_type','')),
            'required_qty': safe_num(data.get('required_qty',0)),
            'safety_stock': safe_num(data.get('safety_stock',0)),
            'purchase_qty': safe_num(data.get('purchase_qty',0)),
            'unit_price': safe_num(data.get('unit_price',0)),
            'total_price': safe_num(data.get('purchase_qty',0)) * safe_num(data.get('unit_price',0)),
            'purchase_status': safe_str(data.get('purchase_status','대기')),
            'note': safe_str(data.get('note','')),
            'reason': safe_str(data.get('reason','')),
            'requester': safe_str(data.get('requester','')),
            'request_date': now.strftime('%Y-%m-%d')
        }
        
        # 디버깅: 서버에서 받은 데이터와 처리된 데이터 로그
        print(f"받은 데이터: {data}")
        print(f"처리된 데이터: {req}")
        
        csv_manager.append_to_csv(PURCHASE_CSV, req)
        return safe_jsonify({'success': True, 'data': req})
        
    except Exception as e:
        print(f"구매 요청 추가 에러: {str(e)}")
        return safe_jsonify({'success': False, 'error': str(e)})

@purchasing_bp.route('/requests/update/<req_id>', methods=['POST'])
def update_purchase_request(req_id):
    import pandas as pd
    df = csv_manager.read_csv(PURCHASE_CSV)
    idx = df.index[df['id']==req_id].tolist()
    if not idx:
        return safe_jsonify({'success': False, 'error': '해당 요청 없음'})
    i = idx[0]
    for k in PURCHASE_FIELDS:
        if k in request.json:
            df.at[i, k] = request.json[k]
    df.at[i, 'total_price'] = float(df.at[i, 'purchase_qty']) * float(df.at[i, 'unit_price'])
    csv_manager.write_csv(PURCHASE_CSV, df)
    return safe_jsonify({'success': True})

@purchasing_bp.route('/requests/delete/<req_id>', methods=['POST'])
def delete_purchase_request(req_id):
    import pandas as pd
    df = csv_manager.read_csv(PURCHASE_CSV)
    df = df[df['id'] != req_id]
    csv_manager.write_csv(PURCHASE_CSV, df)
    return safe_jsonify({'success': True})

@purchasing_bp.route('/requests/list', methods=['GET'])
def list_purchase_requests():
    df = csv_manager.read_csv(PURCHASE_CSV)
    # 필터
    item = request.args.get('item')
    spec = request.args.get('spec')
    requester = request.args.get('requester')
    project_type = request.args.get('project_type')
    if item:
        df = df[df['item'].str.contains(item, na=False)]
    if spec:
        df = df[df['spec'].str.contains(spec, na=False)]
    if requester:
        df = df[df['requester'].str.contains(requester, na=False)]
    if project_type:
        df = df[df['project_type'] == project_type]
    return safe_jsonify(df.to_dict('records'))

@purchasing_bp.route('/requests/summary', methods=['GET'])
def purchase_summary():
    df = csv_manager.read_csv(PURCHASE_CSV)
    total_count = len(df)
    total_price = df['total_price'].astype(float).sum() if not df.empty else 0
    return safe_jsonify({'total_count': total_count, 'total_price': total_price})

# 국책과제 종류 관리
@purchasing_bp.route('/project-types/list')
def list_project_types():
    df = csv_manager.read_csv(PROJECT_TYPE_CSV)
    return safe_jsonify(df.to_dict('records'))

@purchasing_bp.route('/project-types/add', methods=['POST'])
def add_project_type():
    import pandas as pd
    df = csv_manager.read_csv(PROJECT_TYPE_CSV)
    new_type = request.json.get('project_type')
    if df['project_type'].eq(new_type).any():
        return safe_jsonify({'success': False, 'error': '이미 존재하는 국책과제 종류입니다.'})
    new_row = {'id': str(uuid.uuid4()), 'project_type': new_type}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    csv_manager.write_csv(PROJECT_TYPE_CSV, df)
    return safe_jsonify({'success': True, 'data': new_row})

@purchasing_bp.route('/project-types/delete/<type_id>', methods=['POST'])
def delete_project_type(type_id):
    import pandas as pd
    df = csv_manager.read_csv(PROJECT_TYPE_CSV)
    df = df[df['id'] != type_id]
    csv_manager.write_csv(PROJECT_TYPE_CSV, df)
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
