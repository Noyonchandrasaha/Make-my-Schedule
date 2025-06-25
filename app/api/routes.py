from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
from app.core.auth import get_flow, save_token
from app.services.schedule_service import ScheduleService

router = APIRouter()
schedule_service = ScheduleService()

@router.get("/auth/login")
async def login():
    flow = get_flow()
    auth_url, _ = flow.authorization_url(access_type="offline", include_granted_scopes="true")
    return RedirectResponse(auth_url)

@router.get("/auth/callback")
async def callback(request: Request):
    flow = get_flow()
    flow.fetch_token(authorization_response=str(request.url))
    save_token("user123", flow.credentials)
    return {"message": "Authorization successful! You can now close this tab."}

class QueryInput(BaseModel):
    query: str


@router.post("/schedule/query")
async def schedule_query(data: QueryInput):
    result = await schedule_service.handle_query(data.query)

    if isinstance(result, dict) and "messages" in result:
        messages = result["messages"]
        ai_messages = [
            m for m in messages
            if m.__class__.__name__ == "AIMessage" and getattr(m, "content", "").strip()
        ]
        if ai_messages:
            response_text = ai_messages[-1].content
        else:
            response_text = "No response content available."
    elif hasattr(result, "content"):
        response_text = result.content
    elif isinstance(result, str):
        response_text = result
    else:
        response_text = str(result)

    return JSONResponse(content={"response": response_text})
