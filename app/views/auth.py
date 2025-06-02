from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required
from ..models.user import User
from ..models.user import Role
from .. import db

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 验证输入
        if not username or not password:
            flash('请填写所有必填字段')
            return redirect(url_for('auth.register'))
        
        # 验证用户名长度
        if len(username) < 3 or len(username) > 20:
            flash('用户名长度必须在3-20个字符之间')
            return redirect(url_for('auth.register'))
            
        # 验证密码长度
        if len(password) < 6:
            flash('密码长度必须大于6个字符')
            return redirect(url_for('auth.register'))
        
        # 检查用户是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已存在')
            return redirect(url_for('auth.register'))
        
        try:
            # 创建新用户
            user = User(username=username)
            user.set_password(password)
            
            # 设置默认用户角色
            default_role = Role.query.filter_by(name='user').first()
            if default_role:
                user.role = default_role
            
            db.session.add(user)
            db.session.commit()
            
            flash('注册成功！请登录')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('注册失败，请重试')
            print(f"Registration error: {str(e)}")
            return redirect(url_for('auth.register'))
    
    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            if user.status == 'pending':
                flash('您的账号正在等待管理员审批')
                return redirect(url_for('auth.login'))
            elif user.status == 'rejected':
                flash('您的注册申请已被拒绝')
                return redirect(url_for('auth.login'))
            
            login_user(user)
            # 设置 session
            session['username'] = user.username
            session.permanent = True  # 启用永久 session
            
            flash('登录成功！')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            flash('用户名或密码错误')
            
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已退出登录')
    return redirect(url_for('auth.login')) 