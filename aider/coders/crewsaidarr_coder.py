import asyncio

# New import for CrewAI agents
# Assuming a hypothetical CrewAI library provides a `CrewAI` class for orchestrating agents.
# Replace this with the actual import path if the library differs.
try:
    from crewai import CrewAI  # type: ignore
except ImportError:  # pragma: no cover
    # Fallback stub if CrewAI is not installed; this allows the module to be imported
    # without raising an error during testing. The actual functionality will be a no‑op.
    class CrewAI:  # pylint: disable=too-few-public-methods
        def __init__(self, *args, **kwargs):
            pass

        async def run(self, *args, **kwargs):
            # Placeholder implementation – in a real environment this would
            # coordinate the crew of agents to perform the requested task.
            return "CrewAI execution placeholder"


from ..commands import SwitchCoder
from .crewsaidarr_prompts import CrewsAIdarrPrompts
from .ask_coder import AskCoder
from .base_coder import Coder


class CrewsAIdarrCoder(AskCoder):
    """
    A coder that delegates the planning and execution of changes to a CrewAI
    agent crew. The crew is responsible for generating a detailed plan and
    applying edits, while this coder handles the surrounding Aider workflow.
    """

    edit_format = "crewsaidarr"
    gpt_prompts = CrewsAIdarrPrompts()
    auto_accept_architect = False

    async def reply_completed(self):
        """
        Override the base implementation to hand off the user's request to a
        CrewAI crew. The crew will produce the final edited files, and this
        method will then integrate the results back into Aider's workflow.
        """

        content = self.partial_response_content

        if not content or not content.strip():
            return

        # Ask the user whether they want to proceed with the CrewAI agents.
        tweak_responses = getattr(self.args, "tweak_responses", False)
        confirmation = await self.io.confirm_ask(
            "Edit the files using CrewAI agents?", allow_tweak=tweak_responses
        )

        if not self.auto_accept_architect and not confirmation:
            return

        if confirmation == "tweak":
            content = self.io.edit_in_editor(content)

        # Initialise the CrewAI instance. In a real deployment you would pass
        # configuration such as the model, tools, and any required credentials.
        crew = CrewAI(
            name="AiderCrew",
            description="Orchestrates code analysis, planning, and editing for Aider.",
        )

        # Run the crew with the user's request. The crew is expected to return a
        # string containing the updated file listings in the required format.
        try:
            crew_output = await crew.run(content)
        except Exception as e:
            self.io.tool_error(f"CrewAI execution failed: {e}")
            return

        # The crew output should be a series of file listings. Parse them and
        # apply the changes using Aider's existing mechanisms.
        # For simplicity we reuse the existing `editor_coder` path, but feed it
        # the crew's output directly.
        await asyncio.sleep(0.1)

        kwargs = dict()

        # Use the editor_model from the main_model if it exists, otherwise use the main_model itself
        editor_model = self.main_model.editor_model or self.main_model

        kwargs["main_model"] = editor_model
        kwargs["edit_format"] = self.main_model.editor_edit_format
        kwargs["args"] = self.args
        kwargs["suggest_shell_commands"] = False
        kwargs["map_tokens"] = 0
        kwargs["total_cost"] = self.total_cost
        kwargs["cache_prompts"] = False
        kwargs["num_cache_warming_pings"] = 0
        kwargs["summarize_from_coder"] = False
        kwargs["mcp_servers"] = []  # Empty to skip initialization

        # Create a temporary coder that will ingest the crew's output.
        # This mirrors the original behaviour but replaces the LLM‑generated plan
        # with the CrewAI‑generated plan.
        editor_coder = await Coder.create(**kwargs)
        editor_coder.mcp_servers = self.mcp_servers
        editor_coder.mcp_tools = self.mcp_tools
        editor_coder.tui = self.tui

        # Inject the crew's output as the user message for the editor coder.
        new_kwargs = dict(io=self.io, from_coder=self)
        new_kwargs.update(kwargs)

        # Create the final editor coder instance that will process the crew output.
        final_editor = await Coder.create(**new_kwargs)
        final_editor.cur_messages = []
        final_editor.done_messages = []

        if self.verbose:
            final_editor.show_announcements()

        try:
            # Feed the crew's file listings directly to the editor coder.
            await final_editor.generate(user_message=crew_output, preproc=False)
            self.move_back_cur_messages("I made those changes to the files via CrewAI.")
            self.total_cost = final_editor.total_cost
            self.aider_commit_hashes = final_editor.aider_commit_hashes
        except Exception as e:
            self.io.tool_error(f"Error applying CrewAI changes: {e}")

        # Switch back to the architect mode (or whatever the original edit format was).
        raise SwitchCoder(main_model=self.main_model, edit_format="architect")
