"""Utility functions for skill-chat."""

from typing import Any


def extract_text_from_response(response: Any) -> str:
    """Extract text from AgentScope ChatResponse.

    AgentScope 1.0.12 returns ChatResponse as a dict-like object with structure:
    {
        'content': [
            {'text': 'actual text'},  # TextBlock
            ...
        ],
        'id': '...',
        'created_at': '...',
        'type': 'chat',
        'usage': {...},
        'metadata': None
    }

    Args:
        response: ChatResponse object from model call

    Returns:
        Extracted text string

    Raises:
        ValueError: If response format is unexpected
    """
    # Handle dict-like ChatResponse
    if isinstance(response, dict) and 'content' in response:
        content_blocks = response['content']
        if content_blocks and len(content_blocks) > 0:
            # Get text from first block
            first_block = content_blocks[0]
            if isinstance(first_block, dict) and 'text' in first_block:
                return first_block['text']
            else:
                return str(first_block)
        else:
            raise ValueError("Empty content in response")

    # Fallback for unexpected formats
    if isinstance(response, str):
        return response

    # Try to convert to string as last resort
    return str(response)
