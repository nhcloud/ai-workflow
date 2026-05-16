"""
Group Chat Executors

Lightweight, dependency-free implementation of the group chat orchestration
pattern, mirroring the shape of `agent_framework.orchestrations.GroupChatBuilder`
but built directly on top of the Azure OpenAI client to stay consistent with
the other demos in this lab.

Reference:
https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/group-chat
"""

from dataclasses import dataclass, field
from typing import Callable, Optional
from openai import AzureOpenAI


@dataclass
class GroupChatMessage:
    """A single message in the shared group chat history."""
    author_name: str
    role: str  # "user" or "assistant"
    text: str


class GroupChatParticipant:
    """
    A specialized agent that participates in the group chat.

    All participants share the full conversation history before each turn,
    matching the context-synchronization behavior described in the docs.
    """

    def __init__(
        self,
        client: AzureOpenAI,
        deployment: str,
        name: str,
        description: str,
        instructions: str,
    ):
        self.client = client
        self.deployment = deployment
        self.name = name
        self.description = description
        self.instructions = instructions

    async def respond(self, history: list[GroupChatMessage]) -> str:
        """Generate a response given the full shared conversation history."""
        # Build OpenAI-style messages: a system prompt that includes role
        # awareness, then the entire shared history relabeled so the model
        # sees who said what.
        system_prompt = (
            f"{self.instructions}\n\n"
            f"You are participating in a group chat as '{self.name}'. "
            f"Other participants' messages appear prefixed with their name. "
            f"Respond only as {self.name}; do not impersonate others."
        )

        messages: list[dict] = [{"role": "system", "content": system_prompt}]

        for msg in history:
            if msg.role == "user":
                messages.append({"role": "user", "content": msg.text})
            elif msg.author_name == self.name:
                messages.append({"role": "assistant", "content": msg.text})
            else:
                # Other participants' messages -> show as user-visible context
                messages.append({
                    "role": "user",
                    "content": f"[{msg.author_name}]: {msg.text}",
                })

        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=messages,
            max_completion_tokens=400,
        )
        return response.choices[0].message.content or ""


# --------------------------------------------------------------------------- #
# Group chat managers (analogous to RoundRobinGroupChatManager in .NET)
# --------------------------------------------------------------------------- #


class RoundRobinManager:
    """
    Selects the next speaker in round-robin order and terminates when the
    maximum iteration count is reached.
    """

    def __init__(self, participants: list[GroupChatParticipant], maximum_iteration_count: int = 6):
        self.participants = participants
        self.maximum_iteration_count = maximum_iteration_count
        self._turn_index = 0

    def select_next(self, history: list[GroupChatMessage]) -> GroupChatParticipant:
        speaker = self.participants[self._turn_index % len(self.participants)]
        self._turn_index += 1
        return speaker

    def should_terminate(self, history: list[GroupChatMessage]) -> bool:
        # Count assistant messages (i.e., turns taken by participants)
        assistant_turns = sum(1 for m in history if m.role == "assistant")
        return assistant_turns >= self.maximum_iteration_count


class ApprovalBasedManager(RoundRobinManager):
    """
    Round-robin selection that terminates early when a designated approver
    posts an approval keyword. Mirrors the C# `ApprovalBasedManager` example
    from the Agent Framework documentation.
    """

    def __init__(
        self,
        participants: list[GroupChatParticipant],
        approver_name: str,
        approval_keyword: str = "APPROVED",
        maximum_iteration_count: int = 6,
    ):
        super().__init__(participants, maximum_iteration_count)
        self.approver_name = approver_name
        self.approval_keyword = approval_keyword.lower()

    def should_terminate(self, history: list[GroupChatMessage]) -> bool:
        if super().should_terminate(history):
            return True
        last = history[-1] if history else None
        if last is None:
            return False
        return (
            last.author_name == self.approver_name
            and self.approval_keyword in last.text.lower()
        )
