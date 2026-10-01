"""LLM Interface（规格第 16 节）。

LLM 不允许决定工具，只基于给定 Artifact 的 Context 回答问题。
默认提供 OpenAI 兼容协议客户端（可指向内网私有化部署端点），不引入任何
Agent / Tool Calling 循环（禁止 4）。
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from abc import ABC, abstractmethod

from .context import artifact_to_context

DEFAULT_TIMEOUT_SECONDS = 60

SYSTEM_PROMPT = (
    "你是企业办公文档分析助手。只依据用户提供的文档内容回答问题；"
    "如果文档中没有相关信息，请明确说明文档中没有该信息，不要编造。"
)


class LLMError(RuntimeError):
    """LLM 调用失败（网络、协议、响应格式等）。"""


class BaseLLMClient(ABC):
    model_name: str = "base"

    @abstractmethod
    def complete(self, system: str, user: str) -> str:
        """最原始的补全接口，子类实现具体协议。"""

    def ask(self, artifact, question: str) -> str:
        """规格 16 节固定流程：Artifact → Context → LLM → 回答。"""
        context = artifact_to_context(artifact)
        user_message = f"{context}\n\n[Question]\n{question}"
        return self.complete(SYSTEM_PROMPT, user_message)


class OpenAICompatibleClient(BaseLLMClient):
    """OpenAI 兼容 chat/completions 协议客户端（stdlib 实现，无额外依赖）。"""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        timeout: int = DEFAULT_TIMEOUT_SECONDS,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.model_name = model

    def complete(self, system: str, user: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0,
        }
        request = urllib.request.Request(
            self.base_url + "/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", "replace")[:500]
            raise LLMError(f"LLM HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise LLMError(f"LLM request failed: {exc.reason}") from exc
        except json.JSONDecodeError as exc:
            raise LLMError(f"LLM returned non-JSON response: {exc}") from exc

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError(f"unexpected LLM response structure: {data!r}") from exc


class MockLLMClient(BaseLLMClient):
    """测试 / 离线演示用：不访问网络，返回固定答案。"""

    def __init__(self, reply: str = "mock answer"):
        self.reply = reply
        self.model_name = "mock"

    def complete(self, system: str, user: str) -> str:
        return self.reply


def client_from_env(env=None) -> BaseLLMClient | None:
    """从环境变量构造客户端；未配置时返回 None（调用方决定降级行为）。

    HMBUDDY_LLM_BASE_URL  例如 https://llm.intranet.example.com/v1
    HMBUDDY_LLM_MODEL     模型名
    HMBUDDY_LLM_API_KEY   API Key（部分内网部署可留空）
    """
    env = os.environ if env is None else env
    base_url = env.get("HMBUDDY_LLM_BASE_URL")
    model = env.get("HMBUDDY_LLM_MODEL")
    if not base_url or not model:
        return None
    return OpenAICompatibleClient(
        base_url, env.get("HMBUDDY_LLM_API_KEY", ""), model
    )
