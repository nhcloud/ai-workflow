"""
Group Chat Workflow Module

Demonstrates a group chat orchestration where multiple specialized agents
collaborate iteratively, coordinated by a central manager that selects
the next speaker and decides when to terminate.

Reference:
https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/group-chat
"""

from .executors import (
    GroupChatParticipant,
    RoundRobinManager,
    ApprovalBasedManager,
    GroupChatMessage,
)
from .demo import GroupChatWorkflowDemo

__all__ = [
    "GroupChatParticipant",
    "RoundRobinManager",
    "ApprovalBasedManager",
    "GroupChatMessage",
    "GroupChatWorkflowDemo",
]
