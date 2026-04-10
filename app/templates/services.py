from app.templates.models import TemplateModel
from app.database import Session

def get_templates():
    with Session() as session:
        templates = session.query(TemplateModel).all()
        return [{"id": template.id, "name": template.name, "description": template.description} for template in templates]
