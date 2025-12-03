"""
Simple test to check if agent returns JSON format (no MCP call)
"""
import asyncio
import json
from a2a.client import A2ACardResolver, ClientConfig, ClientFactory
from a2a.types import Message, Part, TextPart, Role

async def test_simple_json():
    """
    Test if agent can return JSON format without calling MCP
    """
    print("=" * 80)
    print("Testing Agent JSON Response (No MCP)")
    print("=" * 80)

    agent_url = "http://localhost:10101"
    # Simple test message that doesn't require real data
    test_message = """
    Don't call any tools. Just return a test JSON response in this format:

    {
      "analysis_text": "This is a test analysis",
      "artifacts": {
        "test_data": {
          "description": "Test data",
          "data": {"value": 123}
        }
      },
      "metadata": {
        "ticker": "TEST",
        "agent": "technical_analyst",
        "timestamp": "2025-12-03T10:00:00Z"
      }
    }
    """

    try:
        import httpx

        async with httpx.AsyncClient(timeout=60.0) as http_client:
            card_resolver = A2ACardResolver(http_client, agent_url)

            print("🔍 Resolving agent card...")
            agent_card = await card_resolver.get_agent_card()
            print(f"✅ Agent: {agent_card.name}\n")

            config = ClientConfig()
            client_factory = ClientFactory(config)
            agent_client = client_factory.create(agent_card)

            import uuid
            message = Message(
                role=Role.user,
                parts=[Part(root=TextPart(text=test_message))],
                message_id=str(uuid.uuid4())
            )

            print("📤 Sending message to agent...")

            response_message = None
            from a2a.types import Task, TaskState
            async for event in agent_client.send_message(message):
                if isinstance(event, Message):
                    response_message = event
                    break
                # Handle Task events (status updates)
                if isinstance(event, tuple) and len(event) > 0:
                    task = event[0]
                    if isinstance(task, Task):
                        print(f"Task status: {task.status.state}")
                        # When task is completed, extract artifacts
                        if task.status.state == TaskState.completed:
                            # Extract text from task artifacts
                            if task.artifacts and len(task.artifacts) > 0:
                                # Get the first artifact
                                artifact = task.artifacts[0]
                                # Extract text from artifact parts
                                for part in artifact.parts:
                                    if hasattr(part, 'root') and isinstance(part.root, TextPart):
                                        response_message = part.root
                                        break
                            # Also check task.status.message
                            if not response_message and hasattr(task.status, 'message') and task.status.message:
                                response_message = task.status.message
                            break

        if response_message:
            print("✅ Response received!\n")

            # Extract text content
            message_content = ""
            if isinstance(response_message, TextPart):
                message_content = response_message.text
            else:
                # It's a Message object with parts
                for part in response_message.parts:
                    if part.root and isinstance(part.root, TextPart):
                        message_content += part.root.text

            print("RAW RESPONSE:")
            print("=" * 80)
            print(message_content)
            print("=" * 80)

            # Try to parse JSON
            try:
                content_to_parse = message_content.strip()
                if content_to_parse.startswith("```json"):
                    content_to_parse = content_to_parse[7:]
                if content_to_parse.startswith("```"):
                    content_to_parse = content_to_parse[3:]
                if content_to_parse.endswith("```"):
                    content_to_parse = content_to_parse[:-3]

                parsed = json.loads(content_to_parse.strip())

                print("\n✅ JSON PARSING SUCCESS!")
                print("\nParsed JSON:")
                print(json.dumps(parsed, indent=2))
                return True

            except json.JSONDecodeError as e:
                print(f"\n❌ JSON Parsing FAILED: {e}")
                return False
        else:
            print("❌ No response received")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    asyncio.run(test_simple_json())
