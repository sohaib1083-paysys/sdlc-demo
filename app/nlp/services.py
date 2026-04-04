from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

class NLPService:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))

    def interpret_user_request(self, request):
        tokens = word_tokenize(request.text)
        tokens = [token for token in tokens if token not in self.stop_words]
        response = ' '.join(tokens)
        return response
