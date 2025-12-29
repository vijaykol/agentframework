# Quick Start Guide

Get started with the Advanced Customer Support Agent in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/vijaykol/agentframework.git
cd agentframework
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note**: The demo works out-of-the-box with mock implementations. For full Azure AI Foundry integration, install the optional packages:
> ```bash
> pip install azure-ai-agents azure-identity python-dotenv
> ```

## Running the Demos

### Option 1: Run the Complete Demo

This runs 4 comprehensive demo scenarios:

```bash
python advanced_customer_support_agent.py
```

**Expected Output**:
- Demo 1: Multi-turn customer support conversation
- Demo 2: Support ticket creation and management
- Demo 3: Middleware features (logging, validation, analytics)
- Demo 4: Context and state management

### Option 2: Run Individual Examples

Run 9 specific usage examples:

```bash
python examples.py
```

**Examples Included**:
1. Simple query
2. Multi-turn conversation
3. Ticket workflow
4. Direct tool usage
5. Context state management
6. Conversation export
7. Metrics and analytics
8. Error handling
9. Azure Foundry integration

### Option 3: Use in Your Code

```python
import asyncio
from advanced_customer_support_agent import AdvancedCustomerSupportAgent

async def main():
    # Create agent
    agent = AdvancedCustomerSupportAgent(agent_name="MyBot")
    
    # Process a message
    response = await agent.process_message(
        user_message="How do I reset my password?",
        customer_id="CUST-12345"
    )
    
    # Print response
    print(f"Agent: {response.message.content}")

# Run
asyncio.run(main())
```

## Quick Examples

### Example 1: Simple Query
```python
import asyncio
from advanced_customer_support_agent import AdvancedCustomerSupportAgent

async def quick_query():
    agent = AdvancedCustomerSupportAgent()
    response = await agent.process_message("What is your return policy?")
    print(response.message.content)

asyncio.run(quick_query())
```

### Example 2: Create Support Ticket
```python
import asyncio
from advanced_customer_support_agent import AdvancedCustomerSupportAgent

async def create_ticket():
    agent = AdvancedCustomerSupportAgent()
    response = await agent.process_message(
        user_message="I need help with a billing issue",
        customer_id="CUST-99999"
    )
    print(response.message.content)

asyncio.run(create_ticket())
```

### Example 3: Multi-Turn Conversation
```python
import asyncio
from advanced_customer_support_agent import AdvancedCustomerSupportAgent

async def conversation():
    agent = AdvancedCustomerSupportAgent()
    context = None
    
    messages = [
        "Hi, I need help",
        "What's your shipping policy?",
        "Can you create a ticket for me?"
    ]
    
    for msg in messages:
        response = await agent.process_message(
            user_message=msg,
            context=context,
            customer_id="CUST-12345"
        )
        print(f"User: {msg}")
        print(f"Agent: {response.message.content}\n")
        context = response.context

asyncio.run(conversation())
```

## Understanding the Features

### 1. Middleware (@chat_middleware)

The agent uses 3 middleware layers:

- **Logging**: Tracks all requests and responses
- **Validation**: Security checks and input sanitization
- **Analytics**: Metrics collection and sentiment analysis

### 2. AI Functions (@ai_function)

5 custom tools for customer support:

- `search_knowledge_base()` - Find help articles
- `create_support_ticket()` - Create tickets
- `check_ticket_status()` - Check ticket status
- `get_customer_info()` - Get customer data
- `escalate_to_human()` - Transfer to human agent

### 3. ChatContext

Maintains conversation state:
- Session tracking
- Customer information
- Message history
- Metadata management

### 4. ChatMessage

Handles messages:
- Role-based messaging (user/assistant)
- Timestamps
- Metadata
- Turn tracking

### 5. ChatResponse

Rich responses with:
- Agent reply
- Updated context
- Analytics data
- Processing metadata

## Configuration (Optional)

For Azure AI Foundry integration:

1. Copy the template:
```bash
cp .env.template .env
```

2. Edit `.env` with your values:
```env
AZURE_AI_FOUNDRY_ENDPOINT=https://your-project.azure.ai
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
```

3. Update your code:
```python
agent = AdvancedCustomerSupportAgent(
    agent_name="ProductionBot",
    foundry_endpoint="https://your-project.azure.ai"
)
```

## Viewing Metrics

Access agent metrics:
```python
agent = AdvancedCustomerSupportAgent()

# Process some messages
await agent.process_message("Hello")
await agent.process_message("I need help")

# View metrics
metrics = agent.middleware_manager.metrics
print(f"Total Requests: {metrics.total_requests}")
print(f"Total Tokens: {metrics.total_tokens}")
print(f"Error Count: {metrics.error_count}")
```

## Exporting Conversations

Export conversation history:
```python
# After a conversation with context
json_export = agent.export_conversation(context, format='json')
text_export = agent.export_conversation(context, format='text')

# Save to file
with open('conversation.json', 'w') as f:
    f.write(json_export)
```

## Troubleshooting

### Issue: Import errors
**Solution**: Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: Azure AI Foundry connection fails
**Solution**: Check your credentials in `.env` and ensure you have the required permissions

### Issue: Deprecation warnings about datetime.utcnow()
**Solution**: These are harmless warnings. The code works correctly. For a future update, replace `datetime.utcnow()` with `datetime.now(timezone.utc)`

## Next Steps

1. **Explore the Code**: Check out `advanced_customer_support_agent.py` for detailed implementations
2. **Read the Architecture**: See `ARCHITECTURE.md` for design patterns and best practices
3. **Run Examples**: Try `examples.py` for comprehensive usage scenarios
4. **Customize**: Modify the knowledge base, add new tools, or adjust middleware
5. **Deploy**: Integrate with Azure AI Foundry for production deployment

## Learning Resources

- [Main README](README.md) - Complete documentation
- [Architecture Documentation](ARCHITECTURE.md) - Design and patterns
- [Examples](examples.py) - 9 usage scenarios
- [Azure AI Agent Framework Docs](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-agents-readme)

## Support

- Check the comprehensive inline documentation in the code
- Review the demo scenarios
- Consult the architecture documentation

## What Makes This Demo Special?

✅ **All 5 Core Features** - Uses every Agent Framework feature comprehensively  
✅ **Production Ready** - Includes logging, validation, security, and analytics  
✅ **Well Documented** - Extensive comments and documentation  
✅ **Multiple Demos** - 4 main demos + 9 examples  
✅ **Azure Integration** - Ready for Azure AI Foundry deployment  
✅ **Best Practices** - Follows industry patterns and conventions  

---

**Ready to build intelligent agents? Start with the demos and customize for your use case!** 🚀
