"""llm 包：LLM Interface 与 Context 构造（规格第 16、17 节）。

第一阶段 LLM 不决定工具：流程固定为 用户指定文件 → read_artifact → Artifact →
Context → LLM → 回答。
"""
from .client import (
    BaseLLMClient,
    LLMError,
    MockLLMClient,
    OpenAICompatibleClient,
    client_from_env,
)
from .context import artifact_to_context

__all__ = [
    "BaseLLMClient",
    "LLMError",
    "MockLLMClient",
    "OpenAICompatibleClient",
    "client_from_env",
    "artifact_to_context",
]
