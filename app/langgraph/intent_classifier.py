from langchain_core.tools import Tool, StructuredTool

# Example simple intent classifier tool
async def intent_classifier_func(user_input: str) -> str:
    """
    Very basic intent classifier example.
    For production, use LLM classification or ML model.
    """
    text = user_input.lower()
    if any(k in text for k in ["create", "schedule", "set up", "make"]):
        return "create_event"
    elif any(k in text for k in ["update", "change", "edit"]):
        return "update_event"
    elif any(k in text for k in ["delete", "remove", "cancel"]):
        return "delete_event"
    elif any(k in text for k in ["list", "show", "what", "next", "events"]):
        return "list_events"
    else:
        return "unknown"

IntentClassifierTool = Tool(
    name="intent_classifier",
    func=lambda text: intent_classifier_func(text),
    description="Classifies user intent: create_event, update_event, delete_event, list_events"
)
