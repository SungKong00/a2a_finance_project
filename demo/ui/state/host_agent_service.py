import json
import os
import sys
import traceback
import uuid

from typing import Any

from a2a.types import FileWithBytes, Message, Part, Role, Task, TaskState
from service.client.client import ConversationClient
from service.types import (
    Conversation,
    CreateConversationRequest,
    Event,
    GetEventRequest,
    ListAgentRequest,
    ListConversationRequest,
    ListMessageRequest,
    ListTaskRequest,
    MessageInfo,
    PendingMessageRequest,
    RegisterAgentRequest,
    SendMessageRequest,
)

from .state import (
    AppState,
    SessionTask,
    StateConversation,
    StateEvent,
    StateMessage,
    StateTask,
    StockAnalysis,
)
from utils.json_parser import extract_json_from_response, identify_agent_type


server_url = 'http://localhost:12000'


async def ListConversations() -> list[Conversation]:
    client = ConversationClient(server_url)
    try:
        response = await client.list_conversation(ListConversationRequest())
        return response.result if response.result else []
    except Exception as e:
        print('Failed to list conversations: ', e)
    return []


async def SendMessage(message: Message) -> Message | MessageInfo | None:
    client = ConversationClient(server_url)
    try:
        response = await client.send_message(SendMessageRequest(params=message))
        return response.result
    except Exception as e:
        traceback.print_exc()
        print('Failed to send message: ', e)
    return None


async def CreateConversation() -> Conversation:
    client = ConversationClient(server_url)
    try:
        response = await client.create_conversation(CreateConversationRequest())
        return (
            response.result
            if response.result
            else Conversation(conversation_id='', is_active=False)
        )
    except Exception as e:
        print('Failed to create conversation', e)
    return Conversation(conversation_id='', is_active=False)


async def ListRemoteAgents():
    client = ConversationClient(server_url)
    try:
        response = await client.list_agents(ListAgentRequest())
        return response.result
    except Exception as e:
        print('Failed to read agents', e)


async def AddRemoteAgent(path: str):
    client = ConversationClient(server_url)
    try:
        await client.register_agent(RegisterAgentRequest(params=path))
    except Exception as e:
        print('Failed to register the agent', e)


async def GetEvents() -> list[Event]:
    client = ConversationClient(server_url)
    try:
        response = await client.get_events(GetEventRequest())
        return response.result if response.result else []
    except Exception as e:
        print('Failed to get events', e)
    return []


async def GetProcessingMessages():
    client = ConversationClient(server_url)
    try:
        response = await client.get_pending_messages(PendingMessageRequest())
        return dict(response.result)
    except Exception as e:
        print('Error getting pending messages', e)


def GetMessageAliases():
    return {}


async def GetTasks():
    client = ConversationClient(server_url)
    try:
        response = await client.list_tasks(ListTaskRequest())
        return response.result
    except Exception as e:
        print('Failed to list tasks ', e)
        return []


async def ListMessages(conversation_id: str) -> list[Message]:
    client = ConversationClient(server_url)
    try:
        response = await client.list_messages(
            ListMessageRequest(params=conversation_id)
        )
        return response.result if response.result else []
    except Exception as e:
        print('Failed to list messages ', e)
    return []


async def UpdateAppState(state: AppState, conversation_id: str):
    """Update the app state."""
    try:
        if conversation_id:
            state.current_conversation_id = conversation_id
            messages = await ListMessages(conversation_id)
            if not messages:
                state.messages = []
            else:
                state.messages = [convert_message_to_state(x) for x in messages]
                # Extract stock analysis from messages
                _update_stock_analysis(state, state.messages)
        conversations = await ListConversations()
        if not conversations:
            state.conversations = []
        else:
            state.conversations = [
                convert_conversation_to_state(x) for x in conversations
            ]

        state.task_list = []
        for task in await GetTasks():
            state.task_list.append(
                SessionTask(
                    context_id=extract_conversation_id(task),
                    task=convert_task_to_state(task),
                )
            )
        state.background_tasks = await GetProcessingMessages()
        state.message_aliases = GetMessageAliases()

        # Update loading state based on background tasks
        if state.background_tasks:
            # Still processing
            state.current_analysis.is_loading = True
        elif state.current_analysis.is_loading:
            # No more background tasks - stop loading regardless of data completeness
            # (some agents may have returned errors, which is fine)
            has_any_data = any([
                state.current_analysis.technical,
                state.current_analysis.fundamental,
                state.current_analysis.sentiment,
                state.current_analysis.risk,
            ])
            # Stop loading when background tasks are done
            state.current_analysis.is_loading = False
            print(f"[Loading] Completed. Has data: {has_any_data}")
    except Exception as e:
        print('Failed to update state: ', e)
        traceback.print_exc(file=sys.stdout)


def _update_stock_analysis(state: AppState, messages: list[StateMessage]):
    """Extract and update stock analysis from messages."""
    # Track what we've found
    found_data = {
        'technical': None,
        'fundamental': None,
        'sentiment': None,
        'risk': None,
    }
    ticker = None

    print(f"[Analysis] Processing {len(messages)} messages...")

    # Process messages in reverse to get most recent data
    for message in reversed(messages):
        print(f"[Analysis] Message role: '{message.role}'")
        if message.role != 'agent':
            continue

        print(f"[Analysis] Agent message, content count: {len(message.content)}")

        # First, concatenate ALL content parts into one string
        # This handles cases where JSON is split across multiple parts
        full_content = ""
        for content_part, media_type in message.content:
            print(f"[Analysis] Content type: {type(content_part).__name__}, media: {media_type}")
            print(f"[Analysis] RAW CONTENT (first 500 chars): {str(content_part)[:500]}")
            if isinstance(content_part, str):
                full_content += content_part + "\n"
            elif isinstance(content_part, dict):
                # If already a dict, process it directly
                json_data = content_part
                if 'ticker' in json_data:
                    agent_type = identify_agent_type(json_data)
                    if agent_type and agent_type in found_data and not found_data[agent_type]:
                        found_data[agent_type] = json_data
                        print(f"[Analysis] Direct dict found, identified as: {agent_type}")
                        if json_data.get('ticker') and not ticker:
                            ticker = json_data['ticker']

        # Now extract all JSON blocks from concatenated content
        print(f"[Analysis] Full concatenated content length: {len(full_content)}")

        # Try to extract multiple JSON blocks from the full content
        import re
        json_pattern = r'```json\s*([\s\S]*?)\s*```'
        matches = re.findall(json_pattern, full_content)

        if not matches:
            # Also try without json tag
            json_pattern2 = r'```\s*(\{[\s\S]*?\})\s*```'
            matches = re.findall(json_pattern2, full_content)

        print(f"[Analysis] Found {len(matches)} JSON blocks in full content")

        for json_str in matches:
            json_str = json_str.strip()
            try:
                import json as json_module
                json_data = json_module.loads(json_str)
            except:
                # Try to fix common issues
                json_str_fixed = json_str
                # Fix 1: Remove trailing commas
                json_str_fixed = re.sub(r',\s*([}\]])', r'\1', json_str_fixed)
                # Fix 2: Replace single quotes with double quotes (Python dict -> JSON)
                # But be careful not to replace quotes inside strings
                json_str_fixed = json_str_fixed.replace("'", '"')
                try:
                    json_data = json_module.loads(json_str_fixed)
                except:
                    # Fix 3: Try ast.literal_eval for Python dict format
                    try:
                        import ast
                        json_data = ast.literal_eval(json_str)
                    except:
                        print(f"[Analysis] Failed to parse JSON block: {json_str[:200]}...")
                        continue

            if not isinstance(json_data, dict):
                continue

            print(f"[Analysis] Found JSON with keys: {list(json_data.keys())[:5]}...")
            print(f"[Analysis] JSON DATA: {json_data}")

            agent_type = identify_agent_type(json_data)
            print(f"[Analysis] Identified as: {agent_type}")

            if agent_type and agent_type in found_data and not found_data[agent_type]:
                found_data[agent_type] = json_data
                if json_data.get('ticker') and not ticker:
                    ticker = json_data['ticker']

    print(f"[Analysis] Found data for: {[k for k, v in found_data.items() if v]}")

    # Update state if we found any analysis data
    if any(found_data.values()):
        if ticker:
            state.current_analysis.ticker = ticker
        if found_data['technical']:
            state.current_analysis.technical = found_data['technical']
        if found_data['fundamental']:
            state.current_analysis.fundamental = found_data['fundamental']
        if found_data['sentiment']:
            state.current_analysis.sentiment = found_data['sentiment']
        if found_data['risk']:
            state.current_analysis.risk = found_data['risk']

        # Extract recommendation and summary from any agent
        for data in found_data.values():
            if data:
                if data.get('recommendation') and not state.current_analysis.recommendation:
                    state.current_analysis.recommendation = data['recommendation']
                if data.get('summary') and not state.current_analysis.summary:
                    state.current_analysis.summary = data['summary']
                if data.get('confidence') and not state.current_analysis.confidence:
                    state.current_analysis.confidence = float(data.get('confidence', 0))

        print(f"[Analysis] Updated state with ticker={state.current_analysis.ticker}")


async def UpdateApiKey(api_key: str):
    """Update the API key"""
    import httpx

    try:
        # Set the environment variable
        os.environ['GOOGLE_API_KEY'] = api_key

        # Call the update API endpoint
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{server_url}/api_key/update', json={'api_key': api_key}
            )
            response.raise_for_status()
        return True
    except Exception as e:
        print('Failed to update API key: ', e)
        return False


def convert_message_to_state(message: Message) -> StateMessage:
    if not message:
        return StateMessage()

    return StateMessage(
        message_id=message.message_id,
        context_id=message.context_id if message.context_id else '',
        task_id=message.task_id if message.task_id else '',
        role=message.role.name,
        content=extract_content(message.parts),
    )


def convert_conversation_to_state(
    conversation: Conversation,
) -> StateConversation:
    return StateConversation(
        conversation_id=conversation.conversation_id,
        conversation_name=conversation.name,
        is_active=conversation.is_active,
        message_ids=[extract_message_id(x) for x in conversation.messages],
    )


def convert_task_to_state(task: Task) -> StateTask:
    # Get the first message as the description
    output = (
        [extract_content(a.parts) for a in task.artifacts]
        if task.artifacts
        else []
    )
    if not task.history:
        return StateTask(
            task_id=task.id,
            context_id=task.context_id,
            state=TaskState.failed.name,
            message=StateMessage(
                message_id=str(uuid.uuid4()),
                context_id=task.context_id,
                task_id=task.id,
                role=Role.agent.name,
                content=[('No history', 'text')],
            ),
            artifacts=output,
        )
    message = task.history[0]
    last_message = task.history[-1]
    if last_message != message:
        output = [extract_content(last_message.parts)] + output
    return StateTask(
        task_id=task.id,
        context_id=task.context_id,
        state=str(task.status.state),
        message=convert_message_to_state(message),
        artifacts=output,
    )


def convert_event_to_state(event: Event) -> StateEvent:
    return StateEvent(
        context_id=extract_message_conversation(event.content),
        actor=event.actor,
        role=event.content.role.name,
        id=event.id,
        content=extract_content(event.content.parts),
    )


def extract_content(
    message_parts: list[Part],
) -> list[tuple[str | dict[str, Any], str]]:
    parts: list[tuple[str | dict[str, Any], str]] = []
    if not message_parts:
        return []
    for part in message_parts:
        p = part.root
        if p.kind == 'text':
            parts.append((p.text, 'text/plain'))
        elif p.kind == 'file':
            if isinstance(p.file, FileWithBytes):
                parts.append((p.file.bytes, p.file.mime_type or ''))
            else:
                parts.append((p.file.uri, p.file.mime_type or ''))
        elif p.kind == 'data':
            try:
                jsonData = json.dumps(p.data)
                if 'type' in p.data and p.data['type'] == 'form':
                    parts.append((p.data, 'form'))
                else:
                    parts.append((jsonData, 'application/json'))
            except Exception as e:
                print('Failed to dump data', e)
                parts.append(('<data>', 'text/plain'))
    return parts


def extract_message_id(message: Message) -> str:
    return message.message_id


def extract_message_conversation(message: Message) -> str:
    return message.context_id if message.context_id else ''


def extract_conversation_id(task: Task) -> str:
    if task.context_id:
        return task.context_id
    # Tries to find the first conversation id for the message in the task.
    if task.status.message:
        return task.status.message.context_id or ''
    return ''
