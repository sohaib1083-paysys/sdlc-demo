from app.customization.models import CustomizationModel
from app.database import Session

def customize_video(customization: dict):
    with Session() as session:
        # Customize the video using the provided text, image, and music
        customization_model = CustomizationModel(**customization)
        session.add(customization_model)
        session.commit()
        return {"message": "Video customized successfully"}
