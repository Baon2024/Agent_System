from dotenv import load_dotenv
import httpx
import io


load_dotenv()



from google import genai
from google.genai import types



clientGemini = genai.Client()


def save_to_gemini(files):
    file_ids = []
    for file in files:
        public_url = file["publicUrl"]
        pdf_bytes = httpx.get(public_url).content
        uploaded_file = clientGemini.files.upload(
            file=io.BytesIO(pdf_bytes),
            config={
                "mime_type": file["file_type"],
                "display_name": file["file_name"],
            },
        )
        file_ids.append(uploaded_file)
    return file_ids