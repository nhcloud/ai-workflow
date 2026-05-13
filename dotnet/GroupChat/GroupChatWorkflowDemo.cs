using Microsoft.Agents.AI;
using Microsoft.Agents.AI.Workflows;
using Microsoft.Extensions.AI;
using WorkflowLab.Common;

namespace WorkflowLab.GroupChat;

/// <summary>
/// Group Chat Workflow Demo - Collaborative Customer Response Drafting
///
/// This demonstrates a group chat orchestration where multiple specialized agents
/// collaborate iteratively to produce a high-quality customer support response:
///
///   Customer Ticket
///        │
///        ▼
///   ┌─────────────────────────────────────────┐
///   │   Group Chat Orchestrator (manager)     │
///   │   - selects the next speaker            │
///   │   - synchronizes shared conversation    │
///   │   - decides when to terminate           │
///   └─────────────────────────────────────────┘
///        ▲              ▲                ▲
///        │              │                │
///   CopyWriter       Reviewer        ToneCoach
///   (drafts reply)   (approves       (suggests
///                     or critiques)   tone tweaks)
///
/// Concepts covered:
/// - AgentWorkflowBuilder.CreateGroupChatBuilderWith
/// - RoundRobinGroupChatManager + custom termination (ApprovalBasedManager)
/// - Shared conversation history across participants
/// - Iterative refinement until reviewer approves (or max iterations reached)
///
/// Reference:
/// https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/group-chat
/// </summary>
public static class GroupChatWorkflowDemo
{
    public static async Task RunAsync()
    {
        Console.WriteLine("=== Group Chat Workflow Demo - Collaborative Customer Response ===");
        Console.WriteLine();
        Console.WriteLine("Multiple specialized agents collaborate via a group chat orchestrator:");
        Console.WriteLine("  CopyWriter -> ToneCoach -> Reviewer (approves or sends back for revision)");
        Console.WriteLine();

        // Set up the Azure OpenAI client
        var chatClient = AzureOpenAIClientFactory.CreateChatClient();

        // Define the participants — each has a clear, specialized role.
        ChatClientAgent copyWriter = new(
            chatClient,
            name: "CopyWriter",
            instructions: """
                You are a customer support copywriter.
                Draft a professional, empathetic response to the customer's ticket.
                If a Reviewer or ToneCoach has provided feedback in the conversation,
                produce a revised version that addresses every point of feedback.
                Keep responses concise (3-5 sentences) and end with a ticket reference
                in the format TKT-XXXXX.
                """);

        ChatClientAgent toneCoach = new(
            chatClient,
            name: "ToneCoach",
            instructions: """
                You are a tone and empathy coach for customer support communications.
                Read the most recent draft from the CopyWriter and give 1-3 short,
                actionable suggestions to improve warmth, clarity, and customer empathy.
                Do NOT rewrite the draft yourself — only provide feedback.
                If the draft is already excellent, say "No tone changes needed."
                """);

        ChatClientAgent reviewer = new(
            chatClient,
            name: "Reviewer",
            instructions: """
                You are the final approver for customer support responses.
                Evaluate the most recent CopyWriter draft for accuracy, tone, and policy compliance.
                If it fully meets the bar, reply with exactly "APPROVED" followed by a one-sentence justification.
                Otherwise, list specific revisions the CopyWriter must make. Do NOT say "APPROVED"
                unless you are fully satisfied.
                """);

        // Build the group chat workflow with a custom approval-based manager.
        var workflow = AgentWorkflowBuilder
            .CreateGroupChatBuilderWith(agents =>
                new ApprovalBasedManager(agents, approverName: "Reviewer")
                {
                    MaximumIterationCount = 6
                })
            .AddParticipants(copyWriter, toneCoach, reviewer)
            .Build();

        // Load a ticket from the sample data file
        await TicketLoader.DisplayAvailableTicketsAsync();
        Console.WriteLine();
        Console.Write("Enter ticket number (1-5) or press Enter for random: ");
        var input = Console.ReadLine()?.Trim();

        SupportTicket sampleTicket;
        if (string.IsNullOrEmpty(input))
        {
            sampleTicket = await TicketLoader.GetRandomTicketAsync();
            Console.WriteLine($"Randomly selected: {sampleTicket.TicketId}");
        }
        else if (int.TryParse(input, out int index))
        {
            sampleTicket = await TicketLoader.GetTicketByIndexAsync(index);
        }
        else
        {
            sampleTicket = await TicketLoader.GetTicketByIdAsync(input)
                ?? await TicketLoader.GetRandomTicketAsync();
        }
        Console.WriteLine();

        Console.WriteLine("Incoming Support Ticket:");
        Console.WriteLine($"   Ticket ID: {sampleTicket.TicketId}");
        Console.WriteLine($"   Customer: {sampleTicket.CustomerName} ({sampleTicket.CustomerId})");
        Console.WriteLine($"   Priority: {sampleTicket.Priority}");
        Console.WriteLine($"   Subject: {sampleTicket.Subject}");
        Console.WriteLine($"   Description: {sampleTicket.Description}");
        Console.WriteLine();

        var task = $"""
            A new customer support ticket needs a response. Collaborate as a team
            (CopyWriter drafts, ToneCoach gives feedback, Reviewer approves or
            requests revisions) until the Reviewer approves a final response.

            Ticket ID: {sampleTicket.TicketId}
            Customer: {sampleTicket.CustomerName}
            Priority: {sampleTicket.Priority}
            Subject: {sampleTicket.Subject}
            Description: {sampleTicket.Description}
            """;

        var messages = new List<ChatMessage>
        {
            new(ChatRole.User, task)
        };

        Console.WriteLine("Starting group chat...");
        Console.WriteLine();

        await using StreamingRun run = await InProcessExecution.RunStreamingAsync(workflow, messages);
        await run.TrySendMessageAsync(new TurnToken(emitEvents: true));

        await foreach (WorkflowEvent evt in run.WatchStreamAsync().ConfigureAwait(false))
        {
            if (evt is AgentResponseEvent responseEvt)
            {
                foreach (var message in responseEvt.Response.Messages)
                {
                    if (string.IsNullOrWhiteSpace(message.Text))
                    {
                        continue;
                    }
                    var author = message.AuthorName ?? responseEvt.ExecutorId;
                    Console.WriteLine($"[{author}]");
                    Console.WriteLine(message.Text);
                    Console.WriteLine();
                }
            }
            else if (evt is WorkflowOutputEvent output)
            {
                Console.WriteLine("=== Final Conversation Transcript ===");
                if (output.Data is List<ChatMessage> conversation)
                {
                    foreach (var message in conversation)
                    {
                        if (string.IsNullOrWhiteSpace(message.Text))
                        {
                            continue;
                        }
                        Console.WriteLine($"[{message.AuthorName ?? message.Role.Value}]: {message.Text}");
                        Console.WriteLine();
                    }
                }
                else
                {
                    Console.WriteLine(output.Data);
                }
                break;
            }
        }

        Console.WriteLine("Group chat workflow completed!");
    }
}
