from datetime import datetime

from beam_ai_core.tracing.langfuse import TraceConfig

from app.lib.modules.agents.agent_setup.models.agent_setup import (
    AgentSetupSession,
    AgentSetupStage,
    AgentSetupStageMetadata,
    AgentSetupState,
    AgentSetupStatus,
)


def set_trace_ids(
    agent_setup: AgentSetupSession, trace_config: TraceConfig
) -> AgentSetupSession:

    trace_config.session_id = agent_setup.id
    trace_config.id = agent_setup.thread_id

    return trace_config


def initialize_agent_setup(agent_setup: AgentSetupSession) -> AgentSetupSession:
    # Set Start Time as Datetime String, if not set
    if not agent_setup.start_time:
        agent_setup.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Initialize Task State, if not set
    if not agent_setup.setup_state:
        agent_setup.setup_state = AgentSetupState(
            next=AgentSetupStage.SOP_GENERATION,
            stages=[],
        )

    # Set Task & Node Status to In Progress
    agent_setup.status = AgentSetupStatus.IN_PROGRESS

    return agent_setup


def set_finished_agent_setup_state(agent_setup: AgentSetupSession) -> AgentSetupSession:
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    agent_setup.status = AgentSetupStatus.COMPLETED

    # Set End Time as Datetime String
    agent_setup.end_time = end_time
    # Append the Final Stage with Success
    agent_setup.setup_state.stages.append(
        AgentSetupStageMetadata(
            stage=agent_setup.setup_state.next,
            success=True,
            timestamp=end_time,
            output="Tool Generation Successfully Completed.",
        )
    )

    agent_setup.setup_state.next = AgentSetupStage.CONNECT_INTEGRATIONS

    return agent_setup


def set_failed_agent_setup_state(
    error: str, agent_setup: AgentSetupSession
) -> AgentSetupSession:
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    agent_setup.status = AgentSetupStatus.FAILED
    # Set End Time as Datetime String
    agent_setup.end_time = end_time

    agent_setup.setup_state.stages.append(
        AgentSetupStageMetadata(
            # On a failed task, the next Stage is the current Stage, as it did not proceed
            stage=agent_setup.setup_state.next,
            success=False,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            output=error,
        )
    )

    return agent_setup


def set_next_agent_setup_state(
    output: str, stage: AgentSetupStage, agent_setup: AgentSetupSession
) -> AgentSetupSession:
    agent_setup.setup_state.stages.append(
        AgentSetupStageMetadata(
            stage=agent_setup.setup_state.next,
            success=True,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            output=output,
        )
    )
    agent_setup.setup_state.next = stage

    return agent_setup


def set_user_input_required_state(agent_setup: AgentSetupSession) -> AgentSetupSession:
    agent_setup.status = AgentSetupStatus.USER_INPUT_REQUIRED

    return agent_setup
