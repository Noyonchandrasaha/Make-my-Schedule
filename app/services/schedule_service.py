from app.langgraph.agent import create_schedule_agent

class ScheduleService:
    def __init__(self):
        self.agent = None

    async def init_agent(self):
        if self.agent is None:
            self.agent = await create_schedule_agent()

    async def handle_query(self, user_query: str):
        await self.init_agent()
        result = await self.agent.ainvoke({
            "messages": [{"role": "user", "content": user_query}]
        })
        return result
