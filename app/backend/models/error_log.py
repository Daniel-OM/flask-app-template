import datetime as dt
from app import db

class ErrorLog(db.Model):
    __tablename__: str = 'error_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Text, nullable=True)
    text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=dt.datetime.now(dt.timezone.utc), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    deleted_at = db.Column(db.DateTime, nullable=True)
    active = db.Column(db.Boolean, default=True)

    user = db.relationship('user', backref=db.backref('error_log_user_rel', lazy=True))

    def __repr__(self) -> str:
        return f'<ErrorLog {self.id}>'
