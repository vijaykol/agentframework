# Advanced Customer Support Agent using Microsoft Agent Framework

customer support agent built with **Microsoft Agent Framework** and **Azure AI Foundry**, featuring comprehensive middleware layers, custom AI tools, and a beautiful web-based UI powered by **DevUI**.

## 🎯 Overview

This project demonstrates a complete implementation of the Microsoft Agent Framework with:

- **Native Framework Components**: `@chat_middleware`, `@ai_function`, `ChatContext`, `ChatMessage`, `TextContent`
- **Azure AI Foundry Integration**: Powered by gpt-4o deployment
- **Multiple Middleware Layers**: Logging, user context, validation, and analytics
- **Custom AI Tools**: User lookup, ticket search, ticket creation, service status
- **DevUI Web Interface**: Interactive chat and monitoring dashboard
- **Async/Await Support**: Full async implementation with sync-to-async wrapper
- **Extensive Logging**: Comprehensive logging throughout the system

## ✨ Features

### Core Agent Framework Features

| Feature | Description |
|---------|-------------|
| **@chat_middleware** | 4 middleware layers that process messages sequentially (logging → context → validation → analytics) |
| **@ai_function** | 4 custom tools that the LLM can call automatically based on user intent |
| **ChatContext** | Container for entire conversation with list of ChatMessages |
| **ChatMessage** | Individual messages with TextContent, metadata, and role (user/assistant) |
| **TextContent** | Structured text wrapper with language, encoding, and metadata support |

### Middleware Pipeline

1. **Logging Middleware** - Logs all incoming messages
2. **User Context Middleware** - Enriches messages with user data
3. **Validation Middleware** - Validates message quality and format
4. **Analytics Middleware** - Tracks metrics and performance

### AI Tools (Functions)

The agent can automatically call these tools based on user intent:

```python
@ai_function
def get_user_info(user_id: str) -> str:
    """Get user information from the database"""

@ai_function
def search_tickets(user_id: str) -> str:
    """Search support tickets for a user"""

@ai_function
def create_ticket(user_id: str, subject: str, priority: str) -> str:
    """Create a new support ticket"""

@ai_function
def get_service_status() -> str:
    """Get current service status"""
```

### How Tool Calling Works

```
User Message
    ↓
LLM Analyzes Intent (automatically)
    ↓
LLM Decides Which Tools to Call (based on tool schemas)
    ↓
Framework Executes Tools (via JSON)
    ↓
LLM Synthesizes Response
    ↓
Response to User
```

The LLM receives JSON schemas of all available tools and automatically decides which ones to call based on the user's message. No explicit if/else statements needed!

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Microsoft Agent Framework
- Azure AI Foundry access
- Azure credentials configured



### Configuration

Set your Azure credentials and Foundry endpoint:

```bash

$env:FOUNDRY_ENDPOINT = ""
$env:FOUNDRY_DEPLOYMENT = "gpt-4o"


```

### Running with DevUI



## 🎨 DevUI - Web Interface

DevUI provides a beautiful web-based interface to interact with your agent:

### Features

- **Interactive Chat** - Chat with the agent in real-time
- **Conversation History** - View full conversation history
- **Middleware Monitoring** - Watch each middleware layer execute
- **Tool Execution Trace** - See which tools were called and their results
- **Tool Inspector** - View all available tools and their parameters
- **Events Dashboard** - Real-time event tracking
- **Traces** - Detailed execution traces
- **Performance Metrics** - Track response times and resource usage

### Example Interactions

```
User: "URGENT! I was charged twice!"
→ DevUI shows: middleware execution → get_user_info() → search_tickets() → create_ticket() → response

User: "What is my account status?"
→ DevUI shows: get_user_info() tool call → user data → response

User: "Check service status"
→ DevUI shows: get_service_status() tool call → status info → response
```

## 📊 Architecture

### Data Flow

```
User Input (DevUI Chat)
    ↓
ChatMessage Created (with TextContent)
    ↓
Middleware Pipeline
  ├─ Logging Middleware
  ├─ User Context Middleware
  ├─ Validation Middleware
  └─ Analytics Middleware
    ↓
LLM Processing (with tool schemas)
    ↓
Tool Execution (if needed)
    ↓
Response Synthesis
    ↓
DevUI Display
```

### ChatContext & ChatMessage Relationship

```
ChatContext (entire conversation container)
  └─ messages: List[ChatMessage]
      ├─ Message 1: User asks something
      │   └─ content: TextContent
      ├─ Message 2: Agent responds
      │   └─ content: TextContent
      ├─ Message 3: User follows up
      │   └─ content: TextContent
      └─ Message 4: Agent responds again
          └─ content: TextContent
```

Each turn adds new ChatMessages to the list. The LLM always receives the entire list for full context.

## 🔧 Code Structure

```
advanced_agent_demo_with_devui_final.py
├── Database Simulation (Users & Tickets)
├── Async Wrapper (for sync OpenAI client)
├── AI Functions (@ai_function)
│   ├── get_user_info
│   ├── search_tickets
│   ├── create_ticket
│   └── get_service_status
├── Middleware Layers (@chat_middleware)
│   ├── logging_middleware
│   ├── user_context_middleware
│   ├── validation_middleware
│   └── analytics_middleware
├── Foundry Client Setup
├── Agent Creation
└── Main (DevUI Server)
```

## 💡 Key Concepts

### Intent Determination

The LLM automatically determines user intent by analyzing the message. It doesn't need explicit programming:

```python
# No if/else needed! LLM figures it out:
"URGENT! I was charged twice!" 
→ LLM intent: billing issue, needs user info and ticket creation
→ Calls: get_user_info() → search_tickets() → create_ticket()

"What's my status?"
→ LLM intent: account inquiry
→ Calls: get_user_info()

"Is the service working?"
→ LLM intent: status check
→ Calls: get_service_status()
```

### Tool Calling Flow

1. **LLM Receives Tool Schemas** - JSON descriptions of all available tools
2. **LLM Decides** - Based on user message, which tools to call
3. **Framework Executes** - Parses JSON, calls Python functions
4. **Results Returned** - Tool results sent back to LLM
5. **LLM Synthesizes** - Creates natural response using tool results

### Good Practice: Docstrings

Always provide clear docstrings for your tools:

```python
@ai_function
def get_user_info(user_id: Annotated[str, "The user ID to look up"]) -> str:
    """Get user information from the database"""
    # The docstring and parameter annotations help the LLM understand what this tool does
```

## 📝 Middleware Deep Dive

Middleware runs sequentially and can:
- **Process** messages before/after LLM
- **Enrich** messages with additional data
- **Validate** message quality
- **Monitor** and track metrics

```python
@chat_middleware
async def logging_middleware(context: ChatContext) -> None:
    """Middleware 1: Logging all messages"""
    if context.messages:
        msg_preview = context.messages[-1].content[:50]
        logger.info(f"Message: {msg_preview}...")
```

## 🧪 Testing

The project includes 4 test scenarios (can be run without DevUI):

```bash
# Run test scenarios (console only)
python advanced_agent_demo.py
```

Test scenarios:
1. **Urgent Billing Issue** - Tests multiple tool calls
2. **Technical Support** - Tests API error handling
3. **General Inquiry** - Tests service status tool
4. **Multi-Turn Conversation** - Tests conversation history

## 📚 Understanding the Framework

### How @chat_middleware Works

Middleware intercepts ChatContext before/after LLM processing:

```
Input → MW1 → MW2 → MW3 → MW4 → LLM → Response
```

Each middleware can:
- Read messages from context
- Add metadata
- Validate content
- Track analytics

### How @ai_function Works

Functions decorated with `@ai_function` are automatically:
1. Converted to JSON schemas
2. Sent to LLM as available tools
3. Called by framework when LLM decides
4. Results returned to LLM

### How ChatContext Flows

ChatContext is passed through the entire pipeline:
- Created when user sends message
- Passed through all middleware
- Sent to LLM with full history
- Updated with new messages
- Returned to user

## 🔐 Security Considerations

- **Credentials**: Use Azure Identity for secure authentication
- **Logging**: Be careful not to log sensitive user data
- **Tool Access**: Validate user permissions before executing tools
- **Input Validation**: Always validate user input in middleware

## 🐛 Troubleshooting

### 404 Error from Foundry

If you get a 404 error, check:
- Foundry endpoint is correct
- Model deployment name matches (gpt-4o)
- Azure credentials are valid
- Network connectivity to Foundry

### DevUI Not Opening

- Check if port 8080 is available
- Try `http://localhost:8080` manually
- Check console logs for errors

### Tool Not Being Called

- Verify tool has `@ai_function` decorator
- Check tool docstring is clear
- Ensure parameter annotations are present
- Test with explicit user message mentioning the tool

## 📖 Additional Resources

- [Microsoft Agent Framework Documentation](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview)


## 🤝 Contributing

Feel free to extend this project with:
- Additional middleware layers
- More AI tools
- Custom database implementations
- Enhanced DevUI features

## 📄 License

MIT License - feel free to use this project as a reference or starting point.



**Built with ❤️ using Microsoft Agent Framework and Azure AI Foundry**
