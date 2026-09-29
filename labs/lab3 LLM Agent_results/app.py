import os
import logging
from datetime import datetime, timezone
import chainlit as cl
from autogen import ConversableAgent, UserProxyAgent

# Suppress AutoGen warning logs
logging.getLogger("autogen.oai.client").setLevel(logging.ERROR)

# ---------------------------------------------------------------------------
# 1. Tool Definition
# ---------------------------------------------------------------------------
def convert_epoch_to_datetime(epoch_ms: float) -> dict[str, str]:
    """Converts a Unix epoch timestamp in milliseconds or seconds to human-readable UTC and ISO 8601 strings.

    Args:
        epoch_ms (float): The Unix epoch timestamp (e.g., 1790519130249 for milliseconds or 1790519130 for seconds).

    Returns:
        dict[str, str]: A dictionary containing formatted UTC, ISO 8601, and local timezone strings.
    """
    try:
        if epoch_ms > 1e11:
            seconds = epoch_ms / 1000.0
        else:
            seconds = epoch_ms

        dt = datetime.fromtimestamp(seconds, tz=timezone.utc)

        return {
            "iso_8601": dt.isoformat(),
            "utc_datetime": dt.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "date": dt.strftime("%Y-%m-%d"),
            "time_utc": dt.strftime("%H:%M:%S.%f")[:-3] + " UTC",
            "epoch_input": str(epoch_ms),
        }
    except Exception as err:
        return {"error": f"Failed to convert epoch timestamp: {err}"}


# ---------------------------------------------------------------------------
# 2. Agent Setup
# ---------------------------------------------------------------------------
def setup_agents():
    api_key = (
        os.getenv("API_KEY") 
        or os.getenv("GEMINI_API_KEY") 
        or os.getenv("GROQ_API_KEY")
    )
    model = os.getenv("MODEL") or os.getenv("LLM_MODEL", "gemini-3.8-flash")
    base_url = os.getenv("API_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")

    llm_config = {
        "config_list": [
            {
                "model": model,
                "api_key": api_key,
                "base_url": base_url,
            }
        ],
        "temperature": 0.0,
    }

    system_message = (
        "You are 'Epoch Time Master', an expert security telemetry and timestamp parsing agent.\n"
        "Your primary job is to assist SOC analysts in interpreting raw epoch timestamps, log timestamps, "
        "and event epochs.\n\n"
        "RULES:\n"
        "1. Whenever a user provides an epoch timestamp (e.g., '1790519130249'), "
        "you MUST invoke the 'convert_epoch_to_datetime' tool to get the exact UTC date and time.\n"
        "2. Do NOT attempt to calculate or guess date-time conversions manually.\n"
        "3. Present the converted UTC and ISO 8601 results clearly to the user in markdown format."
    )

    # Primary assistant agent
    assistant = ConversableAgent(
        name="EpochTimeAgent",
        system_message=system_message,
        llm_config=llm_config,
        human_input_mode="NEVER",
    )

    # UserProxy agent to execute tools and handle loop automatically
    user_proxy = UserProxyAgent(
        name="UserProxy",
        human_input_mode="NEVER",
        code_execution_config=False,
        default_auto_reply="",
        is_termination_msg=lambda x: True if x.get("content") and "TERMINATE" in x.get("content") else False,
    )

    # Register tool with both agents for AG2 auto-execution
    assistant.register_for_llm(name="convert_epoch_to_datetime", description="Converts epoch timestamps to UTC")(convert_epoch_to_datetime)
    user_proxy.register_for_execution(name="convert_epoch_to_datetime")(convert_epoch_to_datetime)

    return assistant, user_proxy


# ---------------------------------------------------------------------------
# 3. Chainlit Interface
# ---------------------------------------------------------------------------
@cl.on_chat_start
async def on_chat_start() -> None:
    assistant, user_proxy = setup_agents()
    cl.user_session.set("assistant", assistant)
    cl.user_session.set("user_proxy", user_proxy)

    await cl.Message(
        content=(
            "👋 **Welcome to Epoch Time Master!**\n\n"
            "I can convert Unix epoch timestamps (in milliseconds or seconds) from log files into human-readable UTC dates.\n\n"
            "**Try asking:**\n"
            "* *\"When did event epoch 1790519130249 happen?\"*"
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message) -> None:
    assistant: ConversableAgent = cl.user_session.get("assistant")
    user_proxy: UserProxyAgent = cl.user_session.get("user_proxy")

    # Initiate conversation loop asynchronously
    chat_result = await cl.make_async(user_proxy.initiate_chat)(
        recipient=assistant,
        message=message.content,
        max_turns=2,
        clear_history=False,
    )

    # Extract the last text response generated by the assistant
    final_response = None
    for msg in reversed(chat_result.chat_history):
        if msg.get("role") == "user" and msg.get("name") == "EpochTimeAgent" and msg.get("content"):
            final_response = msg.get("content")
            break
        elif msg.get("role") == "assistant" and msg.get("content"):
            final_response = msg.get("content")
            break

    await cl.Message(content=final_response or "Successfully processed timestamp.").send()