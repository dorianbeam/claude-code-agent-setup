import logging

from beam_ai_core.executor.errors import RateLimitExceededError

from app.lib.modules.agents.agent_setup.models.agent_setup import (
    AgentGraphCreationState,
    AgentSetupStage,
)
from app.lib.modules.agents.agent_setup.stages.graph_generation.graph_generation import (
    generate_graph,
)
from app.lib.modules.agents.agent_setup.utils.agent_setup_utils import (
    set_failed_agent_setup_state,
    set_next_agent_setup_state,
)
from app.lib.modules.graphs.graph_task_executor.models.node_interrupt import (
    NodeInterrupt,
)

logger = logging.getLogger("app")


async def generate_agent_graph(agent_setup_state: AgentGraphCreationState):
    # Get the Current Node from Agent Graph State
    agent_setup_session = agent_setup_state.agent_setup_session
    _agent_memory = agent_setup_state.agent_memory

    # Check if the Agent has an actual SOP Generated from previous Stage
    if not agent_setup_session.agent_sop:
        logger.error(
            "Standard Operating Procedure not specified for Agent... Cannot Create the Graph"
        )
        agent_setup_session = set_failed_agent_setup_state(
            error="Standard Operating Procedure not specified for Agent... Cannot Create the Graph",
            agent_setup=agent_setup_session,
        )
        raise NodeInterrupt(value=agent_setup_state)

    try:

        # NOTE: Generate Agent Graph from Given Standard Operating Procedure
        generated_agent_graph = await generate_graph(
            agent=agent_setup_session.agent,
            agent_sop=agent_setup_session.agent_sop,
            agent_memory=agent_setup_state.agent_memory,
            trace_config=agent_setup_state.trace_config,
            streaming_handlers=agent_setup_state.streaming_handlers,
        )

        agent_setup_session.generated_graph = generated_agent_graph

        # Otherwise, Set the Next Stage for Tool Matching
        agent_setup_session = set_next_agent_setup_state(
            output="Graph Generation completed successfully.",
            stage=AgentSetupStage.TOOL_MATCHING,
            agent_setup=agent_setup_session,
        )

        return agent_setup_state

    except RateLimitExceededError:
        raise

    except Exception as graph_generation_exc:
        logger.warning(
            f"Graph Generation failed for Agent: {agent_setup_session.agent.name}\nReason: {graph_generation_exc}"
        )
        agent_setup_session = set_failed_agent_setup_state(
            error=f"Graph Generation failed for Agent: {agent_setup_session.agent.name}",
            agent_setup=agent_setup_session,
        )

        raise NodeInterrupt(value=agent_setup_state)
