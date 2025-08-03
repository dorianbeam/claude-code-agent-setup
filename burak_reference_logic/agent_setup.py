import logging
from typing import Awaitable, Callable, List

from beam_ai_core.executor.errors import RateLimitExceededError
from beam_ai_core.tracing.langfuse import TraceConfig

from app.lib.modules.agents.agent_setup.models.agent_setup import (
    AgentGraphCreationState,
    AgentSetupSession,
    AgentSetupStage,
    AgentSetupStatus,
)
from app.lib.modules.agents.agent_setup.stages.graph_generation.graph_generation_handler import (
    generate_agent_graph,
)
from app.lib.modules.agents.agent_setup.stages.sop_generation.sop_generation_handler import (
    generate_agent_sop,
)
from app.lib.modules.agents.agent_setup.stages.tool_generation.tool_generation_handler import (
    generate_agent_tools,
)
from app.lib.modules.agents.agent_setup.stages.tool_matching.tool_matching_handler import (
    select_agent_tools,
)
from app.lib.modules.agents.agent_setup.utils.agent_setup_utils import (
    initialize_agent_setup,
    set_failed_agent_setup_state,
    set_trace_ids,
)
from app.lib.modules.graphs.graph_task_executor.models.node_interrupt import (
    NodeInterrupt,
)

logger = logging.getLogger("app")


TERMINAL_TASK_STATES = [
    AgentSetupStatus.COMPLETED,
    AgentSetupStatus.USER_INPUT_REQUIRED,
]


async def setup_agent(
    agent_setup: AgentSetupSession,
    streaming_handlers: List[Callable],
    trace_config: TraceConfig,
    on_exit: Callable[[AgentSetupSession], Awaitable[None]] = None,
) -> AgentSetupSession:
    # Main Entry Function
    if agent_setup.status in TERMINAL_TASK_STATES:
        raise ValueError(
            "Agent Setup Status is already in Terminal State, Cannot Proceed"
        )

    # NOTE: Initialize Session Data
    agent_setup = initialize_agent_setup(agent_setup=agent_setup)

    # Set the Session Id to Setup Session ID
    if trace_config:
        trace_config = set_trace_ids(
            agent_setup=agent_setup,
            trace_config=trace_config,
        )

    try:
        # agent_memory = AgentTaskMemory(
        #     agent_memory_config=AgentMemoryConfig(
        #         agent_id=agent_setup.agent.id,
        #         task_id=agent_setup.id,
        #         thread_id=agent_setup.thread_id,
        #         user_id=agent_setup.user_id,
        #         vectordb_id=agent_setup.agent.vector_db_id,
        #     ),
        #     trace_config=trace_config,
        # )

        agent_setup_state = AgentGraphCreationState(
            agent_setup_session=agent_setup,
            agent_memory=None,
            streaming_handlers=streaming_handlers,
            trace_config=trace_config,
        )

    except Exception as agent_setup_exc:
        logger.error(
            "Something went wrong while starting Agent Graph Creation process..."
        )
        raise agent_setup_exc
    # Execute Graph until it Stops via Node Interrupt (Completed/Failed/UserInput & Consent)
    try:
        while agent_setup_state.agent_setup_session.status not in TERMINAL_TASK_STATES:
            agent_setup_state = await run_setup_stage(
                agent_setup_state=agent_setup_state
            )

    # Handle Terminal States
    except NodeInterrupt as node_interrupt:
        session_status = agent_setup_state.agent_setup_session.status

        match session_status:
            case AgentSetupStatus.FAILED:
                logger.error("Agent Setup & Graph Creation Failed")
                raise node_interrupt

            case AgentSetupStatus.USER_INPUT_REQUIRED:
                logger.warning("User Input Required")

    # Handle Errors & Exceptions
    except RateLimitExceededError:
        agent_setup = set_failed_agent_setup_state(
            "Rate Limit Exceeded", agent_setup=agent_setup
        )
        raise

    except Exception as agent_setup_exc:
        agent_setup = set_failed_agent_setup_state(
            f"Something went wrong while executing the Graph: {agent_setup_exc}",
            agent_setup=agent_setup,
        )
        raise agent_setup_exc

    return agent_setup_state.agent_setup_session


async def run_setup_stage(agent_setup_state: AgentGraphCreationState):
    logger.info(
        f"Running Agent Setup Pipeline... for Stage: {agent_setup_state.agent_setup_session.setup_state.next}"
    )

    logger.info(f"Agent Setup State: {agent_setup_state.agent_setup_session.status}")

    try:
        match agent_setup_state.agent_setup_session.setup_state.next.value:

            case AgentSetupStage.SOP_GENERATION.value:
                agent_setup_state = await generate_agent_sop(agent_setup_state)
            case AgentSetupStage.GRAPH_GENERATION.value:
                agent_setup_state = await generate_agent_graph(agent_setup_state)
            case AgentSetupStage.TOOL_MATCHING.value:
                agent_setup_state = await select_agent_tools(agent_setup_state)
            case AgentSetupStage.TOOL_GENERATION.value:
                agent_setup_state = await generate_agent_tools(agent_setup_state)

        return agent_setup_state

    except Exception:
        raise
