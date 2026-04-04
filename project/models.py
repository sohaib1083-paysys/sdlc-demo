from pydantic import BaseModel

class SDLCPhase(BaseModel):
    """
    Represents an SDLC phase.

    Attributes:
        name (str): The name of the phase.
        description (str): A brief description of the phase.
        order (int): The order of the phase in the SDLC process.
    """
    name: str
    description: str
    order: int
