from app.langgraph.agent import create_schedule_agent
from app.langgraph.tools.google_calendar_tools import (
    ListEventsTool,
    CreateEventTool,
    UpdateEventTool,
    DeleteEventTool
)

class ScheduleService:
    def __init__(self):
        self.agent = None

    async def init_agent(self):
        tools = [
            ListEventsTool,
            CreateEventTool,
            UpdateEventTool,  # Added update tool
            DeleteEventTool   # Added delete tool
        ]
        self.agent = await create_schedule_agent(tools)

    async def handle_query(self, user_query: str):
        if not self.agent:
            await self.init_agent()

        result = await self.agent.ainvoke({
            "messages": [{"role": "user", "content": user_query}]
        })
        print("Agent raw result:", result)  # Debug log
        return result
