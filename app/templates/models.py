from sqlalchemy import Column, Integer, String
from app.database import Base

class TemplateModel(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
