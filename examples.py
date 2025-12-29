"""
Example usage scenarios for the Advanced Customer Support Agent

This file demonstrates various ways to use the agent in your applications.
"""

import asyncio
import os
from advanced_customer_support_agent import (
    AdvancedCustomerSupportAgent,
    CustomerSupportTools,
    ChatContext
)


async def example_1_simple_query():
    """
    Example 1: Simple one-off query
    Perfect for: Quick questions, FAQ lookups
    """
    print("\n=== Example 1: Simple Query ===\n")
    
    agent = AdvancedCustomerSupportAgent(agent_name="SimpleBot")
    
    response = await agent.process_message(
        user_message="What is your return policy?",
        customer_id="CUST-00001"
    )
    
    print(f"Question: What is your return policy?")
    print(f"Answer: {response.message.content}")
    print(f"Processing time: {response.metadata.get('processing_timestamp')}")


async def example_2_multi_turn_conversation():
    """
    Example 2: Multi-turn conversation with context
    Perfect for: Complex support issues requiring multiple interactions
    """
    print("\n=== Example 2: Multi-Turn Conversation ===\n")
    
    agent = AdvancedCustomerSupportAgent(agent_name="ConversationalBot")
    context = None
    customer_id = "CUST-00002"
    
    conversation = [
        "Hi, I have a problem with my recent order",
        "I was charged twice for the same item",
        "Yes, please create a ticket for this issue",
        "Thank you!"
    ]
    
    for i, message in enumerate(conversation, 1):
        print(f"\nTurn {i}")
        print(f"Customer: {message}")
        
        response = await agent.process_message(
            user_message=message,
            context=context,
            customer_id=customer_id,
            session_id=f"session_{customer_id}"
        )
        
        print(f"Agent: {response.message.content}")
        
        # Update context for next turn
        context = response.context
    
    # Show conversation summary
    print("\n--- Conversation Summary ---")
    summary = agent.get_conversation_summary(context)
    print(f"Total turns: {summary['total_turns']}")
    print(f"Total messages: {summary['total_messages']}")
    print(f"Session ID: {summary['session_id']}")


async def example_3_ticket_workflow():
    """
    Example 3: Complete ticket lifecycle
    Perfect for: Issue tracking and resolution
    """
    print("\n=== Example 3: Ticket Workflow ===\n")
    
    agent = AdvancedCustomerSupportAgent(agent_name="TicketBot")
    customer_id = "CUST-00003"
    
    # Step 1: Create a ticket
    print("Step 1: Creating support ticket...")
    response1 = await agent.process_message(
        user_message="I need help with a technical issue. The app keeps crashing.",
        customer_id=customer_id
    )
    print(f"Agent: {response1.message.content}\n")
    
    # Extract ticket ID from response
    import re
    ticket_match = re.search(r'TICKET-\d+', response1.message.content)
    
    if ticket_match:
        ticket_id = ticket_match.group(0)
        
        # Step 2: Check ticket status
        print(f"Step 2: Checking status of {ticket_id}...")
        response2 = await agent.process_message(
            user_message=f"What's the status of {ticket_id}?",
            context=response1.context,
            customer_id=customer_id
        )
        print(f"Agent: {response2.message.content}")


async def example_4_using_tools_directly():
    """
    Example 4: Using customer support tools directly
    Perfect for: Integration with other systems, custom workflows
    """
    print("\n=== Example 4: Direct Tool Usage ===\n")
    
    tools = CustomerSupportTools()
    
    # Search knowledge base
    print("Searching knowledge base for 'shipping'...")
    kb_result = tools.search_knowledge_base("shipping")
    print(f"Result: {kb_result}\n")
    
    # Create a ticket
    print("Creating a priority ticket...")
    ticket = tools.create_support_ticket(
        customer_id="CUST-00004",
        issue_description="Urgent: Payment not processing",
        priority="high"
    )
    print(f"Ticket created: {ticket['ticket_id']}")
    print(f"Status: {ticket['status']}\n")
    
    # Get customer info
    print("Retrieving customer information...")
    customer_info = tools.get_customer_info("CUST-00004")
    print(f"Customer: {customer_info['name']}")
    print(f"Tier: {customer_info['tier']}")
    print(f"Total purchases: {customer_info['total_purchases']}")


async def example_5_context_state_management():
    """
    Example 5: Advanced context and state management
    Perfect for: Personalized experiences, session management
    """
    print("\n=== Example 5: Context State Management ===\n")
    
    agent = AdvancedCustomerSupportAgent(agent_name="StateBot")
    context = ChatContext()
    
    # Set custom state
    context.update_state('user_preference', 'email')
    context.update_state('preferred_language', 'en')
    context.update_state('vip_customer', True)
    
    customer_id = "CUST-VIP-001"
    
    # First interaction
    response1 = await agent.process_message(
        user_message="I need support",
        context=context,
        customer_id=customer_id,
        session_id="vip_session_001"
    )
    
    print(f"Customer: I need support")
    print(f"Agent: {response1.message.content}\n")
    
    # Access state in next interaction
    response2 = await agent.process_message(
        user_message="What information do you have about me?",
        context=response1.context,
        customer_id=customer_id
    )
    
    print(f"Customer: What information do you have about me?")
    print(f"Agent: {response2.message.content}\n")
    
    # Show context state
    print("Current Context State:")
    for key, value in response2.context.state.items():
        print(f"  {key}: {value}")


async def example_6_conversation_export():
    """
    Example 6: Exporting conversations
    Perfect for: Archiving, analysis, compliance
    """
    print("\n=== Example 6: Conversation Export ===\n")
    
    agent = AdvancedCustomerSupportAgent(agent_name="ExportBot")
    context = None
    
    # Have a brief conversation
    messages = [
        "Hello, I need help",
        "What are your business hours?",
        "Thank you!"
    ]
    
    for msg in messages:
        response = await agent.process_message(
            user_message=msg,
            context=context,
            customer_id="CUST-00006"
        )
        context = response.context
    
    # Export as JSON
    print("Exporting conversation as JSON...")
    json_export = agent.export_conversation(context, format='json')
    print(json_export[:500] + "...\n")
    
    # Export as text
    print("Exporting conversation as text...")
    text_export = agent.export_conversation(context, format='text')
    print(text_export)


async def example_7_metrics_and_analytics():
    """
    Example 7: Accessing metrics and analytics
    Perfect for: Monitoring, optimization, reporting
    """
    print("\n=== Example 7: Metrics and Analytics ===\n")
    
    agent = AdvancedCustomerSupportAgent(agent_name="MetricsBot")
    
    # Process several messages to generate metrics
    messages = [
        "This is great service!",
        "I'm very happy with your help",
        "You solved my problem quickly"
    ]
    
    for msg in messages:
        await agent.process_message(msg, customer_id="CUST-00007")
    
    # Access metrics
    metrics = agent.middleware_manager.metrics
    
    print("Agent Metrics:")
    print(f"  Total Requests: {metrics.total_requests}")
    print(f"  Total Tokens: {metrics.total_tokens}")
    print(f"  Error Count: {metrics.error_count}")
    print(f"  Average Response Time: {metrics.average_response_time:.3f}s")
    
    if metrics.sentiment_scores:
        avg_sentiment = sum(metrics.sentiment_scores) / len(metrics.sentiment_scores)
        print(f"  Average Sentiment: {avg_sentiment:.2f} (range: -1 to 1)")
        print(f"  Sentiment Scores: {[f'{s:.2f}' for s in metrics.sentiment_scores]}")


async def example_8_error_handling():
    """
    Example 8: Error handling and validation
    Perfect for: Robust applications, security
    """
    print("\n=== Example 8: Error Handling ===\n")
    
    agent = AdvancedCustomerSupportAgent(agent_name="ErrorBot")
    
    # Test 1: Normal operation
    print("Test 1: Normal message")
    try:
        response = await agent.process_message("What is your shipping policy?")
        print("✓ Success\n")
    except Exception as e:
        print(f"✗ Error: {e}\n")
    
    # Test 2: Blocked pattern (security)
    print("Test 2: Message with blocked pattern")
    try:
        response = await agent.process_message("<script>alert('test')</script>")
        print("✗ Should have been blocked\n")
    except ValueError as e:
        print(f"✓ Blocked as expected: {e}\n")
    
    # Test 3: Very long message (validation)
    print("Test 3: Very long message (over 5000 chars)")
    try:
        long_message = "A" * 6000
        response = await agent.process_message(long_message)
        print("✓ Handled (message was truncated)\n")
    except Exception as e:
        print(f"✗ Error: {e}\n")


async def example_9_azure_foundry_integration():
    """
    Example 9: Azure AI Foundry integration
    Perfect for: Production deployments
    """
    print("\n=== Example 9: Azure AI Foundry Integration ===\n")
    
    # Check if Foundry endpoint is configured
    foundry_endpoint = os.getenv('AZURE_AI_FOUNDRY_ENDPOINT')
    
    if foundry_endpoint:
        print(f"Connecting to Azure AI Foundry: {foundry_endpoint}")
        
        agent = AdvancedCustomerSupportAgent(
            agent_name="ProductionBot",
            foundry_endpoint=foundry_endpoint
        )
        
        response = await agent.process_message(
            user_message="Hello, I need production support",
            customer_id="CUST-PROD-001"
        )
        
        print(f"Agent: {response.message.content}")
    else:
        print("Azure AI Foundry endpoint not configured.")
        print("Set AZURE_AI_FOUNDRY_ENDPOINT in your .env file to enable.")
        print("See .env.template for configuration options.")


async def run_all_examples():
    """Run all examples in sequence"""
    examples = [
        ("Simple Query", example_1_simple_query),
        ("Multi-Turn Conversation", example_2_multi_turn_conversation),
        ("Ticket Workflow", example_3_ticket_workflow),
        ("Direct Tool Usage", example_4_using_tools_directly),
        ("Context State Management", example_5_context_state_management),
        ("Conversation Export", example_6_conversation_export),
        ("Metrics and Analytics", example_7_metrics_and_analytics),
        ("Error Handling", example_8_error_handling),
        ("Azure Foundry Integration", example_9_azure_foundry_integration),
    ]
    
    print("\n" + "="*70)
    print("ADVANCED CUSTOMER SUPPORT AGENT - EXAMPLE USAGE")
    print("="*70)
    
    for i, (name, example_func) in enumerate(examples, 1):
        print(f"\nRunning Example {i}: {name}")
        try:
            await example_func()
        except Exception as e:
            print(f"\nError in {name}: {e}")
        
        if i < len(examples):
            print("\n" + "-"*70)
    
    print("\n" + "="*70)
    print("All examples completed!")
    print("="*70 + "\n")


if __name__ == "__main__":
    # Load environment variables if .env file exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("Note: python-dotenv not installed. Environment variables from .env won't be loaded.")
    
    # Run all examples
    asyncio.run(run_all_examples())
    
    # Or run individual examples:
    # asyncio.run(example_1_simple_query())
    # asyncio.run(example_2_multi_turn_conversation())
    # asyncio.run(example_3_ticket_workflow())
    # asyncio.run(example_4_using_tools_directly())
    # asyncio.run(example_5_context_state_management())
    # asyncio.run(example_6_conversation_export())
    # asyncio.run(example_7_metrics_and_analytics())
    # asyncio.run(example_8_error_handling())
    # asyncio.run(example_9_azure_foundry_integration())
