# Advanced Customer Support Agent - Comprehensive Agent Framework Demo

This repository demonstrates a production-ready **Advanced Customer Support Agent** that extensively showcases all 5 core Agent Framework features integrated with Azure AI Foundry.

## 🎯 Features Demonstrated

### 1. **@chat_middleware** - Multiple Middleware Layers
Three comprehensive middleware layers working in sequence:
- **Logging Middleware**: Tracks all requests and responses with detailed logging
- **Validation Middleware**: Security checks and input sanitization
- **Analytics Middleware**: Real-time metrics collection and sentiment analysis

### 2. **@ai_function** - Custom Tools
Five specialized customer support tools:
- `search_knowledge_base()` - Search help articles and documentation
- `create_support_ticket()` - Create and track support tickets
- `check_ticket_status()` - Query ticket status and details
- `get_customer_info()` - Retrieve customer profile and history
- `escalate_to_human()` - Transfer complex issues to human agents

### 3. **ChatContext** - Context Manipulation
Advanced state management including:
- Session tracking across multiple conversation turns
- Customer information storage and retrieval
- Conversation history maintenance
- Metadata management for request tracking

### 4. **ChatMessage** - Message Handling
Comprehensive message processing:
- Multi-turn conversation support
- Role-based messaging (user/assistant)
- Message metadata and timestamps
- Conversation serialization and export

### 5. **ChatResponse** - Response Processing
Rich response objects with:
- Formatted agent replies
- Analytics and metrics data
- Context state snapshots
- Processing metadata and timestamps

## 🚀 Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/vijaykol/agentframework.git
cd agentframework
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Basic Usage

Run the comprehensive demo:
```bash
python advanced_customer_support_agent.py
```

This will execute 4 different demo scenarios showcasing all features.

## 📋 Demo Scenarios

### Demo 1: Basic Customer Support Conversation
Multi-turn conversation demonstrating:
- Password reset assistance
- Return policy inquiries
- Ticket creation

### Demo 2: Support Ticket Management
Complete ticket lifecycle:
- Ticket creation with priority levels
- Status checking and tracking
- Ticket updates and escalation

### Demo 3: Middleware Features
Security and monitoring capabilities:
- Input validation and sanitization
- Request logging and tracking
- Analytics and sentiment analysis

### Demo 4: Context and State Management
Advanced conversation handling:
- Session state persistence
- Customer profile integration
- Conversation history export

## 🔧 Configuration

### Azure AI Foundry Integration

To integrate with Azure AI Foundry:

1. Set up your Azure AI Foundry project and obtain the endpoint
2. Configure authentication using Azure Identity
3. Update the agent initialization:

```python
agent = AdvancedCustomerSupportAgent(
    agent_name="ProductionSupportBot",
    foundry_endpoint="https://your-project.azure.ai"
)
```

### Environment Variables

Create a `.env` file with your configuration:
```env
AZURE_AI_FOUNDRY_ENDPOINT=https://your-project.azure.ai
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│         User Input                              │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  Middleware Layer 1: Logging                    │
└──────────────────┬──────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────┐
│  Middleware Layer 2: Validation                 │
└──────────────────┬──────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────┐
│  Middleware Layer 3: Analytics                  │
└──────────────────┬──────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────┐
│  ChatContext (State Management)                 │
│  - Session tracking                             │
│  - Customer data                                │
│  - Conversation history                         │
└──────────────────┬──────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────┐
│  Agent Processing                               │
│  - Intent recognition                           │
│  - Tool selection                               │
│  - Response generation                          │
└──────────────────┬──────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────┐
│  AI Functions (Tools)                           │
│  - Knowledge base search                        │
│  - Ticket management                            │
│  - Customer info retrieval                      │
│  - Escalation handling                          │
└──────────────────┬──────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────┐
│  ChatResponse (Formatted Output)                │
│  - Agent reply                                  │
│  - Updated context                              │
│  - Metrics and metadata                         │
└──────────────────┬──────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────┐
│         Response to User                        │
└─────────────────────────────────────────────────┘
```

## 💡 Code Examples

### Example 1: Simple Query
```python
import asyncio
from advanced_customer_support_agent import AdvancedCustomerSupportAgent

async def simple_query():
    agent = AdvancedCustomerSupportAgent()
    response = await agent.process_message(
        user_message="How do I reset my password?",
        customer_id="CUST-12345"
    )
    print(response.message.content)

asyncio.run(simple_query())
```

### Example 2: Multi-Turn Conversation
```python
async def multi_turn_conversation():
    agent = AdvancedCustomerSupportAgent()
    context = None
    
    messages = [
        "I need help with shipping",
        "What about international orders?",
        "Can you create a ticket for me?"
    ]
    
    for msg in messages:
        response = await agent.process_message(
            user_message=msg,
            context=context,
            customer_id="CUST-67890"
        )
        print(f"User: {msg}")
        print(f"Agent: {response.message.content}\n")
        context = response.context

asyncio.run(multi_turn_conversation())
```

### Example 3: Using Custom Tools
```python
from advanced_customer_support_agent import CustomerSupportTools

tools = CustomerSupportTools()

# Search knowledge base
result = tools.search_knowledge_base("return policy")
print(result)

# Create support ticket
ticket = tools.create_support_ticket(
    customer_id="CUST-12345",
    issue_description="Damaged item received",
    priority="high"
)
print(f"Created ticket: {ticket['ticket_id']}")

# Check ticket status
status = tools.check_ticket_status(ticket['ticket_id'])
print(f"Status: {status}")
```

## 📊 Metrics and Analytics

The agent automatically tracks:
- **Request Metrics**: Total requests, response times, error rates
- **Token Usage**: Estimated token consumption
- **Sentiment Analysis**: Customer satisfaction indicators
- **Conversation Stats**: Turn count, message length, session duration

Access metrics through the middleware manager:
```python
agent = AdvancedCustomerSupportAgent()
# ... process some messages ...
metrics = agent.middleware_manager.metrics
print(f"Total Requests: {metrics.total_requests}")
print(f"Average Response Time: {metrics.average_response_time:.2f}s")
print(f"Error Count: {metrics.error_count}")
```

## 🔒 Security Features

- **Input Validation**: Blocks malicious patterns (XSS, SQL injection)
- **Content Filtering**: Validates message length and format
- **Request Logging**: Complete audit trail of all interactions
- **Error Handling**: Graceful degradation and error recovery

## 🧪 Testing

Run individual demos:
```python
import asyncio
from advanced_customer_support_agent import (
    demo_basic_conversation,
    demo_ticket_management,
    demo_middleware_features,
    demo_context_state_management
)

# Run specific demo
asyncio.run(demo_basic_conversation())
```

## 📚 Documentation

### Key Classes

#### `AdvancedCustomerSupportAgent`
Main agent class integrating all features.

**Methods:**
- `process_message()` - Process user messages through the full pipeline
- `get_conversation_summary()` - Generate conversation analytics
- `export_conversation()` - Export conversations in various formats

#### `MiddlewareManager`
Manages all middleware layers.

**Middleware:**
- `logging_middleware()` - Request/response logging
- `validation_middleware()` - Input validation and security
- `analytics_middleware()` - Metrics collection

#### `CustomerSupportTools`
Collection of AI-powered tools.

**Tools:**
- `search_knowledge_base()` - Find relevant information
- `create_support_ticket()` - Ticket creation
- `check_ticket_status()` - Status queries
- `get_customer_info()` - Customer data retrieval
- `escalate_to_human()` - Human agent escalation

## 🔄 Integration with Azure AI Foundry

This agent is designed to work seamlessly with Azure AI Foundry:

1. **Agent Service Integration**: Deploy as a hosted agent
2. **OpenAPI Tool Registration**: Expose tools via OpenAPI
3. **Model Integration**: Connect to GPT-4, GPT-3.5, or custom models
4. **Observability**: Built-in logging for Azure Monitor
5. **Authentication**: Azure AD integration

## 🎓 Learning Resources

- [Azure AI Agent Framework Documentation](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-agents-readme)
- [Agent Framework Core PyPI](https://pypi.org/project/agent-framework-core/)
- [Azure AI Foundry Documentation](https://learn.microsoft.com/en-us/azure/ai-services/agents/)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋 Support

For questions or issues:
1. Check the demo scenarios in the code
2. Review the comprehensive inline documentation
3. Open an issue on GitHub

## ⭐ Features Highlight

This demo is unique because it:
- ✅ Uses **ALL 5** core Agent Framework features comprehensively
- ✅ Implements **3 middleware layers** showing real-world patterns
- ✅ Provides **5 custom AI tools** for practical use cases
- ✅ Includes **4 complete demo scenarios** with different workflows
- ✅ Integrates with **Azure AI Foundry** for production deployment
- ✅ Features **comprehensive logging and analytics**
- ✅ Implements **security best practices**
- ✅ Provides **extensive documentation** and examples

---

**Built with ❤️ using Azure AI Agent Framework**