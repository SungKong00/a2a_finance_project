"""
Test script to verify Technical Analyst returns data in Artifacts format
"""
import asyncio
import json
from a2a.client import A2ACardResolver, ClientConfig, ClientFactory
from a2a.types import Message, Part, TextPart, Role

async def test_technical_analyst_artifacts():
    """
    Technical Analyst에게 분석 요청하고 Artifacts 형식 확인
    """
    print("=" * 80)
    print("Testing Technical Analyst Artifacts Response")
    print("=" * 80)

    # Technical Analyst URL
    agent_url = "http://localhost:10101"
    test_message = "Analyze AAPL stock with technical analysis"

    print(f"\n📤 Sending request to: {agent_url}")
    print(f"💬 Message: {test_message}\n")

    try:
        import httpx

        # A2A 클라이언트 생성 (timeout 증가 - MCP 호출 시간 고려)
        async with httpx.AsyncClient(timeout=300.0) as http_client:
            card_resolver = A2ACardResolver(http_client, agent_url)

            # Agent 카드 가져오기
            print("🔍 Resolving agent card...")
            agent_card = await card_resolver.get_agent_card()
            print(f"✅ Agent: {agent_card.name} ({agent_card.description})\n")

            # 클라이언트 생성
            config = ClientConfig()
            client_factory = ClientFactory(config)
            agent_client = client_factory.create(agent_card)

            # 메시지 생성
            import uuid
            message = Message(
                role=Role.user,
                parts=[Part(root=TextPart(text=test_message))],
                message_id=str(uuid.uuid4())
            )

            print("📤 Sending message to agent...")

            # 메시지 전송 및 응답 받기
            response_message = None
            from a2a.types import Task, TaskState
            async for event in agent_client.send_message(message):
                if isinstance(event, Message):
                    response_message = event
                    break
                # Handle Task events (for non-streaming agents)
                if isinstance(event, tuple) and len(event) > 0:
                    task = event[0]
                    if isinstance(task, Task):
                        print(f"⏳ Task status: {task.status.state}")
                        # When task is completed, extract artifacts
                        if task.status.state == TaskState.completed:
                            # Extract text from task artifacts
                            if task.artifacts and len(task.artifacts) > 0:
                                # Get the first artifact
                                artifact = task.artifacts[0]
                                # Extract text from artifact parts
                                for part in artifact.parts:
                                    if hasattr(part, 'root') and isinstance(part.root, TextPart):
                                        # Create a pseudo-Message for compatibility
                                        response_message = part.root
                                        break
                            break

        if response_message:
            print("✅ Response received!\n")
            print("=" * 80)
            print("RAW RESPONSE:")
            print("=" * 80)

            # 응답 내용 추출
            message_content = ""
            if isinstance(response_message, TextPart):
                message_content = response_message.text
            else:
                for part in response_message.parts:
                    if part.root and isinstance(part.root, TextPart):
                        message_content += part.root.text

            print(f"Message content length: {len(message_content)} characters")
            print(f"First 1000 chars:\n{message_content[:1000]}...")
            print("\n")

            # 응답 파싱 시도
            print("=" * 80)
            print("PARSING ANALYSIS:")
            print("=" * 80)

            # JSON 파싱 시도
            try:
                # LLM이 JSON을 마크다운 코드 블록으로 감싸서 반환할 수 있음
                content_to_parse = message_content.strip()

                # ```json ... ``` 제거
                if content_to_parse.startswith("```json"):
                    content_to_parse = content_to_parse[7:]
                if content_to_parse.startswith("```"):
                    content_to_parse = content_to_parse[3:]
                if content_to_parse.endswith("```"):
                    content_to_parse = content_to_parse[:-3]

                content_to_parse = content_to_parse.strip()

                parsed = json.loads(content_to_parse)

                print("\n✅ JSON Parsing SUCCESS!\n")

                # 분석 텍스트
                if 'analysis_text' in parsed:
                    print("📝 Analysis Text:")
                    print("-" * 80)
                    print(parsed['analysis_text'][:500] + "...")
                    print()

                # Artifacts 데이터
                if 'artifacts' in parsed:
                    print("📦 Artifacts Found:")
                    print("-" * 80)
                    artifacts = parsed['artifacts']

                    # Price Data
                    if 'price_data' in artifacts:
                        price_data = artifacts['price_data']['data']
                        print(f"  📈 Price Data: {len(price_data)} rows")
                        if price_data:
                            print(f"     First row: {price_data[0]}")
                            print(f"     Last row: {price_data[-1]}")

                    # Indicators
                    if 'indicators' in artifacts:
                        indicators = artifacts['indicators']['data']
                        print(f"  🔧 Indicators:")
                        print(f"     RSI: {indicators.get('rsi', 'N/A')}")
                        print(f"     MACD: {indicators.get('macd', 'N/A')}")
                        print(f"     SMAs: {indicators.get('moving_averages', 'N/A')}")

                    # Chart Annotations
                    if 'chart_annotations' in artifacts:
                        annotations = artifacts['chart_annotations']['data']
                        print(f"  🎯 Chart Annotations: {len(annotations)} levels")
                        for ann in annotations:
                            print(f"     {ann.get('type')}: ${ann.get('level')} ({ann.get('strength')})")

                    print()

                # Metadata
                if 'metadata' in parsed:
                    print("ℹ️  Metadata:")
                    print("-" * 80)
                    for key, value in parsed['metadata'].items():
                        print(f"  {key}: {value}")
                    print()

                print("=" * 80)
                print("✅ ARTIFACTS TEST PASSED!")
                print("=" * 80)
                print("\n✨ UI can now use this data to:")
                print("  - Display analysis text")
                print("  - Generate price charts (from price_data)")
                print("  - Show indicator values (from indicators)")
                print("  - Draw support/resistance lines (from chart_annotations)")

                return True

            except json.JSONDecodeError as e:
                print(f"\n❌ JSON Parsing FAILED: {e}")
                print("\n⚠️  Agent returned text but not in valid JSON format.")
                print("💡 Response might need manual inspection.")
                print(f"\nContent that failed to parse:\n{message_content[:500]}...")
                return False
        else:
            print("❌ No response received from agent")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    print("\n🚀 Starting Artifacts Test\n")

    success = await test_technical_analyst_artifacts()

    if success:
        print("\n🎉 Test completed successfully!")
        print("\n📋 Next Steps:")
        print("  1. ✅ Artifacts working!")
        print("  2. 🔄 Update other agents (Fundamental, Sentiment, Risk)")
        print("  3. 🎨 Update UI to use artifacts data")
    else:
        print("\n⚠️  Test failed. Please review the output above.")


if __name__ == "__main__":
    asyncio.run(main())
