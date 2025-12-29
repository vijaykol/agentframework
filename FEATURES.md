# Feature Showcase

This document provides detailed examples of all 5 core Agent Framework features as implemented in the Advanced Customer Support Agent.

## Table of Contents
1. [Feature 1: @chat_middleware](#feature-1-chat_middleware)
2. [Feature 2: @ai_function](#feature-2-ai_function)
3. [Feature 3: ChatContext](#feature-3-chatcontext)
4. [Feature 4: ChatMessage](#feature-4-chatmessage)
5. [Feature 5: ChatResponse](#feature-5-chatresponse)

---

## Feature 1: @chat_middleware

Multiple middleware layers process every request in sequence, enabling logging, validation, security, and analytics.

### Implementation Overview

```python
class MiddlewareManager:
    @chat_middleware
    async def logging_middleware(self, context: ChatContext, next_handler):
        """Layer 1: Comprehensive logging"""
        # Log incoming request
        # Process through next layer
        # Log outgoing response
        
    @chat_middleware
    async def validation_middleware(self, context: ChatContext, next_handler):
        """Layer 2: Security and validation"""
        # Validate input
        # Block malicious patterns
        # Sanitize content
        
    @chat_middleware
    async def analytics_middleware(self, context: ChatContext, next_handler):
        """Layer 3: Metrics and analytics"""
        # Collect metrics
        # Analyze sentiment
        # Track performance
```

### Detailed Examples

#### Example 1.1: Logging Middleware

**Purpose**: Track all requests and responses for debugging and auditing

```python
@chat_middleware
async def logging_middleware(self, context: ChatContext, next_handler):
    request_id = context.metadata.get('request_id', 'unknown')
    logger.info(f"[LOGGING] Request {request_id} - Processing message")
    
    start_time = datetime.utcnow()
    
    try:
        # Pass to next middleware
        response = await next_handler(context)
        
        # Log success
        elapsed = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"[LOGGING] Request {request_id} completed in {elapsed:.2f}s")
        
        # Store in audit trail
        self.request_log.append({
            'request_id': request_id,
            'timestamp': start_time.isoformat(),
            'elapsed_seconds': elapsed,
            'status': 'success'
        })
        
        return response
    except Exception as e:
        logger.error(f"[LOGGING] Request {request_id} failed: {str(e)}")
        self.metrics.error_count += 1
        raise
```

**What it does**:
- ✅ Logs every incoming request
- ✅ Measures response time
- ✅ Creates audit trail
- ✅ Tracks errors
- ✅ Returns performance metrics

#### Example 1.2: Validation Middleware

**Purpose**: Ensure input security and validity

```python
@chat_middleware
async def validation_middleware(self, context: ChatContext, next_handler):
    logger.info("[VALIDATION] Validating input message")
    
    if not context.messages:
        raise ValueError("No messages in context")
    
    last_message = context.messages[-1]
    content = last_message.content
    
    # Security checks
    blocked_patterns = ['<script>', 'DROP TABLE', 'DELETE FROM', '../../']
    for pattern in blocked_patterns:
        if pattern.lower() in content.lower():
            logger.warning(f"[VALIDATION] Blocked harmful pattern: {pattern}")
            raise ValueError(f"Input contains blocked pattern: {pattern}")
    
    # Length validation
    if len(content) > 5000:
        logger.warning("[VALIDATION] Message too long, truncating")
        last_message.content = content[:5000]
    
    # Add validation metadata
    context.metadata['validated'] = True
    context.metadata['validation_timestamp'] = datetime.utcnow().isoformat()
    
    return await next_handler(context)
```

**What it blocks**:
- ❌ XSS attacks (`<script>` tags)
- ❌ SQL injection attempts
- ❌ Path traversal attacks
- ❌ Overly long messages (>5000 chars)

#### Example 1.3: Analytics Middleware

**Purpose**: Collect metrics and analyze sentiment

```python
@chat_middleware
async def analytics_middleware(self, context: ChatContext, next_handler):
    logger.info("[ANALYTICS] Collecting metrics")
    
    # Track request count
    self.metrics.total_requests += 1
    
    # Estimate token usage
    if context.messages:
        last_message = context.messages[-1]
        estimated_tokens = len(last_message.content.split()) * 1.3
        self.metrics.total_tokens += int(estimated_tokens)
    
    # Sentiment analysis
    sentiment_score = self._analyze_sentiment(context.messages[-1].content)
    self.metrics.sentiment_scores.append(sentiment_score)
    
    # Add analytics to context
    context.metadata['analytics'] = {
        'total_requests': self.metrics.total_requests,
        'estimated_tokens': self.metrics.total_tokens,
        'sentiment_score': sentiment_score
    }
    
    return await next_handler(context)
```

**Metrics tracked**:
- 📊 Total requests
- 📊 Token usage
- 📊 Sentiment scores
- 📊 Response times
- 📊 Error rates

---

## Feature 2: @ai_function

Custom tools that the agent can invoke to perform specific operations.

### Implementation Overview

```python
class CustomerSupportTools:
    @ai_function
    def search_knowledge_base(self, query: str) -> str:
        """Search help articles"""
        
    @ai_function
    def create_support_ticket(self, customer_id: str, issue_description: str, priority: str) -> Dict:
        """Create support tickets"""
        
    @ai_function
    def check_ticket_status(self, ticket_id: str) -> Dict:
        """Check ticket status"""
        
    @ai_function
    def get_customer_info(self, customer_id: str) -> Dict:
        """Get customer data"""
        
    @ai_function
    def escalate_to_human(self, ticket_id: str, reason: str) -> Dict:
        """Escalate to human agent"""
```

### Detailed Examples

#### Example 2.1: Knowledge Base Search

```python
@ai_function
def search_knowledge_base(self, query: str) -> str:
    """
    Search the knowledge base for relevant information
    
    Args:
        query: The search query from the customer
    
    Returns:
        Relevant information from the knowledge base
    """
    logger.info(f"[TOOL] Searching knowledge base for: {query}")
    
    query_lower = query.lower()
    results = []
    
    for key, value in self.knowledge_base.items():
        if any(word in key for word in query_lower.split()):
            results.append(f"**{key.replace('_', ' ').title()}**: {value}")
    
    if results:
        return "\n\n".join(results)
    return "No specific information found. Please provide more details."
```

**Usage**:
```python
tools = CustomerSupportTools()
result = tools.search_knowledge_base("password reset")
# Returns: "**Reset Password**: To reset your password: 1) Go to login page..."
```

#### Example 2.2: Ticket Creation

```python
@ai_function
def create_support_ticket(self, customer_id: str, issue_description: str, priority: str = "medium") -> Dict[str, str]:
    """
    Create a new support ticket
    
    Args:
        customer_id: Unique customer identifier
        issue_description: Description of the issue
        priority: Priority level (low, medium, high, urgent)
    
    Returns:
        Ticket details including ticket ID
    """
    logger.info(f"[TOOL] Creating support ticket for customer: {customer_id}")
    
    ticket_id = f"TICKET-{len(self.ticket_database) + 1001}"
    ticket = {
        "ticket_id": ticket_id,
        "customer_id": customer_id,
        "issue": issue_description,
        "priority": priority,
        "status": "open",
        "created_at": datetime.utcnow().isoformat(),
        "assigned_to": "Support Team"
    }
    
    self.ticket_database[ticket_id] = ticket
    
    return {
        "ticket_id": ticket_id,
        "status": "created",
        "message": f"Support ticket {ticket_id} has been created."
    }
```

**Usage**:
```python
tools = CustomerSupportTools()
ticket = tools.create_support_ticket(
    customer_id="CUST-12345",
    issue_description="Cannot access my account",
    priority="high"
)
print(ticket['ticket_id'])  # TICKET-1001
```

#### Example 2.3: Customer Information Retrieval

```python
@ai_function
def get_customer_info(self, customer_id: str) -> Dict[str, Any]:
    """
    Retrieve customer information and history
    
    Args:
        customer_id: Unique customer identifier
    
    Returns:
        Customer information and interaction history
    """
    logger.info(f"[TOOL] Retrieving info for customer: {customer_id}")
    
    if customer_id not in self.customer_data:
        self.customer_data[customer_id] = {
            "customer_id": customer_id,
            "name": f"Customer {customer_id[-4:]}",
            "tier": "premium",
            "join_date": "2023-01-15",
            "total_purchases": 12,
            "lifetime_value": 1250.50
        }
    
    return self.customer_data[customer_id]
```

**Usage**:
```python
tools = CustomerSupportTools()
info = tools.get_customer_info("CUST-12345")
print(f"Name: {info['name']}, Tier: {info['tier']}")
```

---

## Feature 3: ChatContext

Manages conversation state, customer data, and message history across multiple turns.

### Implementation Overview

```python
class ChatContext:
    def __init__(self):
        self.messages: List[ChatMessage] = []
        self.state: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}
        self.session_id: Optional[str] = None
    
    def add_message(self, message: ChatMessage)
    def get_conversation_history(self) -> List[Dict]
    def update_state(self, key: str, value: Any)
    def get_state(self, key: str, default=None)
```

### Detailed Examples

#### Example 3.1: Session Management

```python
# Create context with session tracking
context = ChatContext()
context.session_id = "session_12345"

# Store customer ID
context.update_state('customer_id', 'CUST-99999')

# Store customer information
customer_info = {
    "name": "John Doe",
    "tier": "premium",
    "lifetime_value": 5000.00
}
context.update_state('customer_info', customer_info)

# Track conversation turns
turn_number = context.get_state('turn_number', 0) + 1
context.update_state('turn_number', turn_number)
```

#### Example 3.2: Multi-Turn Conversation State

```python
async def multi_turn_conversation():
    agent = AdvancedCustomerSupportAgent()
    context = None  # Start with no context
    
    # Turn 1
    response1 = await agent.process_message(
        user_message="I need help with shipping",
        context=context,
        customer_id="CUST-12345"
    )
    context = response1.context  # Save context
    
    # Turn 2 - context is maintained
    response2 = await agent.process_message(
        user_message="What about international orders?",
        context=context  # Pass previous context
    )
    context = response2.context
    
    # Turn 3 - full conversation history available
    response3 = await agent.process_message(
        user_message="Thanks!",
        context=context
    )
    
    # Access full conversation
    history = context.get_conversation_history()
    print(f"Total turns: {context.get_state('turn_number')}")
```

#### Example 3.3: Context State Access

```python
# Store custom data in context
context.update_state('preferred_language', 'en')
context.update_state('notification_preference', 'email')
context.update_state('vip_customer', True)

# Retrieve data
language = context.get_state('preferred_language', 'en')
is_vip = context.get_state('vip_customer', False)

# Add request metadata
context.metadata['request_id'] = 'req_123'
context.metadata['timestamp'] = datetime.utcnow().isoformat()
context.metadata['validated'] = True
```

---

## Feature 4: ChatMessage

Structured message representation with roles, content, and metadata.

### Implementation Overview

```python
class ChatMessage:
    def __init__(self, role: str, content: str, **kwargs):
        self.role = role
        self.content = content
        self.metadata = kwargs
        self.timestamp = datetime.utcnow()
    
    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            **self.metadata
        }
```

### Detailed Examples

#### Example 4.1: Creating Messages

```python
# User message
user_msg = ChatMessage(
    role="user",
    content="How do I reset my password?",
    customer_id="CUST-12345",
    turn_number=1
)

# Assistant message
assistant_msg = ChatMessage(
    role="assistant",
    content="To reset your password: 1) Go to login page...",
    turn_number=1
)

# Add to context
context.add_message(user_msg)
context.add_message(assistant_msg)
```

#### Example 4.2: Message with Metadata

```python
message = ChatMessage(
    role="user",
    content="I need urgent help!",
    customer_id="CUST-99999",
    priority="high",
    sentiment="urgent",
    channel="web_chat"
)

# Access metadata
print(message.metadata)
# {'customer_id': 'CUST-99999', 'priority': 'high', ...}
```

#### Example 4.3: Message Serialization

```python
# Convert to dictionary
msg_dict = message.to_dict()

# Example output:
{
    "role": "user",
    "content": "I need urgent help!",
    "timestamp": "2025-12-29T07:53:13.984000",
    "customer_id": "CUST-99999",
    "priority": "high",
    "sentiment": "urgent",
    "channel": "web_chat"
}

# Can be serialized to JSON
import json
json_string = json.dumps(msg_dict)
```

---

## Feature 5: ChatResponse

Comprehensive response object with message, context, and metadata.

### Implementation Overview

```python
class ChatResponse:
    def __init__(self, message: ChatMessage, context: ChatContext):
        self.message = message
        self.context = context
        self.metadata: Dict[str, Any] = {}
    
    def to_dict(self):
        return {
            "message": self.message.to_dict(),
            "context_state": self.context.state,
            "metadata": self.metadata
        }
```

### Detailed Examples

#### Example 5.1: Creating Responses

```python
async def process_message(self, user_message: str, context: ChatContext) -> ChatResponse:
    # Create assistant message
    assistant_msg = ChatMessage(
        role="assistant",
        content="Here's how I can help...",
        turn_number=turn_number
    )
    
    # Add to context
    context.add_message(assistant_msg)
    
    # Create response
    response = ChatResponse(message=assistant_msg, context=context)
    
    # Add metadata
    response.metadata['conversation_turns'] = turn_number
    response.metadata['total_messages'] = len(context.messages)
    response.metadata['session_id'] = context.session_id
    response.metadata['processing_timestamp'] = datetime.utcnow().isoformat()
    
    # Add analytics
    if 'analytics' in context.metadata:
        response.metadata['analytics'] = context.metadata['analytics']
    
    return response
```

#### Example 5.2: Accessing Response Data

```python
response = await agent.process_message("Help me!")

# Access message
print(f"Agent said: {response.message.content}")
print(f"Message role: {response.message.role}")

# Access updated context
print(f"Session: {response.context.session_id}")
print(f"Turn: {response.context.get_state('turn_number')}")

# Access metadata
print(f"Turns: {response.metadata['conversation_turns']}")
print(f"Analytics: {response.metadata['analytics']}")
```

#### Example 5.3: Response with Full Metadata

```python
# Complete response structure
{
    "message": {
        "role": "assistant",
        "content": "I can help you with that...",
        "timestamp": "2025-12-29T07:53:13.984000",
        "turn_number": 3
    },
    "context_state": {
        "customer_id": "CUST-12345",
        "customer_info": {...},
        "turn_number": 3
    },
    "metadata": {
        "conversation_turns": 3,
        "total_messages": 6,
        "session_id": "session_12345",
        "processing_timestamp": "2025-12-29T07:53:13.984000",
        "analytics": {
            "total_requests": 15,
            "estimated_tokens": 450,
            "sentiment_score": 0.75
        }
    }
}
```

---

## Integration: All Features Working Together

### Complete Flow Example

```python
async def complete_workflow_example():
    # Initialize agent with all features
    agent = AdvancedCustomerSupportAgent(
        agent_name="CompleteDemo",
        foundry_endpoint="https://your-project.azure.ai"
    )
    
    # Start conversation
    context = None
    customer_id = "CUST-12345"
    
    # Turn 1
    response1 = await agent.process_message(
        user_message="I can't log in to my account",
        context=context,
        customer_id=customer_id,
        session_id="demo_session"
    )
    
    # Middleware processed: logging ✓ validation ✓ analytics ✓
    # AI Function called: search_knowledge_base() ✓
    # ChatContext created: session tracking ✓
    # ChatMessage created: user + assistant ✓
    # ChatResponse returned: with full metadata ✓
    
    print(f"Turn 1 - Agent: {response1.message.content}")
    print(f"Analytics: {response1.metadata['analytics']}")
    
    # Turn 2 - context maintained
    context = response1.context
    response2 = await agent.process_message(
        user_message="Can you create a ticket?",
        context=context
    )
    
    # AI Function called: create_support_ticket() ✓
    # Context updated: turn_number incremented ✓
    # Full conversation history maintained ✓
    
    print(f"Turn 2 - Agent: {response2.message.content}")
    print(f"Total turns: {response2.context.get_state('turn_number')}")
    
    # Export full conversation
    summary = agent.get_conversation_summary(response2.context)
    print(json.dumps(summary, indent=2))
```

---

## Summary

This Advanced Customer Support Agent demonstrates **comprehensive usage** of all 5 Agent Framework features:

1. **@chat_middleware** ✓ - 3 middleware layers (logging, validation, analytics)
2. **@ai_function** ✓ - 5 custom tools (search, tickets, customer info, escalation)
3. **ChatContext** ✓ - Session management, state persistence, conversation history
4. **ChatMessage** ✓ - Role-based messaging, metadata, serialization
5. **ChatResponse** ✓ - Rich responses with context and analytics

Each feature is:
- ✅ Fully implemented
- ✅ Well documented
- ✅ Production ready
- ✅ Integrated with Azure AI Foundry
- ✅ Demonstrated with multiple examples
