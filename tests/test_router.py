"""Tests for skill router agent."""

import pytest
import json
import asyncio
from unittest.mock import Mock, MagicMock, AsyncMock

from chat_skills.router.agent import SkillRouterAgent, RoutingDecision


@pytest.fixture
def mock_model():
    """Create a mock model for testing that returns ChatResponse-compatible dict."""
    async def async_call(messages):
        # Return ChatResponse-compatible structure
        return {
            'content': [{'text': json.dumps({
                "use_skills": False,
                "selected_skills": [],
                "rationale": "Default response"
            })}],
            'id': 'test-id',
            'type': 'chat'
        }

    mock = MagicMock()
    mock.side_effect = async_call
    return mock


@pytest.fixture
def skill_index():
    """Sample skill index."""
    return """Available Skills:
- **PDF Summary**
  Summarize PDF documents
  Use when: user asks to summarize PDFs
- **Paper Review**
  Academic paper review framework
  Use when: user wants paper feedback
"""


@pytest.fixture
def available_skills():
    """List of available skill names."""
    return ["PDF Summary", "Paper Review"]


def test_routing_decision_validation():
    """Test RoutingDecision model validation."""
    # Valid decision
    decision = RoutingDecision(
        use_skills=True,
        selected_skills=["PDF Summary"],
        rationale="User needs PDF summary"
    )
    assert decision.use_skills is True
    assert len(decision.selected_skills) == 1

    # Valid no-skills decision
    decision2 = RoutingDecision(
        use_skills=False,
        selected_skills=[],
        rationale="Regular chat"
    )
    assert decision2.use_skills is False
    assert len(decision2.selected_skills) == 0


def test_routing_decision_long_rationale():
    """Test that long rationale is truncated."""
    long_text = "x" * 250
    decision = RoutingDecision(
        use_skills=False,
        selected_skills=[],
        rationale=long_text
    )
    assert len(decision.rationale) <= 200


def test_router_agent_initialization(skill_index, available_skills, mock_model):
    """Test router agent initialization."""
    agent = SkillRouterAgent(
        name="TestRouter",
        model=mock_model,
        skill_index=skill_index,
        available_skills=available_skills,
        max_skills=2
    )

    assert agent.name == "TestRouter"
    assert agent.max_skills == 2
    assert len(agent.available_skills) == 2
    assert "PDF Summary" in agent.sys_prompt
    assert "Paper Review" in agent.sys_prompt


def test_router_valid_json_response(skill_index, available_skills):
    """Test router with valid JSON response."""
    # Create a mock model that returns valid JSON in ChatResponse format
    async def mock_model_call(messages):
        return {
            'content': [{'text': json.dumps({
                "use_skills": True,
                "selected_skills": ["PDF Summary"],
                "rationale": "User needs PDF summary"
            })}],
            'id': 'test-id',
            'type': 'chat'
        }

    mock_model = MagicMock()
    mock_model.side_effect = mock_model_call

    agent = SkillRouterAgent(
        name="TestRouter",
        model=mock_model,
        skill_index=skill_index,
        available_skills=available_skills,
    )

    user_msg = "Summarize this PDF"
    response = agent.reply(user_msg)

    assert response["use_skills"] is True
    assert "PDF Summary" in response["selected_skills"]


def test_router_json_with_markdown_blocks(skill_index, available_skills):
    """Test router handling JSON wrapped in markdown blocks."""
    async def mock_model_call(messages):
        return {
            'content': [{'text': """```json
{
  "use_skills": true,
  "selected_skills": ["Paper Review"],
  "rationale": "User needs paper review"
}
```"""}],
            'id': 'test-id',
            'type': 'chat'
        }

    mock_model = MagicMock()
    mock_model.side_effect = mock_model_call

    agent = SkillRouterAgent(
        name="TestRouter",
        model=mock_model,
        skill_index=skill_index,
        available_skills=available_skills,
    )

    user_msg = "Review this paper"
    response = agent.reply(user_msg)

    assert response["use_skills"] is True
    assert "Paper Review" in response["selected_skills"]


def test_router_invalid_skill_name(skill_index, available_skills):
    """Test router rejects invalid skill names."""
    attempt = [0]  # Use list to allow modification in closure

    async def mock_model_call(messages):
        attempt[0] += 1
        if attempt[0] == 1:
            # First attempt: invalid skill name
            return {
                'content': [{'text': json.dumps({
                    "use_skills": True,
                    "selected_skills": ["Invalid Skill"],
                    "rationale": "Testing"
                })}],
                'id': 'test-id',
                'type': 'chat'
            }
        else:
            # Retry: fallback to no skills (system should handle this)
            return {
                'content': [{'text': json.dumps({
                    "use_skills": False,
                    "selected_skills": [],
                    "rationale": "Fallback"
                })}],
                'id': 'test-id',
                'type': 'chat'
            }

    mock_model = MagicMock()
    mock_model.side_effect = mock_model_call

    agent = SkillRouterAgent(
        name="TestRouter",
        model=mock_model,
        skill_index=skill_index,
        available_skills=available_skills,
        max_retries=2
    )

    user_msg = "Test"
    response = agent.reply(user_msg)

    # Should fallback after retry
    assert response["use_skills"] is False or attempt[0] > 1


def test_router_too_many_skills(skill_index, available_skills):
    """Test router enforces max_skills limit."""
    async def mock_model_call(messages):
        return {
            'content': [{'text': json.dumps({
                "use_skills": True,
                "selected_skills": ["PDF Summary", "Paper Review", "Extra Skill"],
                "rationale": "Testing"
            })}],
            'id': 'test-id',
            'type': 'chat'
        }

    mock_model = MagicMock()
    mock_model.side_effect = mock_model_call

    agent = SkillRouterAgent(
        name="TestRouter",
        model=mock_model,
        skill_index=skill_index,
        available_skills=available_skills,
        max_skills=2,
        max_retries=0  # No retries for this test
    )

    user_msg = "Test"
    response = agent.reply(user_msg)

    # Should fallback due to too many skills
    assert response["use_skills"] is False


def test_router_malformed_json(skill_index, available_skills):
    """Test router handles malformed JSON."""
    attempt = [0]

    async def mock_model_call(messages):
        attempt[0] += 1
        if attempt[0] == 1:
            return {
                'content': [{'text': "This is not valid JSON"}],
                'id': 'test-id',
                'type': 'chat'
            }
        else:
            # Fallback
            return {
                'content': [{'text': json.dumps({
                    "use_skills": False,
                    "selected_skills": [],
                    "rationale": "Fallback"
                })}],
                'id': 'test-id',
                'type': 'chat'
            }

    mock_model = MagicMock()
    mock_model.side_effect = mock_model_call

    agent = SkillRouterAgent(
        name="TestRouter",
        model=mock_model,
        skill_index=skill_index,
        available_skills=available_skills,
        max_retries=1
    )

    user_msg = "Test"
    response = agent.reply(user_msg)

    # Should eventually succeed or fallback
    assert "use_skills" in response


def test_router_no_skills_decision(skill_index, available_skills):
    """Test router deciding not to use skills."""
    async def mock_model_call(messages):
        return {
            'content': [{'text': json.dumps({
                "use_skills": False,
                "selected_skills": [],
                "rationale": "Casual conversation"
            })}],
            'id': 'test-id',
            'type': 'chat'
        }

    mock_model = MagicMock()
    mock_model.side_effect = mock_model_call

    agent = SkillRouterAgent(
        name="TestRouter",
        model=mock_model,
        skill_index=skill_index,
        available_skills=available_skills,
    )

    user_msg = "Hi there!"
    response = agent.reply(user_msg)

    assert response["use_skills"] is False
    assert len(response["selected_skills"]) == 0
