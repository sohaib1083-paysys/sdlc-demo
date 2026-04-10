from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base
from app.customization.models import CustomizationModel

class RenderingModel(Base):
    __tablename__ = "renderings"

    id = Column(Integer, primary_key=True)
    customization_id = Column(Integer, ForeignKey("customizations.id"))
    customization = relationship("CustomizationModel", backref="renderings")
