#!/usr/bin/python2

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from datetime import datetime

Base = declarative_base()


# Catalog object representing the main categories
class Catalog(Base):

    __tablename__ = "catalog"
    id = Column(Integer, primary_key=True)
    name = Column(String)

    # Add a property decorator to serialize information from this database
    @property
    def serialize(self):

        return {
            'name': self.name,
            'id': self.id
        }


# CatalogItem object representing an item in the catalog
class CatalogItem(Base):

    __tablename__ = 'catalog_item'
    id = Column(Integer, primary_key=True)
    cat_id = Column(Integer, ForeignKey("catalog.id"), nullable=False)
    title = Column(String)
    description = Column(String)
    creator_email = Column(String)
    date_added = Column(String, default=datetime.now())
    catalog = relationship(Catalog)

    # Add a property decorator to serialize information from this database
    @property
    def serialize(self):

        return {
            'cat_id': self.cat_id,
            'title': self.title,
            'description': self.description,
            'id': self.id
        }

engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)
