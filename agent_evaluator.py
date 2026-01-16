def evaluate_response(
    user_query: str,
    agent_response: dict,
    source: str,
    retrieved_context=None,
    tools_used=None
):
    """
    Evaluates whether the agent response is supported by
    retrieved knowledge or calendar data.
    """

    evaluation = {
        "confidence_score": 0.0,
        "explanation": "",
        "references": [],
        "result": "FAIL"
    }

    # Case 1: Knowledge-based (RAG)
    if source == "knowledge_base":
        if retrieved_context and agent_response.get("answer"):
            evaluation["confidence_score"] = 0.95
            evaluation["explanation"] = (
                "The response is fully supported by retrieved documents "
                "from the knowledge base."
            )
            evaluation["references"] = retrieved_context
            evaluation["result"] = "PASS"
        else:
            evaluation["confidence_score"] = 0.3
            evaluation["explanation"] = (
                "The response lacks sufficient retrieved context."
            )

    # Case 2: Calendar-based (MCP tools)
    elif source == "calendar":
        if tools_used:
            evaluation["confidence_score"] = 0.9
            evaluation["explanation"] = (
                "The response is supported by Google Calendar data "
                "retrieved using MCP tools."
            )
            evaluation["references"] = tools_used
            evaluation["result"] = "PASS"
        else:
            evaluation["confidence_score"] = 0.4
            evaluation["explanation"] = (
                "No calendar tool usage was detected to support the response."
            )

    else:
        evaluation["explanation"] = "Unknown source type."

    return evaluation
