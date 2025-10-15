
import os, time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

from agents.helpdesk import HelpdeskAgent
from agents.security import SecurityAgent
from agents.onboarding import OnboardingAgent
from agents.meeting import MeetingAgent
from agents.execassistant import ExecAssistantAgent

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://vllm:8000/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "local-key")

app = FastAPI(title="Enterprise AI Agent Hub (Air-Gapped)")

class LLMClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    async def chat(self, messages, model="internal-llm", temperature=0.2, max_tokens=512):
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"]

llm = LLMClient(OPENAI_BASE_URL, OPENAI_API_KEY)

helpdesk = HelpdeskAgent(llm)
security = SecurityAgent(llm)
onboarding = OnboardingAgent(llm)
meeting = MeetingAgent(llm)
execassistant = ExecAssistantAgent(llm)

class ChatPayload(BaseModel):
    agent: str
    prompt: str
    context: dict | None = None

@app.post("/chat")
async def chat(payload: ChatPayload):
    agents = {
        "helpdesk": helpdesk,
        "security": security,
        "onboarding": onboarding,
        "meeting": meeting,
        "execassistant": execassistant,
    }
    agent = agents.get(payload.agent)
    if not agent:
        raise HTTPException(400, f"Unknown agent: {payload.agent}")
    try:
        result = await agent.run(payload.prompt, payload.context or {})
        return {"ok": True, "agent": payload.agent, "result": result}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.get("/healthz")
def health():
    return {"ok": True, "time": time.time()}
