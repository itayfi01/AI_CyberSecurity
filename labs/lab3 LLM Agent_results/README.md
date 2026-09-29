# Epoch Time Master Agent

## 1. Agent Name
**Epoch Time Master**

## 2. Agent Purpose
The Epoch Time Master agent is designed to assist security analysts, developers, and system administrators by accurately parsing Unix epoch timestamps found in raw telemetry, stream logs, and security events. 

LLMs frequently hallucinate or make arithmetic errors when converting large numeric timestamps into calendar dates. To ensure 100% deterministic accuracy, this agent uses a Python tool to perform exact datetime conversions into standard UTC and ISO 8601 formats.

**Technical Specification:**# Epoch Time Master Agent

## 1. Agent Overview
**Epoch Time Master** is an automated tool-calling agent designed for SOC analysts, incident responders, and system administrators. It parses raw Unix epoch timestamps (in both seconds and milliseconds) from security logs and converts them into precise, deterministic UTC and ISO 8601 datetimes without LLM hallucinations.

---

## 2. Architecture & Design

The application utilizes a **Dual-Agent AG2 (`autogen`)** setup integrated into a **Chainlit** browser UI:

1. **`UserProxyAgent` (`UserProxy`)**: Initiates the conversation loop, automatically detects function calls requested by the model, executes the Python tools locally, and returns function execution outputs to the LLM.
2. **`ConversableAgent` (`EpochTimeAgent`)**: Analyzes user prompts, decides when to trigger tool execution, and synthesizes final human-readable markdown reports for SOC analysts.

---

## 3. Tool Specifications

### `convert_epoch_to_datetime(epoch_ms: float) -> dict[str, str]`
A Python tool that performs exact timestamp math using standard `datetime` and `timezone` modules.

* **Parameters:**
  * `epoch_ms` (`float` / `int`): The numeric Unix epoch timestamp (e.g., `1790519130249` for milliseconds or `103723200` for seconds). Automatically detects millisecond vs. second precision based on scale ($>10^{11}$).
* **Returns:**
  ```json
  {
    "iso_8601": "2026-09-27T14:25:30.249000+00:00",
    "utc_datetime": "2026-09-27 14:25:30 UTC",
    "date": "2026-09-27",
    "time_utc": "14:25:30.249 UTC",
    "epoch_input": "1790519130249"
  }
* **Role:** Security Telemetry Timestamp Assistant
* **Behavior:** Detects raw epoch numbers (seconds or milliseconds) in user queries, invokes the `convert_epoch_to_datetime` tool, and returns clean, structured date-time breakdowns.

---

## 3. Agent Tools

### `convert_epoch_to_datetime(epoch_ms)`
Converts a Unix epoch timestamp in milliseconds or seconds into formatted UTC and ISO 8601 calendar strings.

* **Inputs:**
  * `epoch_ms` (`float` / `int`): The numeric Unix epoch timestamp (e.g., `1790519130249`). Automatically determines whether the input is in milliseconds (> 1e11) or seconds.
* **Outputs:**
  * `dict[str, str]`: A dictionary containing:
    * `iso_8601`: Standard ISO timestamp string (e.g., `"2026-09-27T14:25:30.249000+00:00"`).
    * `utc_datetime`: Formatted UTC string (e.g., `"2026-09-27 14:25:30 UTC"`).
    * `date`: YYYY-MM-DD format.
    * `time_utc`: HH:MM:SS.fff UTC format.

---

## 4. Example Interaction

**User:**
> "When did the security log event with epoch `1790519130249` occur?"

**Tool Step Execution (`convert_epoch_to_datetime`):**
* **Input:** `{"epoch_ms": 1790519130249}`
* **Output:** 
  ```json
  {
    "iso_8601": "2026-09-27T14:25:30.249000+00:00",
    "utc_datetime": "2026-09-27 14:25:30 UTC",
    "date": "2026-09-27",
    "time_utc": "14:25:30.249 UTC",
    "epoch_input": "1790519130249"
  }