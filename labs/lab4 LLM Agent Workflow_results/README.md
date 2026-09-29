# Lab 4: Domain Restriction Workflow - SecOps Incident Triage Assistant

This repository implements a defensive multi-agent **Domain Restriction Workflow** built with **AG2** and **Chainlit**, powered by the **Gemini 3.8 Flash** model.

## 1. Workflow Purpose

The purpose of this workflow is to restrict an enterprise **SecOps Incident Triage Assistant** strictly to defensive cybersecurity operations (e.g., log analysis, CVE explanations, detection rule creation). 

In enterprise environments, exposing a specialized security LLM directly to users risks resource abuse (using security tools for general Q&A) and prompt-injection/jailbreak exploits aimed at generating offensive malware or weaponized exploits. This architecture enforces an explicit policy gate before any query reaches the main domain assistant.

## 2. Agents Description

The application distributes responsibilities across three dedicated agents:

1. **`DomainClassifierAgent` (Gatekeeper):**
   - **Role:** Inspects all incoming user prompts before they reach the main assistant.
   - **Responsibility:** Evaluates intent against strict whitelist/blacklist categories and returns a structured JSON policy decision (`ALLOWED` or `REFUSED`). It does not answer user queries.
2. **`SecOpsAnalystAgent` (Protected Answering Agent):**
   - **Role:** Primary domain expert.
   - **Responsibility:** Handles authorized defensive tasks, such as parsing malicious logs, detailing mitigation strategies, and providing triage assistance.
3. **`RefusalAgent` (Enforcement Agent):**
   - **Role:** Safe fallback handler.
   - **Responsibility:** Generates polite, professional refusals explaining why an out-of-scope or unauthorized query was blocked.

## 3. Workflow Logic

```text
               User Query
                   │
                   ▼
       [ DomainClassifierAgent ]
                   │
         ┌─────────┴─────────┐
         │ Policy Evaluation │
         └─────────┬─────────┘
        ALLOWED    │    REFUSED
     ┌─────────────┘─────┐
     ▼                   ▼
[ SecOpsAnalystAgent ] [ RefusalAgent ]
     │                   │
     └─────────┬─────────┘
               ▼
       Final Chainlit UI