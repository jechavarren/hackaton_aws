from pipeline import analyzer

result = analyzer("Noah Rhodes")

for msg in result["messages"]:
    if hasattr(msg, "content"):
        print(f"{msg.type.upper()}: {msg.content}")