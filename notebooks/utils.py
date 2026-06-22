from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import json

console = Console()

def format_message_content(message):
    """Convert message content to displayable string"""
    parts = []
    tool_calls_processed = False
    
    # Handle main content
    if isinstance(message.content, str):
        parts.append(message.content)
    elif isinstance(message.content, list):
        # Handle complex content like tool calls (Anthropic format)
        for item in message.content:
            if item.get('type') == 'text':
                parts.append(item['text'])
            elif item.get('type') == 'tool_use':
                parts.append(f"\n🔧 Tool Call: {item['name']}")
                parts.append(f"   Args: {json.dumps(item['input'], indent=2)}")
                parts.append(f"   ID: {item.get('id', 'N/A')}")
                tool_calls_processed = True
    else:
        parts.append(str(message.content))
    
    # Handle tool calls attached to the message (OpenAI format) - only if not already processed
    if not tool_calls_processed and hasattr(message, 'tool_calls') and message.tool_calls:
        for tool_call in message.tool_calls:
            parts.append(f"\n🔧 Tool Call: {tool_call['name']}")
            parts.append(f"   Args: {json.dumps(tool_call['args'], indent=2)}")
            parts.append(f"   ID: {tool_call['id']}")
    
    return "\n".join(parts)


def format_messages(messages):
    """Format and display a list of messages with Rich formatting"""
    for m in messages:
        msg_type = m.__class__.__name__.replace('Message', '')
        content = format_message_content(m)

        if msg_type == 'Human':
            console.print(Panel(content, title="🧑 Human", border_style="blue"))
        elif msg_type == 'Ai':
            console.print(Panel(content, title="🤖 Assistant", border_style="green"))
        elif msg_type == 'Tool':
            console.print(Panel(content, title="🔧 Tool Output", border_style="yellow"))
        else:
            console.print(Panel(content, title=f"📝 {msg_type}", border_style="white"))


def format_message(messages):
    """Alias for format_messages for backward compatibility"""
    return format_messages(messages)


def show_prompt(prompt_text: str, title: str = "Prompt", border_style: str = "blue"):
    """
    Display a prompt with rich formatting and XML tag highlighting.
    
    Args:
        prompt_text: The prompt string to display
        title: Title for the panel (default: "Prompt")
        border_style: Border color style (default: "blue")
    """
    # Create a formatted display of the prompt
    formatted_text = Text(prompt_text)
    formatted_text.highlight_regex(r'<[^>]+>', style="bold blue")  # Highlight XML tags
    formatted_text.highlight_regex(r'##[^#\n]+', style="bold magenta")  # Highlight headers
    formatted_text.highlight_regex(r'###[^#\n]+', style="bold cyan")  # Highlight sub-headers

    # Display in a panel for better presentation
    console.print(Panel(
        formatted_text, 
        title=f"[bold green]{title}[/bold green]",
        border_style=border_style,
        padding=(1, 2)
    ))


def show_command_demo():
    """
    Display an interactive widget comparing a vague vs. specific user message
    and the resulting Command(goto=..., update=...) returned by clarify_with_user.

    Two buttons let the user toggle between the two example cases and see how
    `goto` and `update` change depending on whether clarification is needed.
    """
    import ipywidgets as widgets
    from IPython.display import display, HTML

    # Two example cases mirroring real clarify_with_user behaviour
    cases = {
        "vague": {
            "user_message": "I want to research AI in healthcare.",
            "need_clarification": True,
            "goto": "END",
            "update_preview": (
                'messages: [AIMessage("Could you clarify which area of healthcare? '
                'E.g. diagnostics, drug discovery, patient monitoring...")]'
            ),
            "color": "#FAECE7",
            "text_color": "#712B13",
        },
        "specific": {
            "user_message": (
                "Research AI tools for early sepsis detection in ICU patients, "
                "comparing accuracy across studies from 2023-2025."
            ),
            "need_clarification": False,
            "goto": "write_research_brief",
            "update_preview": 'messages: [AIMessage("Got it — starting the research now.")]',
            "color": "#E1F5EE",
            "text_color": "#085041",
        },
    }

    output = widgets.Output()

    def render(case_key):
        c = cases[case_key]
        output.clear_output()
        with output:
            display(HTML(f"""
            <div style="font-family: sans-serif; max-width: 560px;">
                <p style="font-size:13px; color:#888; margin:0 0 4px;">User message</p>
                <p style="font-size:15px; font-weight:600; margin:0 0 16px;">"{c['user_message']}"</p>

                <p style="font-size:13px; color:#888; margin:0 0 4px;">
                    need_clarification =
                    <span style="background:{c['color']}; color:{c['text_color']}; padding:2px 8px; border-radius:6px; font-weight:600;">
                        {c['need_clarification']}
                    </span>
                </p>

                <div style="border:1px solid #ddd; border-radius:10px; padding:12px 16px; margin-top:16px;">
                    <p style="font-size:13px; color:#888; margin:0 0 10px; font-weight:600;">Command object returned</p>
                    <p style="font-family:monospace; font-size:13px; margin:0 0 8px;">
                        goto = <span style="background:{c['color']}; color:{c['text_color']}; padding:2px 8px; border-radius:6px;">"{c['goto']}"</span>
                    </p>
                    <p style="font-family:monospace; font-size:13px; margin:0;">
                        update = {{{c['update_preview']}}}
                    </p>
                </div>
            </div>
            """))

    btn_vague = widgets.Button(description="Vague message")
    btn_specific = widgets.Button(description="Specific message")

    btn_vague.on_click(lambda b: render("vague"))
    btn_specific.on_click(lambda b: render("specific"))

    display(widgets.HBox([btn_vague, btn_specific]))
    display(output)
    render("vague")  # show the vague case by default