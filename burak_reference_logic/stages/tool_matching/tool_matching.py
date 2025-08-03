import asyncio
import logging
from typing import List

from beam_ai_core.tracing.langfuse import TraceConfig

from app.lib.modules.agents.agent.agent import Agent
from app.lib.modules.agents.agent_setup.models.agent_setup import AgentGraphTool
from app.lib.modules.graphs.agent_graph.graph_creation.strategies.multi_node.generate_graph_pydantic import (
    GeneratedGraph,
)
from app.lib.modules.tools.tools import fetch_tools_v2

logger = logging.getLogger("app")


async def select_integration_tools(
    agent: Agent, generated_graph: GeneratedGraph, trace_config: TraceConfig
) -> List[AgentGraphTool]:

    try:
        integration_nodes = [
            node
            for node in generated_graph.workflow_graph
            if node.tool_category == "integration"
        ]

        tool_selection_tasks = [
            fetch_tools_v2(
                task_step=f"Action Type: {node.action_type}\n Objective: {node.node_objective}. \n Required Context: {node.node_context}",
                workspace_id=agent.config.workspace_id,
                tool_database_top_k=20,
                workspace_id_database_top_k=20,
            )
            for node in integration_nodes
        ]

        selected_tools = await asyncio.gather(
            *tool_selection_tasks, return_exceptions=True
        )

        logger.debug(f"Selected Tools: {selected_tools}")

        integration_tools = [
            AgentGraphTool(
                node_id=node.node_id,
                tool_name=tool.name,
                tool_description=tool.description,
                tool_type="integration",
                action_type=node.action_type,
                input_parameters=tool.tool_parameters,
                integration_name=tool.integration,
            )
            for tool, node in zip(selected_tools, integration_nodes)
            if not isinstance(tool, RuntimeError)
        ]

        logger.debug(f"Selected Integration Tools: {integration_tools}")

        return integration_tools

    except Exception as tool_matching_exc:
        logger.error(f"Failed to Select Tools for Graph: {tool_matching_exc}")
        raise


async def classify_tool_categories():
    pass
