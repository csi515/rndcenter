from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from database import db, Communication
from datetime import datetime

communication_bp = Blueprint('communication', __name__)

@communication_bp.route('/free')
def free_communication():
    posts = Communication.query.filter_by(category='자유소통').order_by(Communication.created_date.desc()).all()
    return render_template('communication/free.html', posts=posts)

@communication_bp.route('/free/add', methods=['POST'])
def add_free_post():
    try:
        new_post = Communication(
            comm_id=datetime.now().strftime('%Y%m%d%H%M%S%f'),
            category='자유소통',
            title=request.form.get('title'),
            content=request.form.get('content'),
            author=request.form.get('author', '익명'),
            created_date=datetime.now(),
            views=0,
            status='공개'
        )
        db.session.add(new_post)
        db.session.commit()
        flash('게시글이 성공적으로 등록되었습니다.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('게시글 등록 중 오류가 발생했습니다.', 'error')
    return redirect(url_for('communication.free_communication'))

@communication_bp.route('/safety_qa')
def safety_qa():
    posts = Communication.query.filter_by(category='안전 Q&A').order_by(Communication.created_date.desc()).all()
    posts_json = [
        {
            'id': p.id,
            'comm_id': p.comm_id,
            'category': p.category,
            'title': p.title,
            'content': p.content,
            'author': p.author,
            'question_type': p.question_type,
            'urgency': p.urgency,
            'created_date': p.created_date.strftime('%Y-%m-%d %H:%M') if p.created_date else '',
            'views': p.views,
            'status': p.status,
            'answer': p.answer  # answer 필드 추가
        }
        for p in posts
    ]
    return render_template('communication/safety_qa.html', posts=posts, posts_json=posts_json)

@communication_bp.route('/safety_qa/add', methods=['POST'])
def add_safety_qa():
    try:
        new_qa = Communication(
            comm_id=datetime.now().strftime('%Y%m%d%H%M%S%f'),
            category='안전 Q&A',
            title=request.form.get('title'),
            content=request.form.get('content'),
            author=request.form.get('author', '익명'),
            question_type=request.form.get('question_type', '일반'),
            urgency=request.form.get('urgency', '보통'),
            created_date=datetime.now(),
            views=0,
            status='답변대기'
        )
        db.session.add(new_qa)
        db.session.commit()
        flash('질문이 성공적으로 등록되었습니다.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('질문 등록 중 오류가 발생했습니다.', 'error')
    return redirect(url_for('communication.safety_qa'))

@communication_bp.route('/safety_qa/answer/<int:post_id>', methods=['POST'])
def answer_safety_qa(post_id):
    try:
        post = Communication.query.get_or_404(post_id)
        data = request.get_json()
        answer = data.get('answer', '').strip()
        if not answer:
            return jsonify({'success': False, 'message': '답변 내용이 비어 있습니다.'}), 400
        post.answer = answer
        post.status = '답변완료'
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@communication_bp.route('/safety_qa/answer/<int:post_id>/edit', methods=['POST'])
def edit_answer_safety_qa(post_id):
    try:
        post = Communication.query.get_or_404(post_id)
        data = request.get_json()
        answer = data.get('answer', '').strip()
        if not answer:
            return jsonify({'success': False, 'message': '답변 내용이 비어 있습니다.'}), 400
        post.answer = answer
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
