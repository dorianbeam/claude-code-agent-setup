import logging
import traceback

from beam_ai_core.executor.errors import RateLimitExceededError

from app.lib.modules.agents.agent_setup.models.agent_setup import (
    AgentGraphCreationState,
    AgentSetupStage,
)
from app.lib.modules.agents.agent_setup.stages.tool_matching.tool_matching import (
    select_integration_tools,
)
from app.lib.modules.agents.agent_setup.utils.agent_setup_utils import (
    set_failed_agent_setup_state,
    set_next_agent_setup_state,
)
from app.lib.modules.graphs.graph_task_executor.models.node_interrupt import (
    NodeInterrupt,
)

logger = logging.getLogger("app")


async def select_agent_tools(
    agent_setup_state: AgentGraphCreationState,
):
    # Get the Current Node from Agent Graph State
    agent_setup_session = agent_setup_state.agent_setup_session
    _agent_memory = agent_setup_state.agent_memory

    # Check if the Agent has an actual SOP Generated from previous Stage
    if not agent_setup_session.generated_graph:
        logger.error(
            "Agent Graph not specified for Agent... Cannot Generate Tools as Nodes are Unknown"
        )
        agent_setup_session = set_failed_agent_setup_state(
            error="Agent Graph not specified for Agent... Cannot Generate Tools as Nodes are Unknown",
            agent_setup=agent_setup_session,
        )
        raise NodeInterrupt(value=agent_setup_state)

    try:
        # NOTE: Generate Custom Tools for Prompt Type Nodes in the Generated Agent Graph
        selected_integration_tools = await select_integration_tools(
            agent=agent_setup_session.agent,
            generated_graph=agent_setup_session.generated_graph,
            trace_config=agent_setup_state.trace_config,
        )

        agent_setup_session.integration_tools = selected_integration_tools

        # Set the Next Stage for Tool Generation
        agent_setup_session = set_next_agent_setup_state(
            output="Tool Matching for Integrations completed successfully.",
            stage=AgentSetupStage.TOOL_GENERATION,
            agent_setup=agent_setup_session,
        )

        return agent_setup_state

    except RateLimitExceededError:
        raise

    except Exception as tool_matching_exc:
        logger.warning(
            f"Tool Matching @Integrations failed for Agent: {agent_setup_session.agent.name}\nReason: {tool_matching_exc}"
        )

        traceback.print_exc()

        agent_setup_session = set_failed_agent_setup_state(
            error=f"Tool Matching failed for Agent: {agent_setup_session.agent.name}",
            agent_setup=agent_setup_session,
        )

        raise NodeInterrupt(value=agent_setup_state)
