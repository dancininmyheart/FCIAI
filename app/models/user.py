from datetime import datetime
import pytz
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db

# 角色-权限关联表
role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'))
)

class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    permissions = db.relationship('Permission', secondary=role_permissions, backref='roles')

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role', backref='users')
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    register_time = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(pytz.timezone('Asia/Shanghai')))
    approve_time = db.Column(db.DateTime(timezone=True))
    approve_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    approve_user = db.relationship('User', remote_side=[id], backref='approved_users')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def has_permission(self, permission_name):
        if not self.role:
            return False
        return any(p.name == permission_name for p in self.role.permissions)

    @property
    def is_active(self):
        return self.status == 'approved'

    def is_administrator(self):
        """
        检查用户是否是管理员
        优化版本：避免懒加载，直接比较role_id
        """
        if not self.role_id:
            return False

        # 使用缓存的管理员角色ID，避免每次查询数据库
        if not hasattr(self.__class__, '_admin_role_id'):
            admin_role = Role.query.filter_by(name='admin').first()
            self.__class__._admin_role_id = admin_role.id if admin_role else None

        return self.role_id == self.__class__._admin_role_id