using Microsoft.Agents.AI;
using Microsoft.Agents.AI.Workflows;
using Microsoft.Extensions.AI;

namespace WorkflowLab.GroupChat;

/// <summary>
/// Custom group chat manager that terminates the conversation when the reviewer
/// explicitly approves the draft. Falls back to round-robin selection until the
/// approval signal is detected or the iteration limit is reached.
///
/// Demonstrates extending <see cref="RoundRobinGroupChatManager"/> with custom
/// termination logic, as documented at:
/// https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/group-chat
/// </summary>
internal sealed class ApprovalBasedManager : RoundRobinGroupChatManager
{
    private readonly string _approverName;
    private readonly string _approvalKeyword;

    public ApprovalBasedManager(IReadOnlyList<AIAgent> agents, string approverName, string approvalKeyword = "APPROVED")
        : base(agents)
    {
        _approverName = approverName;
        _approvalKeyword = approvalKeyword;
    }

    protected override ValueTask<bool> ShouldTerminateAsync(
        IReadOnlyList<ChatMessage> history,
        CancellationToken cancellationToken = default)
    {
        var last = history.LastOrDefault();
        bool shouldTerminate = last?.AuthorName == _approverName &&
            last.Text?.Contains(_approvalKeyword, StringComparison.OrdinalIgnoreCase) == true;

        return ValueTask.FromResult(shouldTerminate);
    }
}
