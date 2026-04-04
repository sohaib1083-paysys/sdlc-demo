from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from app.nlp.schemas import Request

router = APIRouter()

@router.post("/interpret")
async def interpret(request: Request):
    try:
        tokens = word_tokenize(request.text)
        tokens = [token for token in tokens if token not in stopwords.words('english')]
        response = ' '.join(tokens)
        return JSONResponse(content={"response": response}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

class Request(BaseModel):
    text: str
