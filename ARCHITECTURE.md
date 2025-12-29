# Architecture Documentation

## Overview

The Advanced Customer Support Agent is built on the Azure AI Agent Framework, demonstrating production-ready patterns for building intelligent conversational agents. This document explains the architectural decisions and design patterns used.

## Core Architecture

### Layer Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│                  (External Applications)                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Middleware Stack                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  1. Logging Middleware                               │   │
│  │     - Request/Response logging                       │   │
│  │     - Performance tracking                           │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  2. Validation Middleware                            │   │
│  │     - Input sanitization                             │   │
│  │     - Security checks                                │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  3. Analytics Middleware                             │   │
│  │     - Metrics collection                             │   │
│  │     - Sentiment analysis                             │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  Context Management Layer                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  ChatContext                                         │   │
│  │  - Conversation state                                │   │
│  │  - Session management                                │   │
│  │  - Customer data                                     │   │
│  │  - Message history                                   │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Agent Processing Layer                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  AdvancedCustomerSupportAgent                        │   │
│  │  - Intent recognition                                │   │
│  │  - Response generation                               │   │
│  │  - Tool orchestration                                │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      Tools Layer                             │
│  ┌─────────────────┐ ┌─────────────────┐ ┌──────────────┐  │
│  │  Knowledge Base │ │ Ticket System   │ │  Customer    │  │
│  │     Search      │ │  Management     │ │     CRM      │  │
│  └─────────────────┘ └─────────────────┘ └──────────────┘  │
│  ┌─────────────────┐ ┌─────────────────┐                   │
│  │   Escalation    │ │  Status Check   │                   │
│  │     Handler     │ │     Tool        │                   │
│  └─────────────────┘ └─────────────────┘                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Integration Layer                         │
│              (Azure AI Foundry, Databases, APIs)             │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Middleware Components

#### Logging Middleware
**Purpose**: Comprehensive request/response logging for debugging and auditing

**Features**:
- Timestamps for all requests
- Request ID tracking
- Response time measurement
- Error logging
- Audit trail creation

**Implementation**:
```python
@chat_middleware
async def logging_middleware(self, context: ChatContext, next_handler):
    request_id = context.metadata.get('request_id', 'unknown')
    start_time = datetime.utcnow()
    
    # Log and process
    response = await next_handler(context)
    
    # Track metrics
    elapsed = (datetime.utcnow() - start_time).total_seconds()
    self.request_log.append({...})
    
    return response
```

#### Validation Middleware
**Purpose**: Security and input validation

**Features**:
- XSS attack prevention
- SQL injection detection
- Length validation
- Pattern blocking
- Input sanitization

**Security Patterns Blocked**:
- `<script>` tags
- SQL commands (DROP, DELETE)
- Path traversal attempts (`../../`)

#### Analytics Middleware
**Purpose**: Real-time metrics collection and analysis

**Metrics Collected**:
- Request count
- Token usage estimation
- Sentiment analysis
- Response time tracking
- Error rate monitoring

### 2. Context Management

#### ChatContext
**Purpose**: Maintain conversation state across multiple turns

**State Management**:
```python
context.update_state('customer_id', 'CUST-12345')
context.update_state('turn_number', 3)
context.update_state('customer_info', {...})
```

**Features**:
- Session tracking
- Customer data storage
- Conversation history
- Metadata management
- State persistence

### 3. Message Handling

#### ChatMessage
**Purpose**: Structured message representation

**Attributes**:
- `role`: Message sender (user/assistant)
- `content`: Message text
- `metadata`: Additional context
- `timestamp`: Creation time

**Multi-Turn Support**:
```python
# Turn 1
user_msg = ChatMessage(role="user", content="...", turn_number=1)
context.add_message(user_msg)

# Turn 2
assistant_msg = ChatMessage(role="assistant", content="...", turn_number=1)
context.add_message(assistant_msg)
```

### 4. Agent Processing

#### AdvancedCustomerSupportAgent
**Purpose**: Core agent logic and orchestration

**Responsibilities**:
1. Intent recognition
2. Tool selection
3. Response generation
4. Context management
5. Error handling

**Processing Flow**:
```
User Message → Context Creation → Middleware Processing → 
Intent Recognition → Tool Execution → Response Generation → 
ChatResponse Creation → Return to User
```

### 5. AI Functions (Tools)

#### Tool Architecture
Each tool is decorated with `@ai_function` and provides specific capabilities:

**Tool Categories**:

1. **Information Retrieval**
   - `search_knowledge_base()`: FAQ and documentation search

2. **Transaction Management**
   - `create_support_ticket()`: Issue tracking
   - `check_ticket_status()`: Status queries

3. **Data Access**
   - `get_customer_info()`: CRM integration

4. **Escalation**
   - `escalate_to_human()`: Human handoff

**Tool Interface**:
```python
@ai_function
def tool_name(param1: str, param2: int) -> Dict[str, Any]:
    """
    Tool description for AI model
    
    Args:
        param1: Description
        param2: Description
    
    Returns:
        Result dictionary
    """
    # Implementation
    return result
```

### 6. Response Processing

#### ChatResponse
**Purpose**: Structured response with metadata

**Components**:
- Agent message
- Updated context
- Processing metadata
- Analytics data

**Response Structure**:
```python
{
    "message": {
        "role": "assistant",
        "content": "...",
        "timestamp": "..."
    },
    "context_state": {...},
    "metadata": {
        "conversation_turns": 3,
        "session_id": "...",
        "analytics": {...}
    }
}
```

## Design Patterns

### 1. Chain of Responsibility
Middleware forms a chain where each layer can:
- Process the request
- Pass to next handler
- Modify the response

### 2. Decorator Pattern
`@chat_middleware` and `@ai_function` decorators add functionality without modifying core logic.

### 3. Strategy Pattern
Different tool implementations can be swapped based on requirements.

### 4. Observer Pattern
Analytics middleware observes all requests for metrics collection.

### 5. Builder Pattern
ChatContext and ChatResponse are built incrementally through the processing pipeline.

## Data Flow

### Request Processing

```
1. User Input
   ↓
2. ChatMessage Creation
   ↓
3. Middleware Layer 1 (Logging)
   - Log request
   - Start timer
   ↓
4. Middleware Layer 2 (Validation)
   - Check security
   - Validate input
   ↓
5. Middleware Layer 3 (Analytics)
   - Count request
   - Analyze sentiment
   ↓
6. Context Update
   - Add message to history
   - Update state
   ↓
7. Agent Processing
   - Recognize intent
   - Select tools
   - Generate response
   ↓
8. Tool Execution (if needed)
   - Execute AI functions
   - Gather results
   ↓
9. Response Creation
   - Create ChatMessage
   - Build ChatResponse
   - Add metadata
   ↓
10. Return through middleware
    - Update metrics
    - Log response
    ↓
11. Return to User
```

### State Management Flow

```
Session Start
   ↓
Create ChatContext
   ↓
Initialize State
   - session_id
   - turn_number = 0
   - customer_id (if available)
   ↓
For Each Turn:
   ↓
   Update State
   - Increment turn_number
   - Add customer info
   - Update metadata
   ↓
   Process Message
   ↓
   Update Context
   - Add messages
   - Update state
   - Track history
   ↓
Continue or End Session
```

## Scalability Considerations

### Horizontal Scaling
- Stateless middleware design
- Session data in external store (Redis, CosmosDB)
- Load balancer compatible

### Vertical Scaling
- Async/await for I/O operations
- Efficient message batching
- Connection pooling

### Caching Strategy
- Knowledge base responses
- Customer information
- Frequent queries

## Security Architecture

### Defense in Depth

1. **Input Layer**
   - Validation middleware
   - Pattern blocking
   - Length limits

2. **Processing Layer**
   - Sanitization
   - Safe string handling
   - No code execution

3. **Output Layer**
   - Response filtering
   - PII protection
   - Content moderation

### Authentication & Authorization
- Azure AD integration
- Role-based access control
- API key management

## Monitoring & Observability

### Metrics Collected
- Request count
- Response times
- Error rates
- Token usage
- Sentiment scores

### Logging Levels
- INFO: Normal operations
- WARNING: Validation issues
- ERROR: Processing failures

### Tracing
- Request ID tracking
- Session ID tracking
- Customer ID linking

## Azure AI Foundry Integration

### Connection Points

1. **Agent Service**
   - Register agent definition
   - Deploy to hosted environment

2. **Model Integration**
   - Connect to GPT-4/GPT-3.5
   - Token management
   - Rate limiting

3. **Authentication**
   - DefaultAzureCredential
   - Managed Identity support

4. **Monitoring**
   - Azure Monitor integration
   - Application Insights
   - Custom metrics

### Deployment Architecture

```
┌─────────────────────────────────────────┐
│       Azure AI Foundry Portal           │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│     Agent Service (Hosted)              │
│  ┌─────────────────────────────────┐   │
│  │  AdvancedCustomerSupportAgent   │   │
│  └─────────────────────────────────┘   │
└───────────┬──────────────┬──────────────┘
            │              │
            ▼              ▼
┌──────────────────┐  ┌──────────────────┐
│  Azure OpenAI    │  │  External APIs   │
│  (GPT-4)         │  │  (CRM, Tickets)  │
└──────────────────┘  └──────────────────┘
```

## Performance Optimization

### Best Practices

1. **Async Operations**
   - All I/O operations are async
   - Non-blocking message processing

2. **Efficient State Management**
   - Minimal state in memory
   - External storage for persistence

3. **Caching**
   - Knowledge base results
   - Customer information
   - Frequent queries

4. **Connection Pooling**
   - Database connections
   - API clients
   - Azure service clients

## Testing Strategy

### Unit Tests
- Individual middleware functions
- Tool implementations
- State management

### Integration Tests
- Full request/response cycle
- Multi-turn conversations
- Error scenarios

### Load Tests
- Concurrent requests
- Long-running sessions
- Memory usage

## Future Enhancements

### Planned Features
1. Multi-language support
2. Voice interaction
3. Proactive notifications
4. Advanced analytics dashboard
5. A/B testing framework

### Scalability Improvements
1. Distributed session storage
2. Message queue integration
3. Event-driven architecture
4. Microservices decomposition

## References

- [Azure AI Agent Framework Documentation](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-agents-readme)
- [Agent Framework Core](https://pypi.org/project/agent-framework-core/)
- [Azure AI Foundry](https://learn.microsoft.com/en-us/azure/ai-services/agents/)
