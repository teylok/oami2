from sqlalchemy import Column, ForeignKey, Integer, String, UnicodeText, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Journal(Base):
    __tablename__ = 'journal'
    title = Column(UnicodeText, primary_key=True)
    articles = relationship('Article')

class Category(Base):
    __tablename__ = 'category'
    name = Column(UnicodeText, primary_key=True)
    articles = relationship('Article', secondary='article_category')

class Article(Base):
    __tablename__ = 'article'
    name = Column(UnicodeText)
    doi = Column(UnicodeText)
    title = Column(UnicodeText, primary_key=True)
    contrib_authors = Column(UnicodeText, primary_key=True)
    abstract = Column(UnicodeText)
    year = Column(Integer)  # should always be there
    month = Column(Integer)  # or None
    day = Column(Integer)  # or None
    url = Column(UnicodeText)
    license_url = Column(UnicodeText)
    license_text = Column(UnicodeText)
    copyright_statement = Column(UnicodeText)
    copyright_holder = Column(UnicodeText)
    journal_title = Column(UnicodeText, ForeignKey('journal.title'))
    journal = relationship('Journal', backref='articles')
    supplementary_materials = relationship('SupplementaryMaterial')
    categories = relationship('Category', secondary='article_category')

    def __repr__(self):
        return '<Article "{}">'.format(self.title)

class SupplementaryMaterial(Base):
    __tablename__ = 'supplementary_material'
    label = Column(UnicodeText)
    title = Column(UnicodeText)
    caption = Column(UnicodeText)
    mimetype = Column(UnicodeText)
    mime_subtype = Column(UnicodeText)
    mimetype_reported = Column(UnicodeText)
    mime_subtype_reported = Column(UnicodeText)
    url = Column(UnicodeText, primary_key=True)
    article_title = Column(UnicodeText, ForeignKey('article.title'))
    article = relationship('Article', backref='supplementary_materials')
    downloaded = Column(Boolean, default=False)
    converting = Column(Boolean, default=False)
    converted = Column(Boolean, default=False)
    uploaded = Column(Boolean, default=False)

    def __repr__(self):
        return '<SupplementaryMaterial "{}" of Article "{}">'.format(self.label, self.article.title)
