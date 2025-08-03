import logging

from beam_ai_core.executor.errors import RateLimitExceededError

from app.lib.modules.agents.agent_setup.models.agent_setup import (
    AgentGraphCreationState,
    AgentSetupStage,
)
from app.lib.modules.agents.agent_setup.stages.sop_generation.sop_generation import (
    generate_sop,
)
from app.lib.modules.agents.agent_setup.utils.agent_setup_utils import (
    set_failed_agent_setup_state,
    set_next_agent_setup_state,
)
from app.lib.modules.graphs.graph_task_executor.models.node_interrupt import (
    NodeInterrupt,
)

logger = logging.getLogger("app")


async def generate_agent_sop(
    agent_setup_state: AgentGraphCreationState,
):
    # Get the Current Node from Agent Graph State
    agent_setup_session = agent_setup_state.agent_setup_session
    _agent_memory = agent_setup_state.agent_memory

    # Check if the Agent has an actual SOP Generated from previous Stage
    if not agent_setup_session.process_instructions:
        logger.error(
            "Process Instructions / Process Graph not specified for Agent... Cannot Create the Standard Operating Procedure"
        )
        agent_setup_session = set_failed_agent_setup_state(
            error="Process Instructions / Process Graph not specified for Agent... Cannot Create the Standard Operating Procedure",
            agent_setup=agent_setup_session,
        )
        raise NodeInterrupt(value=agent_setup_state)

    try:

        # NOTE: Generate Agent Graph from Given Standard Operating Procedure
        generated_agent_sop = await generate_sop(
            agent=agent_setup_session.agent,
            process_details=agent_setup_session.process_instructions,
            agent_memory=agent_setup_state.agent_memory,
            trace_config=agent_setup_state.trace_config,
        )

        agent_setup_session.agent_sop = generated_agent_sop

        # Set the Next Stage for Graph Generation
        agent_setup_session = set_next_agent_setup_state(
            output="SOP Generation completed successfully.",
            stage=AgentSetupStage.GRAPH_GENERATION,
            agent_setup=agent_setup_session,
        )

        return agent_setup_state

    except RateLimitExceededError:
        raise

    except Exception as sop_generation_exc:
        logger.warning(
            f"SOP Generation failed for Agent: {agent_setup_session.agent.name}\nReason: {sop_generation_exc}"
        )
        agent_setup_session = set_failed_agent_setup_state(
            error=f"SOP Generation failed for Agent: {agent_setup_session.agent.name}",
            agent_setup=agent_setup_session,
        )

        raise NodeInterrupt(value=agent_setup_state)
