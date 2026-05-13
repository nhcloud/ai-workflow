"""
Group Chat Workflow Demo - Collaborative Customer Response Drafting

This demonstrates a group chat orchestration where multiple specialized agents
collaborate iteratively to produce a high-quality customer support response:

    Customer Ticket
         |
         v
    +-----------------------------------------+
    |   Group Chat Manager (orchestrator)     |
    |   - selects the next speaker            |
    |   - synchronizes shared conversation    |
    |   - decides when to terminate           |
    +-----------------------------------------+
         ^              ^                ^
         |              |                |
    CopyWriter       ToneCoach        Reviewer
    (drafts reply)   (suggests        (approves or
                      tone tweaks)     critiques)

Concepts covered:
- Centralized speaker selection (round-robin + custom termination)
- Shared conversation history across participants
- Iterative refinement until the Reviewer approves (or max iterations reached)

Reference:
https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/group-chat
"""

import asyncio

from common import create_chat_client
from common.azure_openai_client_factory import get_deployment_name
from common.ticket_loader import (
    display_available_tickets,
    get_ticket_by_index,
    get_random_ticket,
    get_ticket_by_id,
)
from .executors import (
    GroupChatParticipant,
    ApprovalBasedManager,
    GroupChatMessage,
)


class GroupChatWorkflow:
    """Workflow that runs a group chat until the manager signals termination."""

    def __init__(self, manager):
        self.manager = manager

    async def run(self, task: str) -> list[GroupChatMessage]:
        """Execute the group chat and return the full conversation transcript."""
        history: list[GroupChatMessage] = [
            GroupChatMessage(author_name="User", role="user", text=task)
        ]

        while not self.manager.should_terminate(history):
            speaker = self.manager.select_next(history)
            print(f"--- {speaker.name} is thinking... ---")
            reply_text = await speaker.respond(history)
            message = GroupChatMessage(
                author_name=speaker.name,
                role="assistant",
                text=reply_text,
            )
            history.append(message)

            print(f"[{speaker.name}]")
            print(reply_text)
            print()

        return history


class GroupChatWorkflowDemo:
    """Demo class for the group chat workflow."""

    @staticmethod
    async def run_async():
        """Run the group chat workflow demo."""
        print("=== Group Chat Workflow Demo - Collaborative Customer Response ===")
        print()
        print("Multiple specialized agents collaborate via a group chat orchestrator:")
        print("  CopyWriter -> ToneCoach -> Reviewer (approves or sends back for revision)")
        print()

        # Set up the Azure OpenAI client
        client = create_chat_client()
        deployment = get_deployment_name()

        # Define the participants
        copy_writer = GroupChatParticipant(
            client=client,
            deployment=deployment,
            name="CopyWriter",
            description="Drafts customer support replies.",
            instructions=(
                "You are a customer support copywriter. "
                "Draft a professional, empathetic response to the customer's ticket. "
                "If a Reviewer or ToneCoach has provided feedback in the conversation, "
                "produce a revised version that addresses every point of feedback. "
                "Keep responses concise (3-5 sentences) and end with a ticket reference "
                "in the format TKT-XXXXX."
            ),
        )

        tone_coach = GroupChatParticipant(
            client=client,
            deployment=deployment,
            name="ToneCoach",
            description="Coaches tone, warmth, and empathy.",
            instructions=(
                "You are a tone and empathy coach for customer support communications. "
                "Read the most recent draft from the CopyWriter and give 1-3 short, "
                "actionable suggestions to improve warmth, clarity, and customer empathy. "
                "Do NOT rewrite the draft yourself - only provide feedback. "
                "If the draft is already excellent, say 'No tone changes needed.'"
            ),
        )

        reviewer = GroupChatParticipant(
            client=client,
            deployment=deployment,
            name="Reviewer",
            description="Final approver for customer support responses.",
            instructions=(
                "You are the final approver for customer support responses. "
                "Evaluate the most recent CopyWriter draft for accuracy, tone, and policy compliance. "
                "If it fully meets the bar, reply with exactly 'APPROVED' followed by a one-sentence justification. "
                "Otherwise, list specific revisions the CopyWriter must make. "
                "Do NOT say 'APPROVED' unless you are fully satisfied."
            ),
        )

        # Build the group chat workflow with a custom approval-based manager
        manager = ApprovalBasedManager(
            participants=[copy_writer, tone_coach, reviewer],
            approver_name="Reviewer",
            maximum_iteration_count=6,
        )
        workflow = GroupChatWorkflow(manager=manager)

        # Load a ticket from the data file
        display_available_tickets()
        print()
        user_input = input("Enter ticket number (1-5) or press Enter for random: ").strip()

        if not user_input:
            sample_ticket = get_random_ticket()
            print(f"Randomly selected: {sample_ticket.ticket_id}")
        elif user_input.isdigit():
            sample_ticket = get_ticket_by_index(int(user_input))
        else:
            sample_ticket = get_ticket_by_id(user_input) or get_random_ticket()
        print()

        print("Incoming Support Ticket:")
        print(f"   Ticket ID: {sample_ticket.ticket_id}")
        print(f"   Customer: {sample_ticket.customer_name} ({sample_ticket.customer_id})")
        print(f"   Priority: {sample_ticket.priority.value}")
        print(f"   Subject: {sample_ticket.subject}")
        print(f"   Description: {sample_ticket.description}")
        print()

        task = (
            "A new customer support ticket needs a response. Collaborate as a team "
            "(CopyWriter drafts, ToneCoach gives feedback, Reviewer approves or "
            "requests revisions) until the Reviewer approves a final response.\n\n"
            f"Ticket ID: {sample_ticket.ticket_id}\n"
            f"Customer: {sample_ticket.customer_name}\n"
            f"Priority: {sample_ticket.priority.value}\n"
            f"Subject: {sample_ticket.subject}\n"
            f"Description: {sample_ticket.description}"
        )

        print("Starting group chat...")
        print()

        history = await workflow.run(task)

        print("=" * 69)
        print("=== Final Conversation Transcript ===")
        print("=" * 69)
        for msg in history:
            print(f"[{msg.author_name}]: {msg.text}")
            print()

        print("Group chat workflow completed!")


async def main():
    """Entry point for running the demo."""
    await GroupChatWorkflowDemo.run_async()


if __name__ == "__main__":
    asyncio.run(main())
