from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base
from app.templates.models import TemplateModel

class CustomizationModel(Base):
    __tablename__ = "customizations"

    id = Column(Integer, primary_key=True)
    template_id = Column(Integer, ForeignKey("templates.id"))
    text = Column(String)
    image = Column(String)
    music = Column(String)
    template = relationship("TemplateModel", backref="customizations")
