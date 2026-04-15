# AI Workflow Patterns - Python

This project demonstrates three key workflow patterns for building AI applications using Python with Azure OpenAI.

## Project Structure

```
python/
├── program.py                        # Main entry point (interactive menu)
├── requirements.txt                  # Python dependencies
├── .env.template                     # Environment variable template
├── start.cmd                         # Windows launch script
├── start.sh                          # Linux/macOS launch script
│
├── common/                           # Shared components
│   ├── __init__.py
│   ├── azure_openai_client_factory.py  # Azure OpenAI client
│   ├── support_ticket.py              # SupportTicket model
│   └── ticket_loader.py               # Loads tickets from ../data/tickets.json
│
├── sequential/                       # Sequential Workflow
│   ├── __init__.py
│   ├── executors.py                  # Executor classes
│   └── demo.py                       # SequentialWorkflowDemo
│
├── concurrent_workflow/              # Concurrent Workflow
│   ├── __init__.py
│   ├── executors.py                  # Executor classes
│   └── demo.py                       # ConcurrentWorkflowDemo
│
└── human_in_the_loop/                # Human-in-the-Loop Workflow
    ├── __init__.py
    ├── models.py                     # Review models
    ├── executors.py                  # Executor classes
    └── demo.py                       # HumanInTheLoopWorkflowDemo
```

Ticket data is stored in `../data/tickets.json`, shared by both the Python and .NET projects.

## Workflow Patterns

### 1. Sequential Workflow
A linear pipeline where each step processes data and passes it to the next:

```
+---------------+    +--------------------+    +-------------------+
|   Ticket      |--->|  Categorization    |--->|    Response        |
|   Intake      |    |   AI Agent         |    |    AI Agent        |
+---------------+    +--------------------+    +-------------------+
```

**Use Cases:**
- Document processing pipelines
- Multi-stage content generation
- Step-by-step data transformation

### 2. Concurrent Workflow (Fan-out/Fan-in)
Distributes work to multiple agents simultaneously and aggregates results:

```
                    +--------------------+
               +--->|  Billing Expert    |---+
+----------+   |    +--------------------+   |    +---------------+
| Question |---+                              +-->|  Combined     |
+----------+   |    +--------------------+   |    |  Response     |
               +--->| Technical Expert   |---+    +---------------+
                    +--------------------+
```

**Use Cases:**
- Multi-expert analysis
- Parallel data processing
- Consensus building

### 3. Human-in-the-Loop Workflow
Pauses execution for human input, approval, or oversight:

```
+---------------+    +----------------+    +------------------+    +----------------+
|   Ticket      |--->|   AI Draft     |--->|  Supervisor      |--->|   Finalize     |
|   Intake      |    |    Agent       |    |   Review         |    |   Response     |
+---------------+    +----------------+    +------------------+    +----------------+
                                                    |
                                                    v
                                           +----------------+
                                           |  - Approve     |
                                           |  - Edit        |
                                           |  - Escalate    |
                                           +----------------+
```

**Use Cases:**
- Content approval workflows
- Financial authorization
- Quality control checkpoints

## Getting Started

### Prerequisites
- Python 3.10 or later
- Azure OpenAI resource with deployed model

### Installation

```bash
cd python

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows PowerShell
# source .venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. Copy the template to create your local config:

```bash
cp .env.template .env
```

2. Edit `.env` with your values (JSON format):

```json
{
    "TICKETS_PATH": "../data/tickets.json",
    "AZURE_OPENAI_ENDPOINT": "https://your-resource.openai.azure.com",
    "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4o-mini",
    "AZURE_OPENAI_API_KEY": "your-api-key"
}
```

#### Authentication Options

**Option 1: API Key**
```bash
export AZURE_OPENAI_API_KEY="your-api-key"
```

**Option 2: Azure CLI**
```bash
az login
# No additional environment variables needed
```

**Option 3: Service Principal**
```bash
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"
```

**Option 4: Managed Identity**
No additional configuration needed when running in Azure.

## Running the Lab

### Main Menu (Interactive)
```bash
python program.py
```

Or use the launch script:

```bash
.\start.cmd     # Windows
./start.sh      # Linux/macOS
```

## Additional Resources

- [Azure OpenAI Documentation](https://learn.microsoft.com/azure/ai-services/openai/)
- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)

