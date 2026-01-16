import re
from datetime import datetime

from google_calendar_server import (
    list_events,
    search_events,
    create_event
)

from rag_engine import retrieve_context
from agent_evaluator import evaluate_response


# ---------------- HELPER FUNCTIONS ----------------

def parse_date_time(user_query: str):
    """
    Very simple parser for queries like:
    'Create a meeting on January 21st from 10 AM to 11 AM'
    """

    # Extract date
    date_match = re.search(
        r"(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})",
        user_query,
        re.IGNORECASE
    )

    # Extract time
    time_match = re.search(
        r"(\d{1,2})\s*(am|pm)\s*to\s*(\d{1,2})\s*(am|pm)",
        user_query,
        re.IGNORECASE
    )

    if not date_match or not time_match:
        return None

    month, day = date_match.groups()
    sh, s_ampm, eh, e_ampm = time_match.groups()

    year = 2026  # demo year

    start_time = datetime.strptime(f"{sh} {s_ampm}", "%I %p").strftime("%H:%M")
    end_time = datetime.strptime(f"{eh} {e_ampm}", "%I %p").strftime("%H:%M")

    date_obj = datetime.strptime(f"{day} {month} {year}", "%d %B %Y")

    return {
        "date": date_obj.strftime("%Y-%m-%d"),
        "start_time": start_time,
        "end_time": end_time
    }


# ---------------- AGENT ----------------

def agent_decide_and_act(user_query: str):
    query = user_query.lower()
    print(f"[Agent] Received query: {user_query}")

    # 🔹 CALENDAR INTENTS
    if any(word in query for word in ["event", "events", "calendar", "meeting", "schedule", "create"]):

        # LIST EVENTS
        if any(word in query for word in ["list", "show", "what"]):
            print("[Agent Reasoning] User wants to see events")
            print("[Agent Action] Calling list_events tool")

            events = list_events("2026-01-01", "2026-01-31")

            evaluation = evaluate_response(
                user_query=user_query,
                agent_response=events,
                source="calendar",
                tools_used=["list_events"]
            )

            return {"response": events, "evaluation": evaluation}

        # SEARCH EVENTS
        if any(word in query for word in ["search", "find"]):
            print("[Agent Reasoning] User wants to search events")
            print("[Agent Action] Calling search_events tool")

            events = search_events("Project")

            evaluation = evaluate_response(
                user_query=user_query,
                agent_response=events,
                source="calendar",
                tools_used=["search_events"]
            )

            return {"response": events, "evaluation": evaluation}

        # CREATE EVENT
        if any(word in query for word in ["create", "schedule"]):
            print("[Agent Reasoning] User wants to create an event")

            parsed = parse_date_time(user_query)

            if not parsed:
                return {
                    "response": {
                        "message": "Could not understand date/time. Please try a clearer format."
                    },
                    "evaluation": {"status": "failed"}
                }

            print("[Agent Action] Calling create_event tool")

            result = create_event(
                title="Meeting",
                date=parsed["date"],
                start_time=parsed["start_time"],
                end_time=parsed["end_time"],
                description="Created by Agentic Calendar Assistant",
                location="Home"
            )

            evaluation = evaluate_response(
                user_query=user_query,
                agent_response=result,
                source="calendar",
                tools_used=["create_event"]
            )

            return {"response": result, "evaluation": evaluation}

    # 🔹 KNOWLEDGE (RAG)
    if any(word in query for word in ["what", "explain", "how"]):
        print("[Agent Reasoning] Knowledge-based question detected")

        context = retrieve_context(user_query)

        response = {"answer": context, "source": "knowledge_base"}

        evaluation = evaluate_response(
            user_query=user_query,
            agent_response=response,
            source="knowledge_base",
            retrieved_context=context
        )

        return {"response": response, "evaluation": evaluation}

    return {
        "response": {"message": "Agent could not determine intent"},
        "evaluation": {"status": "failed"}
    }


# ---------------- INTERACTIVE MODE ----------------

if __name__ == "__main__":
    print("=== Agentic Calendar Assistant ===")
    print("Type your query below (type 'exit' to quit)\n")

    while True:
        user_query = input("You: ")

        if user_query.lower() in ["exit", "quit"]:
            print("Exiting Agentic Calendar Assistant.")
            break

        response = agent_decide_and_act(user_query)

        print("\n[Agent Result]")
        print(response)
        print("-" * 50)





# from google_calendar_server import (
#     list_events,
#     search_events,
#     create_event
# )

# from rag_engine import retrieve_context
# from agent_evaluator import evaluate_response

# def agent_decide_and_act(user_query: str):
#     """
#     Agent brain: decides whether to use RAG or calendar tools,
#     executes action, and evaluates the response.
#     """
#     query = user_query.lower()
#     print(f"[Agent] Received query: {user_query}")

#     # --------------------------------------------------
#     # 🔹 PRIORITY 1: CALENDAR-RELATED INTENTS
#     # --------------------------------------------------
#     if any(word in query for word in ["event", "events", "calendar", "meeting", "schedule", "create"]):

#         # 🔹 LIST EVENTS
#         if any(word in query for word in ["list", "show", "what"]):
#             print("[Agent Reasoning] User wants to see events")
#             print("[Agent Action] Calling list_events tool")

#             try:
#                 events = list_events("2026-01-01", "2026-01-15")
#             except FileNotFoundError:
#                 return {
#                     "response": {
#                         "message": "Google Calendar credentials not provided."
#                     },
#                     "evaluation": {
#                         "status": "skipped",
#                         "reason": "Missing credentials.json"
#                     }
#                 }

#             evaluation = evaluate_response(
#                 user_query=user_query,
#                 agent_response=events,
#                 source="calendar",
#                 tools_used=["list_events"]
#             )

#             return {
#                 "response": events,
#                 "evaluation": evaluation
#             }

#         # 🔹 SEARCH EVENTS
#         if any(word in query for word in ["search", "find"]):
#             print("[Agent Reasoning] User wants to search events")
#             print("[Agent Action] Calling search_events tool")

#             events = search_events("Project")

#             evaluation = evaluate_response(
#                 user_query=user_query,
#                 agent_response=events,
#                 source="calendar",
#                 tools_used=["search_events"]
#             )

#             return {
#                 "response": events,
#                 "evaluation": evaluation
#             }

#         # 🔹 CREATE EVENT (DEMO-SAFE & CORRECT)
#         if any(word in query for word in ["create", "schedule"]):
#             print("[Agent Reasoning] User wants to create an event")
#             print("[Agent Action] Calling create_event tool")

#             # NOTE:
#             # NLP date parsing is not implemented yet.
#             # For now, we use a fixed demo slot that matches user intent.
#             result = create_event(
#                 title="Demo Meeting",
#                 date="2026-01-10",
#                 start_time="02:00",
#                 end_time="03:00",
#                 description="Created by Agentic Calendar Assistant",
#                 location="Home"
#             )

#             evaluation = evaluate_response(
#                 user_query=user_query,
#                 agent_response=result,
#                 source="calendar",
#                 tools_used=["create_event"]
#             )

#             return {
#                 "response": result,
#                 "evaluation": evaluation
#             }

#     # --------------------------------------------------
#     # 🔹 PRIORITY 2: KNOWLEDGE / RAG QUESTIONS
#     # --------------------------------------------------
#     if any(word in query for word in ["what", "explain", "how"]):
#         print("[Agent Reasoning] Knowledge-based question detected")

#         context = retrieve_context(user_query)

#         response = {
#             "answer": context,
#             "source": "knowledge_base"
#         }

#         evaluation = evaluate_response(
#             user_query=user_query,
#             agent_response=response,
#             source="knowledge_base",
#             retrieved_context=context
#         )

#         return {
#             "response": response,
#             "evaluation": evaluation
#         }

#     # --------------------------------------------------
#     # 🔹 FALLBACK
#     # --------------------------------------------------
#     return {
#         "response": {"message": "Agent could not determine intent"},
#         "evaluation": {"status": "failed", "reason": "Unknown intent"}
#     }


# # --------------------------------------------------
# # 🔹 INTERACTIVE MODE
# # --------------------------------------------------
# if __name__ == "__main__":
#     print("=== Agentic Calendar Assistant ===")
#     print("Type your query below (type 'exit' to quit)\n")

#     while True:
#         user_query = input("You: ")

#         if user_query.lower() in ["exit", "quit"]:
#             print("Exiting Agentic Calendar Assistant.")
#             break

#         response = agent_decide_and_act(user_query)

#         print("\n[Agent Result]")
#         print(response)
#         print("-" * 50)

















# from google_calendar_server import (
#     list_events,
#     get_event_details,
#     search_events,
#     create_event
# )

# from rag_engine import retrieve_context
# from agent_evaluator import evaluate_response


# def agent_decide_and_act(user_query: str):
#     """
#     Agent brain: decides whether to use RAG or calendar tools,
#     executes action, and evaluates the response.
#     """
#     query = user_query.lower()

#     print(f"[Agent] Received query: {user_query}")

#     # 🔹 RAG-based knowledge questions
#     if "what" in query or "explain" in query:
#         print("[Agent Reasoning] Knowledge-based question detected")

#         context = retrieve_context(user_query)

#         response = {
#             "answer": context,
#             "source": "knowledge_base"
#         }

#         evaluation = evaluate_response(
#             user_query=user_query,
#             agent_response=response,
#             source="knowledge_base",
#             retrieved_context=context
#         )

#         return {
#             "response": response,
#             "evaluation": evaluation
#         }

#     # 🔹 List calendar events
#     if "show" in query or "list" in query:
#         print("[Agent Reasoning] User wants to see events")
#         print("[Agent Action] Calling list_events tool")

#         events = list_events("2026-01-01", "2026-01-07")

#         evaluation = evaluate_response(
#             user_query=user_query,
#             agent_response=events,
#             source="calendar",
#             tools_used=["list_events"]
#         )

#         return {
#             "response": events,
#             "evaluation": evaluation
#         }

#     # 🔹 Search events
#     if "search" in query or "find" in query:
#         print("[Agent Reasoning] User wants to search events")
#         print("[Agent Action] Calling search_events tool")

#         events = search_events("Project")

#         evaluation = evaluate_response(
#             user_query=user_query,
#             agent_response=events,
#             source="calendar",
#             tools_used=["search_events"]
#         )

#         return {
#             "response": events,
#             "evaluation": evaluation
#         }

#     # 🔹 Create event
#     if "create" in query or "schedule" in query:
#         print("[Agent Reasoning] User wants to create an event")
#         print("[Agent Action] Calling create_event tool")

#         result = create_event(
#             title="Study Session",
#             date="2026-01-05",
#             start_time="18:00",
#             end_time="19:00",
#             description="Scheduled by agent",
#             location="Home"
#         )

#         evaluation = evaluate_response(
#             user_query=user_query,
#             agent_response=result,
#             source="calendar",
#             tools_used=["create_event"]
#         )

#         return {
#             "response": result,
#             "evaluation": evaluation
#         }

#     # 🔹 Fallback
#     return {
#         "response": {"message": "Agent could not determine intent"},
#         "evaluation": {"status": "failed", "reason": "Unknown intent"}
#     }

# if __name__ == "__main__":
#     print("=== Agentic Calendar Assistant ===")
#     print("Type your query below (type 'exit' to quit)\n")

#     while True:
#         user_query = input("You: ")

#         if user_query.lower() in ["exit", "quit"]:
#             print("Exiting Agentic Calendar Assistant.")
#             break

#         response = agent_decide_and_act(user_query)

#         print("\n[Agent Result]")
#         print(response)
#         print("-" * 50)


# # 🧪 Step 5.4: Test Agentic Evaluation (RAG)
# if __name__ == "__main__":
#     response = agent_decide_and_act(
#         "Explain what the Agentic Calendar Assistant does"
#     )

#     print("\n[Agent Result]")
#     print(response)