from groq import Groq, AsyncGroq

from config.config import settings

from google import genai as genai_new

# genai.configure(api_key=settings.gemini_key)
# gemini_model = genai.GenerativeModel('gemini-2.0-flash')

groq_api = AsyncGroq(api_key=settings.groq_key)
gemini_client = genai_new.Client(
    api_key=settings.gemini_key,
    http_options={'api_version': 'v1beta'}
)