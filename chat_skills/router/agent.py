"""Skill Router Agent with JSON schema validation."""

import json
import asyncio
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

from agentscope.model import ChatModelBase
from agentscope.message import Msg

from chat_skills.utils import extract_text_from_response


class RoutingDecision(BaseModel):
    """Schema for router decision output."""

    use_skills: bool = Field(
        description="Whether to use any skills for this query"
    )
    selected_skills: List[str] = Field(
        default_factory=list,
        description="List of skill names to use (0 to N skills)"
    )
    rationale: str = Field(
        description="One short sentence explaining the decision"
    )

    @field_validator('rationale')
    @classmethod
    def rationale_must_be_short(cls, v: str) -> str:
        """Ensure rationale is concise."""
        if len(v) > 200:
            return v[:197] + "..."
        return v


class SkillRouterAgent:
    """Agent that routes user queries to appropriate skills."""

    def __init__(
        self,
        name: str,
        model: ChatModelBase,
        skill_index: str,
        available_skills: List[str],
        max_skills: int = 3,
        max_retries: int = 2,
    ):
        """Initialize the skill router agent.

        Args:
            name: Agent name
            model: ChatModelBase instance for routing decisions
            skill_index: String containing skill descriptions
            available_skills: List of valid skill names
            max_skills: Maximum number of skills to select (default 3)
            max_retries: Maximum retries for JSON parsing (default 2)
        """
        self.name = name
        self.model = model
        self.skill_index = skill_index
        self.available_skills = available_skills
        self.max_skills = max_skills
        self.max_retries = max_retries

        # Build system prompt
        self.sys_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """Build the system prompt for routing."""
        return f"""You are a skill routing assistant. Your job is to analyze user queries and decide whether to use specialized skills to handle them.

{self.skill_index}

INSTRUCTIONS:
1. Analyze the user's message carefully
2. Decide if any skills would be helpful (0 to {self.max_skills} skills)
3. Only select skills that are DIRECTLY relevant to the user's request
4. Respond with ONLY a JSON object, no other text

OUTPUT FORMAT (strict JSON only):
{{
  "use_skills": true or false,
  "selected_skills": ["skill_name_1", "skill_name_2"],
  "rationale": "One short sentence"
}}

RULES:
- selected_skills must contain 0 to {self.max_skills} skill names
- Only use skill names from the available skills list
- For casual chat or simple queries, use_skills should be false
- The rationale must be one concise sentence

VALID SKILL NAMES:
{', '.join(self.available_skills) if self.available_skills else 'None'}

OUTPUT ONLY THE JSON OBJECT, NO OTHER TEXT."""

    async def reply_async(self, user_message: str) -> dict:
        """Process a message and return routing decision (async).

        Args:
            user_message: Input message from user

        Returns:
            Dictionary containing RoutingDecision or error fallback
        """
        # Try to get routing decision with retries
        for attempt in range(self.max_retries + 1):
            try:
                decision = await self._get_routing_decision(user_message, attempt)
                return decision.model_dump()
            except Exception as e:
                if attempt < self.max_retries:
                    # Retry
                    continue
                else:
                    # Final failure - fallback to no skills
                    print(f"Router failed after {self.max_retries + 1} attempts: {e}")
                    fallback = RoutingDecision(
                        use_skills=False,
                        selected_skills=[],
                        rationale="Routing failed, proceeding without skills"
                    )
                    return fallback.model_dump()

    def reply(self, user_message: str) -> dict:
        """Synchronous wrapper for reply_async."""
        return asyncio.run(self.reply_async(user_message))

    async def _get_routing_decision(
        self,
        user_message: str,
        attempt: int
    ) -> RoutingDecision:
        """Get routing decision from model with validation.

        Args:
            user_message: The user's query
            attempt: Current attempt number (for logging)

        Returns:
            Validated RoutingDecision

        Raises:
            ValueError: If JSON is invalid or doesn't match schema
            json.JSONDecodeError: If response is not valid JSON
        """
        # Call model with system prompt and user message
        messages = [
            {"role": "system", "content": self.sys_prompt},
            {"role": "user", "content": user_message}
        ]

        # Await the model call
        response = await self.model(messages)

        # Extract response text using utility function
        try:
            response_text = extract_text_from_response(response)
        except ValueError as e:
            raise ValueError(f"Failed to extract text from response: {e}") from e

        # Clean response (remove markdown code blocks if present)
        response_text = response_text.strip()
        if response_text.startswith("```"):
            # Remove code block markers
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1] if len(lines) > 2 else lines)
            response_text = response_text.strip()
            if response_text.startswith("json"):
                response_text = response_text[4:].strip()

        # Parse JSON
        try:
            data = json.loads(response_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {response_text[:200]}") from e

        # Validate with Pydantic
        try:
            decision = RoutingDecision(**data)
        except Exception as e:
            raise ValueError(f"JSON doesn't match schema: {e}") from e

        # Additional validation: check skill names
        invalid_skills = [
            s for s in decision.selected_skills
            if s not in self.available_skills
        ]
        if invalid_skills:
            raise ValueError(
                f"Invalid skill names: {invalid_skills}. "
                f"Valid skills: {self.available_skills}"
            )

        # Check max skills limit
        if len(decision.selected_skills) > self.max_skills:
            raise ValueError(
                f"Too many skills selected: {len(decision.selected_skills)} "
                f"(max: {self.max_skills})"
            )

        return decision
