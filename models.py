from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name_en = db.Column(db.String(100), nullable=False)
    name_zh = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    terms = db.relationship('Term', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<Category {self.name_en}>'

class Term(db.Model):
    __tablename__ = 'terms'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Chinese terms
    chinese_simplified = db.Column(db.String(200), nullable=False, index=True)
    chinese_traditional = db.Column(db.String(200), index=True)
    pinyin = db.Column(db.String(300), index=True)
    
    # English terms
    english_term = db.Column(db.String(300), nullable=False, index=True)
    english_aliases = db.Column(db.Text)  # Comma-separated alternative translations
    
    # Detailed information
    definition_en = db.Column(db.Text)
    definition_zh = db.Column(db.Text)
    etymology = db.Column(db.Text)
    clinical_notes = db.Column(db.Text)
    
    # Classification
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    subcategory = db.Column(db.String(100))
    
    # Source and reliability
    source = db.Column(db.String(500))
    who_standard = db.Column(db.Boolean, default=False)
    reliability_score = db.Column(db.Integer, default=3)  # 1-5 scale
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Full-text search helper
    search_text = db.Column(db.Text, index=True)
    
    def __repr__(self):
        return f'<Term {self.chinese_simplified} - {self.english_term}>'
    
    def update_search_text(self):
        """Combine all searchable fields into one text field"""
        parts = [
            self.chinese_simplified or '',
            self.chinese_traditional or '',
            self.pinyin or '',
            self.english_term or '',
            self.english_aliases or '',
            self.definition_en or '',
            self.definition_zh or '',
            self.etymology or '',
            self.clinical_notes or ''
        ]
        self.search_text = ' '.join(parts).lower()

class Suggestion(db.Model):
    __tablename__ = 'suggestions'
    
    id = db.Column(db.Integer, primary_key=True)
    term_id = db.Column(db.Integer, db.ForeignKey('terms.id'), nullable=True)
    suggestion_type = db.Column(db.String(50))  # 'new_term', 'correction', 'addition'
    content = db.Column(db.Text, nullable=False)
    submitter_email = db.Column(db.String(200))
    submitter_name = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
