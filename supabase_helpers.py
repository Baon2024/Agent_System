from pathlib import Path
from supabase import create_client
import mimetypes

SUPABASE_URL = "https://xmcyvimeuarsivupecuv.supabase.co"
SUPABASE_SERVICE_ROLE_KEY= "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhtY3l2aW1ldWFyc2l2dXBlY3V2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNjUzNjY5NywiZXhwIjoyMDUyMTEyNjk3fQ.S8lA3GEZdnWVzUExHSIl9qE1M72qiu40ITv7_oJGrbE"


supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

bucket = "agent_files"

async def save_file_to_supabase(file_path):
    local_path = Path(file_path).resolve()

    storage_path = f"outputs/{local_path.name}"

    mime_type, _ = mimetypes.guess_type(file_path)

    with open(local_path, "rb") as f:
        supabase.storage.from_(bucket).upload(
            path=storage_path,
            file=f,
            file_options={
                "content-type": mime_type, # so can only save markdown currently
                "upsert": "true",
            },
        )
    
    return storage_path, mime_type

async def get_supabase_public_path(storage_path):
    public_url = supabase.storage.from_(bucket).get_public_url(storage_path)
    return public_url
