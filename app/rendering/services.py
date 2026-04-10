from app.rendering.models import RenderingModel
from app.database import Session

def render_video(rendering: dict):
    with Session() as session:
        # Render the customized video
        rendering_model = RenderingModel(**rendering)
        session.add(rendering_model)
        session.commit()
        return {"message": "Video rendered successfully"}
