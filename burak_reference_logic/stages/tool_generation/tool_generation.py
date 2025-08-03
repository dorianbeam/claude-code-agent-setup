import asyncio
import logging
from typing import List

from beam_ai_core.tracing.langfuse import TraceConfig

from app.lib.modules.agents.agent_setup.models.agent_setup import AgentGraphTool
from app.lib.modules.graphs.agent_graph.graph_creation.strategies.multi_node.generate_graph_pydantic import (
    GeneratedGraph,
)
from app.lib.modules.tools.custom_tool.custom_tool_creator.custom_tool_creator import (
    create_custom_tool_prompt,
)

logger = logging.getLogger("app")


async def generate_custom_tools(
    generated_graph: GeneratedGraph,
    integration_tools: List[AgentGraphTool],
    trace_config: TraceConfig,
) -> List[AgentGraphTool]:
    try:
        prompt_nodes = [
            node
            for node in generated_graph.workflow_graph
            if node.tool_category == "prompt"
        ]

        # TODO: Use Input / Output Data From Integration Tools

        tool_generation_tasks = [
            create_custom_tool_prompt(
                task=f"Prompt Type: {node.action_type}\n Main objective: {node.node_objective}. \n Required Context: {node.node_context}",
                trace_config=trace_config,
            )
            for node in prompt_nodes
        ]

        generated_tools = await asyncio.gather(
            *tool_generation_tasks, return_exceptions=True
        )

        prompt_tools = [
            AgentGraphTool(
                node_id=node.node_id,
                tool_name=tool.title,
                tool_description=tool.tool_description,
                short_description=tool.short_description,
                tool_type="prompt",
                prompt=tool.prompt,
                action_type=node.action_type,
                input_parameters=[],
                output_parameters=[],
            )
            for tool, node in zip(generated_tools, prompt_nodes)
            if tool and not isinstance(tool, RuntimeError)
        ]

        return prompt_tools

    except Exception as tool_matching_exc:
        logger.error(f"Failed to Select Tools for Graph: {tool_matching_exc}")
        raise
