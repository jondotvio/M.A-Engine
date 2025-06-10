"""Backbone abstractions for grok and openai.

Kept thin and protocol-based so swapping models is just a class swap.
Different style choice from Judge Network (which used standalone clients):
here the backbones are protocols + concrete impls.
"""
from __future__ import annotations

import os
from typing import Protocol, runtime_checkable

import httpx


@runtime_checkable
class Backbone(Protocol):
    name: str

    async def complete(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 256,
    ) -> str: ...


class _BaseHttpBackbone:
    """Shared HTTP plumbing for OpenAI-compatible chat APIs."""

    def __init__(self, base_url: str, model: str, api_key_env: str, timeout: float = 60.0):
        key = os.environ.get(api_key_env)
        if not key:
            raise RuntimeError(f"missing env var: {api_key_env}")
        self._key = key
        self._base = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout

    async def _post(self, path: str, body: dict) -> dict:
        headers = {"Authorization": f"Bearer {self._key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(f"{self._base}{path}", json=body, headers=headers)
            resp.raise_for_status()
            return resp.json()

    async def _chat(self, messages: list[dict], temperature: float, max_tokens: int) -> str:
        body = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        data = await self._post("/chat/completions", body)
        return data["choices"][0]["message"]["content"]


class OpenAIBackbone(_BaseHttpBackbone):
    name = "openai"

    def __init__(self, model: str = "gpt-4o"):
        super().__init__(
            base_url="https://api.openai.com/v1",
            model=model,
            api_key_env="OPENAI_API_KEY",
        )

    async def complete(self, messages, temperature=0.7, max_tokens=256) -> str:
        return await self._chat(messages, temperature, max_tokens)


class GrokBackbone(_BaseHttpBackbone):
    name = "grok"

    def __init__(self, model: str = "grok-4"):
        super().__init__(
            base_url="https://api.x.ai/v1",
            model=model,
            api_key_env="XAI_API_KEY",
        )

    async def complete(self, messages, temperature=0.7, max_tokens=256) -> str:
        return await self._chat(messages, temperature, max_tokens)


