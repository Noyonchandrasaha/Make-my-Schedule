from pydantic import BaseModel, Field, ValidationError
from typing import Optional, List
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

class Reminder(BaseModel):
    method: str  # e.g., "email", "popup"
    minutes: int

class CreateEventInput(BaseModel):
    summary: str = Field(..., description="Title of the event")
    start_time: str = Field(..., description="Start time in ISO 8601 format")
    end_time: Optional[str] = Field(None, description="End time in ISO 8601 format")
    location: Optional[str] = Field(None, description="Location of the event")
    description: Optional[str] = Field(None, description="Description of the event")
    color_id: Optional[str] = Field(None, description="Event color ID based on importance")
    status: Optional[str] = Field("busy", description="Event status, default is 'busy'")
    reminders: Optional[List[Reminder]] = Field(None, description="List of reminders for the event")

create_event_parser = PydanticOutputParser(pydantic_object=CreateEventInput)

create_event_prompt_template = """
You are a helpful assistant that extracts calendar event details from a user's input.

User input: "{user_input}"

Instructions:
- Extract the event title (summary). If missing, generate a meaningful title based on the input.
- Extract start_time and end_time in ISO 8601 format (YYYY-MM-DDTHH:MM:SS).
- Extract location if available.
- Extract or generate a brief description summarizing the event.
- Determine the importance of the meeting and set 'color_id' accordingly:
    * Use colorId "11" for high importance (urgent/important)
    * Use colorId "7" for medium importance
    * Use colorId "5" for normal/low importance or if unclear
- If 'status' is missing, default to "busy".
- You can omit reminders or set it to null if not specified.

Return ONLY a JSON object with the fields:
summary, start_time, end_time, location, description, color_id, status, reminders

Example output:
{{
  "summary": "Project kickoff meeting",
  "start_time": "2025-07-04T10:00:00",
  "end_time": "2025-07-04T11:00:00",
  "location": "Conference Room 2",
  "description": "Discuss project objectives and timeline.",
  "color_id": "11",
  "status": "busy",
  "reminders": null
}}
"""

create_event_prompt = PromptTemplate(
    input_variables=["user_input"],
    template=create_event_prompt_template,
)

def parse_create_event(llm_output: str) -> CreateEventInput:
    try:
        return create_event_parser.parse(llm_output)
    except ValidationError as e:
        raise ValueError(f"Parsing failed: {e}")
