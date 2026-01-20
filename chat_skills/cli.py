"""CLI interface for skill-aware chat."""

import os
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

import agentscope
from agentscope.model import OpenAIChatModel

from chat_skills.skills.loader import SkillLoader
from chat_skills.router.agent import SkillRouterAgent
from chat_skills.chat.agent import SkillChatAgent


console = Console()


def print_welcome():
    """Print welcome message."""
    console.print(Panel.fit(
        "[bold blue]Chat Skills - Dynamic Skill Injection Runtime[/bold blue]\n"
        "Type your message and press Enter. Type 'exit' or 'quit' to exit.\n"
        "Type 'reset' to clear conversation history.",
        border_style="blue"
    ))


def print_routing_info(decision: dict, show_routing: bool):
    """Print routing decision if enabled."""
    if not show_routing:
        return

    use_skills = decision.get("use_skills", False)
    selected = decision.get("selected_skills", [])
    rationale = decision.get("rationale", "")

    if use_skills and selected:
        console.print(
            f"[dim]🎯 Using skills: {', '.join(selected)}[/dim]",
            style="dim"
        )
        console.print(f"[dim]   Reason: {rationale}[/dim]\n", style="dim")
    else:
        console.print("[dim]💬 Regular chat (no skills)[/dim]\n", style="dim")


@click.command()
@click.option(
    "--skills-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=None,
    help="Path to skills directory (default: try .claude/skills, ~/.claude/skills, ./demo_skills)"
)
@click.option(
    "--router-model",
    type=str,
    default=None,
    help="Model name for skill routing (default: from env or chat-model)"
)
@click.option(
    "--chat-model",
    type=str,
    default=None,
    help="Model name for chat responses (default: from env)"
)
@click.option(
    "--show-routing/--no-show-routing",
    default=False,
    help="Show skill routing decisions before each response"
)
@click.option(
    "--max-skills",
    type=int,
    default=3,
    help="Maximum number of skills to use per query"
)
@click.option(
    "--api-key",
    type=str,
    default=None,
    help="API key for model provider (or set DEEPSEEK_API_KEY/OPENAI_API_KEY env var)"
)
@click.option(
    "--base-url",
    type=str,
    default=None,
    envvar="OPENAI_BASE_URL",
    help="Base URL for OpenAI-compatible API (default: https://api.openai.com/v1)"
)
def main(
    skills_dir: Optional[Path],
    router_model: Optional[str],
    chat_model: Optional[str],
    show_routing: bool,
    max_skills: int,
    api_key: Optional[str],
    base_url: Optional[str],
):
    """Start the skill-aware chat REPL."""

    # Set defaults
    if not chat_model:
        chat_model = os.getenv("CHAT_MODEL", "deepseek-chat")
    if not router_model:
        router_model = os.getenv("ROUTER_MODEL", chat_model)
    if not api_key:
        # Try DeepSeek first, then OpenAI
        api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")

    if not api_key:
        console.print(
            "[red]Error: No API key provided. Set DEEPSEEK_API_KEY or OPENAI_API_KEY env var or use --api-key[/red]"
        )
        sys.exit(1)

    # Auto-detect base URL for DeepSeek if not set
    if not base_url:
        base_url = os.getenv("OPENAI_BASE_URL")
        # If using DeepSeek API key but no base URL, set DeepSeek base URL
        if not base_url and os.getenv("DEEPSEEK_API_KEY"):
            base_url = "https://api.deepseek.com/v1"

    # Initialize AgentScope (simplified - just for logging)
    agentscope.init(project="skill-chat")

    # Create model instances
    client_kwargs = {}
    if base_url:
        client_kwargs["base_url"] = base_url

    router_model_instance = OpenAIChatModel(
        model_name=router_model,
        api_key=api_key,
        client_kwargs=client_kwargs,
        stream=False,  # Disable streaming for JSON parsing
    )

    chat_model_instance = OpenAIChatModel(
        model_name=chat_model,
        api_key=api_key,
        client_kwargs=client_kwargs,
        stream=False,
    )

    # Load skills
    console.print("[yellow]Loading skills...[/yellow]")
    loader = SkillLoader(skills_dir)
    skills = loader.load_skills()

    if not skills:
        console.print(
            f"[yellow]Warning: No skills found in {loader.skills_dir}[/yellow]"
        )
        console.print("[yellow]Continuing with regular chat mode...[/yellow]\n")

    skill_index = loader.generate_index()
    skill_names = loader.get_skill_names()

    console.print(f"[green]Loaded {len(skills)} skill(s)[/green]")
    if skills and show_routing:
        console.print("\n[dim]" + skill_index + "[/dim]\n")

    # Create agents
    router_agent = SkillRouterAgent(
        name="Router",
        model=router_model_instance,
        skill_index=skill_index,
        available_skills=skill_names,
        max_skills=max_skills,
    )

    chat_agent = SkillChatAgent(
        name="Assistant",
        model=chat_model_instance,
    )

    # Print welcome
    print_welcome()

    # REPL loop
    while True:
        try:
            # Get user input
            user_input = console.input("\n[bold green]You:[/bold green] ")

            if not user_input.strip():
                continue

            # Check for special commands
            if user_input.strip().lower() in ["exit", "quit"]:
                console.print("[yellow]Goodbye![/yellow]")
                break

            if user_input.strip().lower() == "reset":
                chat_agent.reset_memory()
                console.print("[yellow]Conversation history cleared.[/yellow]")
                continue

            # Phase A: Router decision
            if skills:
                with console.status("[dim]Routing...[/dim]"):
                    decision = router_agent.reply(user_input)

                print_routing_info(decision, show_routing)

                # Get selected skills
                selected_skill_objs = []
                if decision.get("use_skills", False):
                    for skill_name in decision.get("selected_skills", []):
                        skill = loader.get_skill_by_name(skill_name)
                        if skill:
                            selected_skill_objs.append(skill)
            else:
                selected_skill_objs = []

            # Phase B: Generate response with optional skill injection
            with console.status("[dim]Thinking...[/dim]"):
                response = chat_agent.reply(
                    user_input,
                    selected_skills=selected_skill_objs if selected_skill_objs else None
                )

            # Print response
            console.print("\n[bold blue]Assistant:[/bold blue]")
            console.print(Markdown(response))

        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted. Type 'exit' to quit.[/yellow]")
            continue
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            if os.getenv("DEBUG"):
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    main()
