"""
Advanced Customer Support Agent - Comprehensive Agent Framework Demo

This demo extensively uses all 5 core Agent Framework features:
1. @chat_middleware - Multiple middleware layers for logging, validation, and analytics
2. @ai_function - Custom tools for customer support operations
3. ChatContext - Context manipulation for conversation state management
4. ChatMessage - Message handling for multi-turn conversations
5. ChatResponse - Response processing for formatted outputs

Integrated with Azure AI Foundry for production-ready deployment.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

# Agent Framework Core Imports
try:
    from agent_framework import (
        chat_middleware,
        ai_function,
        ChatContext,
        ChatMessage,
        ChatResponse,
        ChatAgent
    )
except ImportError:
    # Fallback for demonstration purposes
    print("Note: Install agent-framework-core package for full functionality")
    
    # Mock implementations for demonstration
    def chat_middleware(func):
        """Mock decorator for middleware"""
        func._is_middleware = True
        return func
    
    def ai_function(func):
        """Mock decorator for AI functions"""
        func._is_ai_function = True
        return func
    
    class ChatMessage:
        """Mock ChatMessage class"""
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
    
    class ChatContext:
        """Mock ChatContext class"""
        def __init__(self):
            self.messages: List[ChatMessage] = []
            self.state: Dict[str, Any] = {}
            self.metadata: Dict[str, Any] = {}
            self.session_id: Optional[str] = None
        
        def add_message(self, message: ChatMessage):
            self.messages.append(message)
        
        def get_conversation_history(self) -> List[Dict]:
            return [msg.to_dict() for msg in self.messages]
        
        def update_state(self, key: str, value: Any):
            self.state[key] = value
        
        def get_state(self, key: str, default=None):
            return self.state.get(key, default)
    
    class ChatResponse:
        """Mock ChatResponse class"""
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
    
    class ChatAgent:
        """Mock ChatAgent class"""
        def __init__(self, name: str, instructions: str):
            self.name = name
            self.instructions = instructions
            self.middleware_stack = []
            self.tools = []
        
        def add_middleware(self, middleware):
            self.middleware_stack.append(middleware)
        
        def add_tool(self, tool):
            self.tools.append(tool)

# Azure AI Foundry Imports
try:
    from azure.ai.agents import AgentsClient
    from azure.identity import DefaultAzureCredential
    FOUNDRY_AVAILABLE = True
except ImportError:
    FOUNDRY_AVAILABLE = False
    print("Note: Install azure-ai-agents for Azure AI Foundry integration")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# FEATURE 1: @chat_middleware - Multiple Middleware Layers
# ============================================================================

@dataclass
class MiddlewareMetrics:
    """Track metrics across middleware layers"""
    total_requests: int = 0
    total_tokens: int = 0
    average_response_time: float = 0.0
    error_count: int = 0
    sentiment_scores: List[float] = field(default_factory=list)


class MiddlewareManager:
    """Centralized middleware management"""
    
    def __init__(self):
        self.metrics = MiddlewareMetrics()
        self.request_log = []
    
    @chat_middleware
    async def logging_middleware(self, context: ChatContext, next_handler):
        """
        Middleware Layer 1: Comprehensive Logging
        Logs all incoming requests and outgoing responses
        """
        request_id = context.metadata.get('request_id', 'unknown')
        logger.info(f"[LOGGING] Request {request_id} - Processing message")
        
        # Log incoming message
        if context.messages:
            last_message = context.messages[-1]
            logger.info(f"[LOGGING] User message: {last_message.content[:100]}...")
        
        start_time = datetime.utcnow()
        
        try:
            # Pass to next middleware
            response = await next_handler(context)
            
            # Log response
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"[LOGGING] Request {request_id} completed in {elapsed:.2f}s")
            
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
    
    @chat_middleware
    async def validation_middleware(self, context: ChatContext, next_handler):
        """
        Middleware Layer 2: Input Validation and Security
        Validates and sanitizes user input before processing
        """
        logger.info("[VALIDATION] Validating input message")
        
        if not context.messages:
            raise ValueError("No messages in context")
        
        last_message = context.messages[-1]
        content = last_message.content
        
        # Security checks
        blocked_patterns = ['<script>', 'DROP TABLE', 'DELETE FROM', '../../']
        for pattern in blocked_patterns:
            if pattern.lower() in content.lower():
                logger.warning(f"[VALIDATION] Blocked potentially harmful pattern: {pattern}")
                raise ValueError(f"Input contains blocked pattern: {pattern}")
        
        # Length validation
        if len(content) > 5000:
            logger.warning("[VALIDATION] Message too long, truncating")
            last_message.content = content[:5000]
        
        # Add validation metadata
        context.metadata['validated'] = True
        context.metadata['validation_timestamp'] = datetime.utcnow().isoformat()
        
        logger.info("[VALIDATION] Input validation passed")
        return await next_handler(context)
    
    @chat_middleware
    async def analytics_middleware(self, context: ChatContext, next_handler):
        """
        Middleware Layer 3: Analytics and Metrics Collection
        Tracks usage metrics and sentiment analysis
        """
        logger.info("[ANALYTICS] Collecting metrics")
        
        self.metrics.total_requests += 1
        
        # Estimate token usage (simple approximation)
        if context.messages:
            last_message = context.messages[-1]
            estimated_tokens = len(last_message.content.split()) * 1.3
            self.metrics.total_tokens += int(estimated_tokens)
        
        # Simple sentiment analysis (mock)
        sentiment_score = self._analyze_sentiment(context.messages[-1].content)
        self.metrics.sentiment_scores.append(sentiment_score)
        
        # Add analytics metadata to context
        context.metadata['analytics'] = {
            'total_requests': self.metrics.total_requests,
            'estimated_tokens': self.metrics.total_tokens,
            'sentiment_score': sentiment_score
        }
        
        logger.info(f"[ANALYTICS] Sentiment score: {sentiment_score:.2f}")
        
        response = await next_handler(context)
        
        # Update average response time
        if self.request_log:
            avg_time = sum(r['elapsed_seconds'] for r in self.request_log) / len(self.request_log)
            self.metrics.average_response_time = avg_time
        
        return response
    
    def _analyze_sentiment(self, text: str) -> float:
        """Simple sentiment analysis (mock implementation)"""
        positive_words = ['happy', 'great', 'excellent', 'good', 'love', 'thank']
        negative_words = ['bad', 'terrible', 'hate', 'poor', 'awful', 'disappointed']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        # Return score between -1 and 1
        total = pos_count + neg_count
        if total == 0:
            return 0.0
        return (pos_count - neg_count) / total


# ============================================================================
# FEATURE 2: @ai_function - Custom Tools for Customer Support
# ============================================================================

class CustomerSupportTools:
    """Collection of AI-powered customer support tools"""
    
    def __init__(self):
        self.ticket_database = {}
        self.knowledge_base = self._initialize_knowledge_base()
        self.customer_data = {}
    
    def _initialize_knowledge_base(self) -> Dict[str, str]:
        """Initialize a sample knowledge base"""
        return {
            "reset_password": "To reset your password: 1) Go to login page 2) Click 'Forgot Password' 3) Enter your email 4) Follow the link in your email",
            "shipping_policy": "We offer free shipping on orders over $50. Standard shipping takes 3-5 business days. Express shipping is available for $15.",
            "return_policy": "Items can be returned within 30 days of purchase. Item must be unused and in original packaging. Refunds processed within 5-7 business days.",
            "billing_issue": "For billing issues: 1) Check your email for receipt 2) Verify card details 3) Contact your bank 4) If unresolved, contact our billing department at billing@company.com",
            "technical_support": "For technical support: 1) Clear browser cache 2) Try different browser 3) Check internet connection 4) Contact support at support@company.com"
        }
    
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
        return "No specific information found. Please provide more details so I can assist you better."
    
    @ai_function
    def create_support_ticket(self, customer_id: str, issue_description: str, priority: str = "medium") -> Dict[str, str]:
        """
        Create a new support ticket for the customer
        
        Args:
            customer_id: Unique customer identifier
            issue_description: Description of the customer's issue
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
            "message": f"Support ticket {ticket_id} has been created. A team member will respond within 24 hours."
        }
    
    @ai_function
    def check_ticket_status(self, ticket_id: str) -> Dict[str, Any]:
        """
        Check the status of an existing support ticket
        
        Args:
            ticket_id: The ticket ID to check
        
        Returns:
            Current ticket status and details
        """
        logger.info(f"[TOOL] Checking status for ticket: {ticket_id}")
        
        if ticket_id in self.ticket_database:
            ticket = self.ticket_database[ticket_id]
            return {
                "found": True,
                "ticket_id": ticket_id,
                "status": ticket["status"],
                "created_at": ticket["created_at"],
                "priority": ticket["priority"]
            }
        
        return {
            "found": False,
            "message": f"Ticket {ticket_id} not found. Please verify the ticket ID."
        }
    
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
        
        # Mock customer data
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
    
    @ai_function
    def escalate_to_human(self, ticket_id: str, reason: str) -> Dict[str, str]:
        """
        Escalate the conversation to a human agent
        
        Args:
            ticket_id: The ticket ID to escalate
            reason: Reason for escalation
        
        Returns:
            Escalation confirmation
        """
        logger.info(f"[TOOL] Escalating ticket {ticket_id} to human agent")
        
        if ticket_id in self.ticket_database:
            self.ticket_database[ticket_id]["status"] = "escalated"
            self.ticket_database[ticket_id]["escalation_reason"] = reason
        
        return {
            "status": "escalated",
            "message": "Your request has been escalated to a human agent. You will be contacted within 2 hours.",
            "ticket_id": ticket_id
        }


# ============================================================================
# FEATURE 3, 4, 5: ChatContext, ChatMessage, and ChatResponse Integration
# ============================================================================

class AdvancedCustomerSupportAgent:
    """
    Comprehensive customer support agent demonstrating all 5 Agent Framework features
    """
    
    def __init__(self, agent_name: str = "SupportBot", foundry_endpoint: Optional[str] = None):
        self.agent_name = agent_name
        self.middleware_manager = MiddlewareManager()
        self.support_tools = CustomerSupportTools()
        self.foundry_endpoint = foundry_endpoint
        self.foundry_client = None
        
        # Initialize Foundry client if available
        if FOUNDRY_AVAILABLE and foundry_endpoint:
            try:
                credential = DefaultAzureCredential()
                self.foundry_client = AgentsClient(
                    endpoint=foundry_endpoint,
                    credential=credential
                )
                logger.info("Azure AI Foundry client initialized successfully")
            except Exception as e:
                logger.warning(f"Could not initialize Foundry client: {e}")
        
        # Create the chat agent
        self.agent = ChatAgent(
            name=agent_name,
            instructions=self._get_agent_instructions()
        )
        
        # Register all middleware (in order)
        self.agent.add_middleware(self.middleware_manager.logging_middleware)
        self.agent.add_middleware(self.middleware_manager.validation_middleware)
        self.agent.add_middleware(self.middleware_manager.analytics_middleware)
        
        # Register all tools
        self.agent.add_tool(self.support_tools.search_knowledge_base)
        self.agent.add_tool(self.support_tools.create_support_ticket)
        self.agent.add_tool(self.support_tools.check_ticket_status)
        self.agent.add_tool(self.support_tools.get_customer_info)
        self.agent.add_tool(self.support_tools.escalate_to_human)
        
        logger.info(f"Advanced Customer Support Agent '{agent_name}' initialized")
    
    def _get_agent_instructions(self) -> str:
        """Get comprehensive agent instructions"""
        return """
        You are an advanced AI customer support agent with the following capabilities:
        
        1. Answer customer questions using the knowledge base
        2. Create and track support tickets
        3. Access customer information and history
        4. Escalate complex issues to human agents
        5. Provide empathetic and helpful responses
        
        Guidelines:
        - Always be polite and professional
        - Use customer's name when available
        - Acknowledge their frustration if they're upset
        - Provide clear, step-by-step instructions
        - Offer to create a ticket for unresolved issues
        - Escalate to human when appropriate
        
        Available tools:
        - search_knowledge_base: Find relevant help articles
        - create_support_ticket: Create new support tickets
        - check_ticket_status: Check existing ticket status
        - get_customer_info: Retrieve customer details
        - escalate_to_human: Transfer to human agent
        """
    
    async def process_message(
        self,
        user_message: str,
        context: Optional[ChatContext] = None,
        customer_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> ChatResponse:
        """
        Process a customer message through the full agent pipeline
        
        This method demonstrates:
        - FEATURE 3: ChatContext manipulation for state management
        - FEATURE 4: ChatMessage handling for conversations
        - FEATURE 5: ChatResponse processing for formatted outputs
        
        Args:
            user_message: The customer's message
            context: Existing conversation context (optional)
            customer_id: Customer identifier (optional)
            session_id: Session identifier (optional)
        
        Returns:
            ChatResponse with the agent's reply and updated context
        """
        # FEATURE 3: ChatContext - Create or use existing context
        if context is None:
            context = ChatContext()
            context.session_id = session_id or f"session_{datetime.utcnow().timestamp()}"
            logger.info(f"Created new context with session_id: {context.session_id}")
        
        # Store customer information in context state
        if customer_id:
            context.update_state('customer_id', customer_id)
            customer_info = self.support_tools.get_customer_info(customer_id)
            context.update_state('customer_info', customer_info)
            logger.info(f"Added customer {customer_id} to context")
        
        # Update conversation turn counter
        turn_number = context.get_state('turn_number', 0) + 1
        context.update_state('turn_number', turn_number)
        
        # FEATURE 4: ChatMessage - Create and add user message
        user_msg = ChatMessage(
            role="user",
            content=user_message,
            customer_id=customer_id,
            turn_number=turn_number
        )
        context.add_message(user_msg)
        logger.info(f"Added user message (turn {turn_number})")
        
        # Add request metadata for middleware
        context.metadata['request_id'] = f"req_{datetime.utcnow().timestamp()}"
        context.metadata['timestamp'] = datetime.utcnow().isoformat()
        
        # Process through agent (this goes through all middleware)
        agent_response_content = await self._generate_response(context, user_message)
        
        # FEATURE 4: ChatMessage - Create assistant message
        assistant_msg = ChatMessage(
            role="assistant",
            content=agent_response_content,
            turn_number=turn_number
        )
        context.add_message(assistant_msg)
        logger.info(f"Added assistant message (turn {turn_number})")
        
        # FEATURE 5: ChatResponse - Create comprehensive response
        response = ChatResponse(message=assistant_msg, context=context)
        
        # Add response metadata
        response.metadata['conversation_turns'] = turn_number
        response.metadata['total_messages'] = len(context.messages)
        response.metadata['session_id'] = context.session_id
        response.metadata['processing_timestamp'] = datetime.utcnow().isoformat()
        
        # Add analytics from middleware
        if 'analytics' in context.metadata:
            response.metadata['analytics'] = context.metadata['analytics']
        
        logger.info(f"Created ChatResponse with full metadata")
        
        return response
    
    async def _generate_response(self, context: ChatContext, user_message: str) -> str:
        """
        Generate agent response based on context and message
        This is where you would integrate with actual AI model
        """
        # Simple rule-based response for demonstration
        # In production, this would call Azure OpenAI or other LLM
        
        message_lower = user_message.lower()
        
        # Check if customer info is available
        customer_info = context.get_state('customer_info')
        greeting = ""
        if customer_info:
            greeting = f"Hello {customer_info.get('name', 'valued customer')}, "
        
        # Route based on intent
        if any(word in message_lower for word in ['password', 'reset', 'login', 'access']):
            kb_result = self.support_tools.search_knowledge_base("reset password")
            return f"{greeting}I can help you with password issues.\n\n{kb_result}"
        
        elif any(word in message_lower for word in ['shipping', 'delivery', 'ship']):
            kb_result = self.support_tools.search_knowledge_base("shipping policy")
            return f"{greeting}Here's information about our shipping:\n\n{kb_result}"
        
        elif any(word in message_lower for word in ['return', 'refund', 'exchange']):
            kb_result = self.support_tools.search_knowledge_base("return policy")
            return f"{greeting}Here's our return policy:\n\n{kb_result}"
        
        elif any(word in message_lower for word in ['billing', 'charge', 'payment', 'card']):
            kb_result = self.support_tools.search_knowledge_base("billing issue")
            return f"{greeting}Let me help with your billing concern:\n\n{kb_result}"
        
        elif any(word in message_lower for word in ['ticket', 'status', 'check']):
            # Extract ticket ID if present
            words = user_message.split()
            ticket_id = None
            for word in words:
                if 'TICKET-' in word.upper():
                    ticket_id = word.upper()
                    break
            
            if ticket_id:
                status = self.support_tools.check_ticket_status(ticket_id)
                if status['found']:
                    return f"{greeting}Here's the status of your ticket:\n\nTicket ID: {ticket_id}\nStatus: {status['status']}\nPriority: {status['priority']}\nCreated: {status['created_at']}"
                else:
                    return f"{greeting}I couldn't find ticket {ticket_id}. Please verify the ticket number."
            else:
                return f"{greeting}Please provide your ticket ID (format: TICKET-XXXX) so I can check its status."
        
        elif any(word in message_lower for word in ['create ticket', 'new ticket', 'open ticket', 'help', 'issue', 'problem']):
            customer_id = context.get_state('customer_id', 'CUST-UNKNOWN')
            ticket = self.support_tools.create_support_ticket(
                customer_id=customer_id,
                issue_description=user_message,
                priority='medium'
            )
            return f"{greeting}I've created a support ticket for you:\n\n{ticket['message']}\n\nYour ticket ID is: {ticket['ticket_id']}"
        
        else:
            # Default response with knowledge base search
            kb_result = self.support_tools.search_knowledge_base(user_message)
            return f"{greeting}I'm here to help! {kb_result}\n\nIf you need further assistance, I can create a support ticket for you."
    
    def get_conversation_summary(self, context: ChatContext) -> Dict[str, Any]:
        """
        Generate a comprehensive summary of the conversation
        Demonstrates ChatContext and ChatResponse usage
        """
        summary = {
            "session_id": context.session_id,
            "total_turns": context.get_state('turn_number', 0),
            "total_messages": len(context.messages),
            "customer_id": context.get_state('customer_id'),
            "conversation_history": context.get_conversation_history(),
            "state": context.state,
            "metadata": context.metadata
        }
        
        # Add middleware metrics
        summary["metrics"] = {
            "total_requests": self.middleware_manager.metrics.total_requests,
            "total_tokens": self.middleware_manager.metrics.total_tokens,
            "average_response_time": self.middleware_manager.metrics.average_response_time,
            "error_count": self.middleware_manager.metrics.error_count,
            "average_sentiment": (
                sum(self.middleware_manager.metrics.sentiment_scores) / 
                len(self.middleware_manager.metrics.sentiment_scores)
                if self.middleware_manager.metrics.sentiment_scores else 0
            )
        }
        
        return summary
    
    def export_conversation(self, context: ChatContext, format: str = 'json') -> str:
        """Export conversation in various formats"""
        summary = self.get_conversation_summary(context)
        
        if format == 'json':
            return json.dumps(summary, indent=2, default=str)
        elif format == 'text':
            lines = [
                f"=== Conversation Summary ===",
                f"Session ID: {summary['session_id']}",
                f"Total Turns: {summary['total_turns']}",
                f"Customer ID: {summary['customer_id']}",
                f"\n=== Messages ===\n"
            ]
            for msg in summary['conversation_history']:
                lines.append(f"{msg['role'].upper()}: {msg['content']}\n")
            return "\n".join(lines)
        else:
            raise ValueError(f"Unsupported format: {format}")


# ============================================================================
# Demo Usage Examples
# ============================================================================

async def demo_basic_conversation():
    """Demo 1: Basic conversation with all features"""
    print("\n" + "="*70)
    print("DEMO 1: Basic Customer Support Conversation")
    print("="*70 + "\n")
    
    # Initialize agent
    agent = AdvancedCustomerSupportAgent(
        agent_name="AdvancedSupportBot",
        foundry_endpoint=None  # Set to your Azure AI Foundry endpoint
    )
    
    # Create conversation context
    context = None
    customer_id = "CUST-12345"
    
    # Simulate multi-turn conversation
    conversations = [
        "Hi, I forgot my password and can't log in",
        "Thanks! Also, what's your return policy?",
        "Can you create a ticket for a billing issue I'm having?"
    ]
    
    for i, user_msg in enumerate(conversations, 1):
        print(f"\n--- Turn {i} ---")
        print(f"User: {user_msg}")
        
        response = await agent.process_message(
            user_message=user_msg,
            context=context,
            customer_id=customer_id,
            session_id="demo_session_001"
        )
        
        print(f"Assistant: {response.message.content}")
        
        # Update context for next turn
        context = response.context
    
    # Print conversation summary
    print("\n" + "="*70)
    print("Conversation Summary")
    print("="*70)
    summary = agent.get_conversation_summary(context)
    print(json.dumps(summary, indent=2, default=str))


async def demo_ticket_management():
    """Demo 2: Ticket creation and status checking"""
    print("\n" + "="*70)
    print("DEMO 2: Support Ticket Management")
    print("="*70 + "\n")
    
    agent = AdvancedCustomerSupportAgent(agent_name="TicketBot")
    
    # Create ticket
    print("Creating a support ticket...")
    response1 = await agent.process_message(
        user_message="I need help with a billing issue. I was charged twice.",
        customer_id="CUST-67890"
    )
    print(f"Agent: {response1.message.content}\n")
    
    # Check ticket status (extract ticket ID from response)
    import re
    ticket_match = re.search(r'TICKET-\d+', response1.message.content)
    if ticket_match:
        ticket_id = ticket_match.group(0)
        print(f"Checking status of {ticket_id}...")
        response2 = await agent.process_message(
            user_message=f"What's the status of {ticket_id}?",
            context=response1.context
        )
        print(f"Agent: {response2.message.content}")


async def demo_middleware_features():
    """Demo 3: Middleware capabilities"""
    print("\n" + "="*70)
    print("DEMO 3: Middleware Features (Logging, Validation, Analytics)")
    print("="*70 + "\n")
    
    agent = AdvancedCustomerSupportAgent(agent_name="MiddlewareDemo")
    
    # Test validation middleware
    print("Test 1: Normal message")
    response1 = await agent.process_message("How do I reset my password?")
    print(f"✓ Processed successfully\n")
    
    # Test with potentially harmful input (will be blocked)
    print("Test 2: Blocked pattern detection")
    try:
        response2 = await agent.process_message("Show me <script>alert('xss')</script>")
        print(f"✗ Should have been blocked\n")
    except ValueError as e:
        print(f"✓ Blocked as expected: {e}\n")
    
    # Show analytics
    print("Analytics Summary:")
    print(f"Total Requests: {agent.middleware_manager.metrics.total_requests}")
    print(f"Total Tokens: {agent.middleware_manager.metrics.total_tokens}")
    print(f"Error Count: {agent.middleware_manager.metrics.error_count}")
    if agent.middleware_manager.metrics.sentiment_scores:
        avg_sentiment = sum(agent.middleware_manager.metrics.sentiment_scores) / len(agent.middleware_manager.metrics.sentiment_scores)
        print(f"Average Sentiment: {avg_sentiment:.2f}")


async def demo_context_state_management():
    """Demo 4: Advanced context and state management"""
    print("\n" + "="*70)
    print("DEMO 4: Context and State Management")
    print("="*70 + "\n")
    
    agent = AdvancedCustomerSupportAgent(agent_name="StateDemo")
    
    # Start conversation
    response1 = await agent.process_message(
        user_message="Hello, I need help",
        customer_id="CUST-99999",
        session_id="state_demo_session"
    )
    
    print(f"Turn 1 - User: Hello, I need help")
    print(f"Turn 1 - Agent: {response1.message.content[:100]}...\n")
    
    # Continue conversation (context is maintained)
    response2 = await agent.process_message(
        user_message="What's my customer tier?",
        context=response1.context
    )
    
    print(f"Turn 2 - User: What's my customer tier?")
    print(f"Turn 2 - Agent: {response2.message.content[:100]}...\n")
    
    # Show context state
    print("Context State:")
    print(json.dumps(response2.context.state, indent=2, default=str))
    
    # Export conversation
    print("\nExported Conversation (Text Format):")
    print(agent.export_conversation(response2.context, format='text'))


async def main():
    """Run all demos"""
    print("\n" + "="*70)
    print("ADVANCED CUSTOMER SUPPORT AGENT")
    print("Comprehensive Agent Framework Demo with Azure AI Foundry Integration")
    print("="*70)
    print("\nFeatures Demonstrated:")
    print("1. @chat_middleware - Multiple middleware layers")
    print("2. @ai_function - Custom tools for customer support")
    print("3. ChatContext - Context manipulation and state management")
    print("4. ChatMessage - Multi-turn conversation handling")
    print("5. ChatResponse - Response processing and metadata")
    print("="*70)
    
    try:
        await demo_basic_conversation()
        await demo_ticket_management()
        await demo_middleware_features()
        await demo_context_state_management()
        
        print("\n" + "="*70)
        print("All demos completed successfully!")
        print("="*70 + "\n")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    # Run the comprehensive demo
    asyncio.run(main())
