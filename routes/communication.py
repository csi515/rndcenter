from flask import Blueprint, render_template, request, redirect, url_for, flash
from csv_manager import csv_manager
from datetime import datetime

communication_bp = Blueprint('communication', __name__)

@communication_bp.route('/free')
def free_communication():
    communications_data = csv_manager.read_csv('communications.csv')
    
    if not communications_data.empty:
        free_posts = communications_data[communications_data['category'] == '자유소통']
        posts_list = free_posts.to_dict('records')
    else:
        posts_list = []
    
    return render_template('communication/free.html', posts=posts_list)

@communication_bp.route('/free/add', methods=['POST'])
def add_free_post():
    data = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'category': '자유소통',
        'title': request.form.get('title'),
        'content': request.form.get('content'),
        'author': request.form.get('author', '익명'),
        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'views': 0,
        'status': '공개'
    }
    
    if csv_manager.append_to_csv('communications.csv', data):
        flash('게시글이 성공적으로 등록되었습니다.', 'success')
    else:
        flash('게시글 등록 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('communication.free_communication'))

@communication_bp.route('/safety_qa')
def safety_qa():
    communications_data = csv_manager.read_csv('communications.csv')
    
    if not communications_data.empty:
        qa_posts = communications_data[communications_data['category'] == '안전 Q&A']
        posts_list = qa_posts.to_dict('records')
    else:
        posts_list = []
    
    return render_template('communication/safety_qa.html', posts=posts_list)

@communication_bp.route('/safety_qa/add', methods=['POST'])
def add_safety_qa():
    data = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'category': '안전 Q&A',
        'title': request.form.get('title'),
        'content': request.form.get('content'),
        'author': request.form.get('author', '익명'),
        'question_type': request.form.get('question_type', '일반'),
        'urgency': request.form.get('urgency', '보통'),
        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'views': 0,
        'status': '답변대기'
    }
    
    if csv_manager.append_to_csv('communications.csv', data):
        flash('질문이 성공적으로 등록되었습니다.', 'success')
    else:
        flash('질문 등록 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('communication.safety_qa'))
