from fastmcp import FastMCP
from googleapiclient.discovery import build
from get_google_auth import get_user_credentials

mcp = FastMCP("gmail")

def gmail_service(creds):
    return build("gmail", "v1", credentials=creds)

@mcp.tool()
def search_emails(query: str, max_results: int = 10):
    service = gmail_service(get_user_credentials())
    res = service.users().messages().list(
        userId="me",
        q=query,
        maxResults=max_results,
    ).execute()

    messages = res.get('messages', [])
    
    results = []
    for msg in messages:
        full = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="full",
            metadataHeaders=["Subject", "From", "Date"],
        ).execute()

        headers = {
            h["name"]: h["value"]
            for h in full.get("payload", {}).get("headers", [])
        }

        results.append({
            "id": full["id"],
            "threadId": full.get("threadId"),
            "subject": headers.get("Subject"),
            "from": headers.get("From"),
            "date": headers.get("Date"),
            "snippet": full.get("snippet"),
        })

    return results

@mcp.tool()
def read_email(message_id: str):
    service = gmail_service(get_user_credentials())
    return service.users().messages().get(
        userId="me",
        id=message_id,
        format="full",
    ).execute()


#if __name__ == "__main__":
    #mcp.run(transport="http")

# or with fastmcp cli - fastmcp run server.py:mcp --transport http


## python -m venv gmail