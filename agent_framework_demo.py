"""
Advanced Customer Support Agent - Comprehensive Agent Framework Demo with Foundry Integration

This demo extensively uses all 5 core Agent Framework features:
1. @chat_middleware - Multiple middleware layers
2. @ai_function - Custom tools
3. ChatContext - Context manipulation
4. ChatMessage - Message handling
5. ChatResponse - Response processing

Properly integrated with Azure AI Foundry (gpt-4o deployment).
Uses a custom async wrapper for Foundry's sync OpenAI client.


"""

import os
import json
import asyncio
import logging
from datetime import datetime
from typing import Annotated, List, Dict, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Agent Framework imports
from agent_framework import (
    ChatAgent,
    chat_middleware,
    ai_function,
    ChatContext,
    ChatMessage,
    TextContent,
)
from agent_framework.openai import OpenAIChatClient
from agent_framework.devui import serve

# Foundry SDK imports
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient


# ============================================================================
# DATABASE SIMULATION
# ============================================================================

@dataclass
class User:
    user_id: str
    name: str
    email: str
    tier: str
    language: str
    preferences: Dict[str, Any]
    conversation_history: List[Dict[str, str]]


@dataclass
class Ticket:
    ticket_id: str
    user_id: str
    subject: str
    status: str
    priority: str
    created_at: datetime
    messages: List[str]


USERS_DB = {
    "user123": User(
        user_id="user123",
        name="Alice Johnson",
        email="alice@example.com",
        tier="enterprise",
        language="en",
        preferences={"tone": "professional", "detail_level": "high"},
        conversation_history=[]
    ),
    "user456": User(
        user_id="user456",
        name="Bob Smith",
        email="bob@example.com",
        tier="free",
        language="es",
        preferences={"tone": "casual", "detail_level": "low"},
        conversation_history=[]
    ),
}

TICKETS_DB = {
    "ticket001": Ticket(
        ticket_id="ticket001",
        user_id="user123",
        subject="Login issue",
        status="open",
        priority="high",
        created_at=datetime.now(),
        messages=["Cannot login with my password"]
    )
}


# ============================================================================
# ASYNC WRAPPER FOR SYNC OPENAI CLIENT
# ============================================================================

class AsyncCompletionsWrapper:
    """
    Wraps the completions interface to be async.
    """
    
    def __init__(self, sync_client, executor=None):
        self.sync_client = sync_client
        self.executor = executor or ThreadPoolExecutor(max_workers=5)
        logger.info("[AsyncCompletionsWrapper] Initialized")
    
    async def create(self, *args, **kwargs):
        """Async wrapper for client.chat.completions.create()"""
        # Force stream=False and remove stream_options to avoid issues
        kwargs['stream'] = False
        kwargs.pop('stream_options', None)
        loop = asyncio.get_event_loop()
        logger.info("[AsyncCompletionsWrapper] Calling sync create() in executor")
        return await loop.run_in_executor(
            self.executor,
            lambda: self.sync_client.chat.completions.create(*args, **kwargs)
        )


class AsyncChatWrapper:
    """
    Wraps the chat interface with completions.
    """
    
    def __init__(self, sync_client, executor=None):
        self.sync_client = sync_client
        self.executor = executor or ThreadPoolExecutor(max_workers=5)
        self.completions = AsyncCompletionsWrapper(sync_client, executor)
        logger.info("[AsyncChatWrapper] Initialized")


class AsyncOpenAIChatClientWrapper:
    """
    Wraps the sync OpenAI client to provide async interface.
    Matches the structure: client.chat.completions.create()
    """
    
    def __init__(self, sync_openai_client):
        self.sync_client = sync_openai_client
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.chat = AsyncChatWrapper(sync_openai_client, self.executor)
        logger.info("[AsyncOpenAIChatClientWrapper] Initialized with proper interface")
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        self.executor.shutdown(wait=True)
        logger.info("[AsyncOpenAIChatClientWrapper] Executor shut down")


# ============================================================================
# AI FUNCTIONS - Custom Tools (@ai_function)
# ============================================================================

@ai_function
def get_user_info(user_id: Annotated[str, "The user ID to look up"]) -> str:
    """Get user information from the database"""
    logger.info(f"[TOOL] Getting user info for: {user_id}")
    user = USERS_DB.get(user_id)
    if user:
        return json.dumps({
            "user_id": user.user_id,
            "name": user.name,
            "email": user.email,
            "tier": user.tier,
            "language": user.language,
            "preferences": user.preferences
        })
    return json.dumps({"error": f"User {user_id} not found"})


@ai_function
def search_tickets(user_id: Annotated[str, "The user ID to search tickets for"]) -> str:
    """Search support tickets for a user"""
    logger.info(f"[TOOL] Searching tickets for user: {user_id}")
    user_tickets = [t for t in TICKETS_DB.values() if t.user_id == user_id]
    return json.dumps([{
        "ticket_id": t.ticket_id,
        "subject": t.subject,
        "status": t.status,
        "priority": t.priority,
        "created_at": t.created_at.isoformat()
    } for t in user_tickets])


@ai_function
def create_ticket(
    user_id: Annotated[str, "The user ID"],
    subject: Annotated[str, "The ticket subject"],
    priority: Annotated[str, "Priority level: low, medium, high, urgent"]
) -> str:
    """Create a new support ticket"""
    logger.info(f"[TOOL] Creating ticket for user {user_id}: {subject}")
    ticket_id = f"ticket{len(TICKETS_DB) + 1:03d}"
    new_ticket = Ticket(
        ticket_id=ticket_id,
        user_id=user_id,
        subject=subject,
        status="open",
        priority=priority,
        created_at=datetime.now(),
        messages=[]
    )
    TICKETS_DB[ticket_id] = new_ticket
    return json.dumps({
        "success": True,
        "ticket_id": ticket_id,
        "message": f"Ticket {ticket_id} created successfully"
    })


@ai_function
def get_service_status() -> str:
    """Get current service status"""
    logger.info("[TOOL] Getting service status")
    return json.dumps({
        "status": "operational",
        "uptime": "99.99%",
        "last_incident": "2025-12-20",
        "services": {
            "api": "operational",
            "web": "operational",
            "database": "operational"
        }
    })


# ============================================================================
# MIDDLEWARE LAYERS (@chat_middleware)
# ============================================================================

@chat_middleware
async def logging_middleware(context: ChatContext) -> None:
    """Middleware 1: Logging all messages"""
    if context.messages:
        msg_preview = context.messages[-1].content[:50] if context.messages[-1].content else "No content"
        logger.info(f"[MW1-LOG] Message: {msg_preview}...")


@chat_middleware
async def user_context_middleware(context: ChatContext) -> None:
    """Middleware 2: Add user context to messages"""
    logger.info("[MW2-CONTEXT] Processing user context")
    if context.messages:
        last_msg = context.messages[-1]
        if hasattr(last_msg, 'metadata') and last_msg.metadata:
            user_id = last_msg.metadata.get('user_id')
            if user_id and user_id in USERS_DB:
                user = USERS_DB[user_id]
                logger.info(f"[MW2-CONTEXT] User: {user.name} ({user.tier})")


@chat_middleware
async def validation_middleware(context: ChatContext) -> None:
    """Middleware 3: Validate message content"""
    logger.info("[MW3-VALIDATION] Validating message")
    if context.messages:
        msg_len = len(context.messages[-1].content)
        if msg_len < 2:
            logger.warning(f"[MW3-VALIDATION] Message too short ({msg_len} chars)")


@chat_middleware
async def analytics_middleware(context: ChatContext) -> None:
    """Middleware 4: Analytics and monitoring"""
    if context.messages:
        msg_len = len(context.messages[-1].content)
        logger.info(f"[MW4-ANALYTICS] Message length: {msg_len} chars")


# ============================================================================
# FOUNDRY CLIENT INITIALIZATION
# ============================================================================

def create_foundry_client():
    """Create Azure OpenAI client"""
    logger.info("🔧 Initializing Azure OpenAI client...")
    
    azure_endpoint = "https://openai-aa.openai.azure.com/"
    
    logger.info(f"   Endpoint: {azure_endpoint}")
    
    try:
        from openai import AsyncAzureOpenAI
        
        # API key
        api_key = ""
        
        # Use AsyncAzureOpenAI directly - no wrapper needed
        openai_client = AsyncAzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            api_version="2024-08-01-preview"
        )
        logger.info("   Connected to Azure OpenAI")
        
        return openai_client
        
    except Exception as e:
        logger.error(f"   Failed to initialize: {e}")
        raise


# ============================================================================
# AGENT CREATION
# ============================================================================

def create_support_agent():
    """
    Create the main support agent with all middleware and tools.
    Uses Microsoft Foundry as the chat client (with async wrapper).
    """
    logger.info("🤖 Creating support agent...")
    
    # Get OpenAI client from Foundry (with async wrapper)
    async_client = create_foundry_client()
    
    # Create agent framework chat client
    chat_client = OpenAIChatClient(
        model_id="gpt-4o",  # Matches Azure OpenAI deployment name
        async_client=async_client
    )
    logger.info("   Chat client configured")
    
    # Create agent with all features
    agent = ChatAgent(
        name="AdvancedSupportAgent",
        description="Advanced customer support agent with comprehensive middleware and tools",
        instructions="""
You are an advanced customer support agent for a SaaS company.

Your capabilities:
- Access user information and preferences
- Search and manage support tickets
- Check service status
- Create and update tickets

Always:
1. Greet users professionally
2. Use appropriate tools to gather information
3. Provide accurate, helpful responses
4. Offer to create tickets for unresolved issues
5. End with a follow-up question

Remember:
- Enterprise users get priority support
- Be professional but friendly
- Use the available tools to help resolve issues
""",
        chat_client=chat_client,
        tools=[get_user_info, search_tickets, create_ticket, get_service_status],
        middlewares=[
            logging_middleware,
            user_context_middleware,
            validation_middleware,
            analytics_middleware
        ]
    )
    
    logger.info("   ✅ Agent created successfully")
    return agent


# ============================================================================
# TEST SCENARIOS (ASYNC)
# ============================================================================

async def test_scenario_1_urgent_billing():
    """Test: Urgent billing issue"""
    print(f"\n{'#'*70}")
    print(f"# TEST SCENARIO 1: Urgent Billing Issue")
    print(f"{'#'*70}\n")
    
    logger.info("Starting test scenario 1...")
    agent = create_support_agent()
    
    try:
        response = await agent.run(
            "URGENT! I was charged twice for my subscription this month!"
        )
        
        print(f"\n{'='*70}")
        print(f"AGENT RESPONSE:")
        print(f"{'='*70}")
        print(response.text)
        print(f"{'='*70}\n")
        logger.info("Test scenario 1 completed successfully")
        
    except Exception as e:
        logger.error(f"Error in test scenario 1: {e}")
        import traceback
        traceback.print_exc()
        print(f"Error: {e}")


async def test_scenario_2_technical_support():
    """Test: Technical support request"""
    print(f"\n{'#'*70}")
    print(f"# TEST SCENARIO 2: Technical Support")
    print(f"{'#'*70}\n")
    
    logger.info("Starting test scenario 2...")
    agent = create_support_agent()
    
    try:
        response = await agent.run(
            "I'm having trouble with the API. Getting 500 errors when I try to authenticate."
        )
        
        print(f"\n{'='*70}")
        print(f"AGENT RESPONSE:")
        print(f"{'='*70}")
        print(response.text)
        print(f"{'='*70}\n")
        logger.info("Test scenario 2 completed successfully")
        
    except Exception as e:
        logger.error(f"Error in test scenario 2: {e}")
        print(f"Error: {e}")


async def test_scenario_3_general_inquiry():
    """Test: General inquiry"""
    print(f"\n{'#'*70}")
    print(f"# TEST SCENARIO 3: General Inquiry")
    print(f"{'#'*70}\n")
    
    logger.info("Starting test scenario 3...")
    agent = create_support_agent()
    
    try:
        response = await agent.run(
            "What's your current service status? Any known issues?"
        )
        
        print(f"\n{'='*70}")
        print(f"AGENT RESPONSE:")
        print(f"{'='*70}")
        print(response.text)
        print(f"{'='*70}\n")
        logger.info("Test scenario 3 completed successfully")
        
    except Exception as e:
        logger.error(f"Error in test scenario 3: {e}")
        print(f"Error: {e}")


async def test_scenario_4_multi_turn():
    """Test: Multi-turn conversation"""
    print(f"\n{'#'*70}")
    print(f"# TEST SCENARIO 4: Multi-Turn Conversation")
    print(f"{'#'*70}\n")
    
    logger.info("Starting test scenario 4...")
    agent = create_support_agent()
    
    try:
        # First turn
        print("User: Can you check my account status?")
        response1 = await agent.run("Can you check my account status?")
        print(f"\nAgent: {response1.text[:200]}...\n")
        logger.info("First turn completed")
        
        # Second turn
        print("User: What's my current plan?")
        response2 = await agent.run("What's my current plan?")
        print(f"\nAgent: {response2.text[:200]}...\n")
        logger.info("Second turn completed")
        print(f"{'='*70}\n")
        
    except Exception as e:
        logger.error(f"Error in test scenario 4: {e}")
        print(f"Error: {e}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main function to run the agent with DevUI"""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║    Advanced Customer Support Agent - With DevUI                            ║
║                                                                            ║
║  Features:                                                                 ║
║  • Microsoft Agent Framework (native components)                           ║
║  • Azure AI Foundry Global Standard (gpt-4o deployment)                    ║
║  • Multiple middleware layers (@chat_middleware)                           ║
║  • Custom AI functions as tools (@ai_function)                             ║
║  • Async wrapper for sync OpenAI client                                     ║
║  • Full async/await support                                                ║
║  • 🎨 DevUI - Web-based interactive interface                              ║
║                                                                            ║
║  DevUI will open at: http://localhost:8085                                 ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    logger.info("🚀 Initializing agent system...")
    
    try:
        # Create the agent
        agent = create_support_agent()
        logger.info("✅ Agent created successfully")
        
        # Serve with DevUI
        logger.info("🎨 Starting DevUI...")
        serve(entities=[agent], auto_open=True, host="localhost", port=8085)
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
