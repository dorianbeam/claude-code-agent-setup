# TODO: Implement AgentSetupManager
import logging
from functools import partial
from typing import Any, Dict, Optional

from beam_ai_core.tracing.langfuse import TraceConfig
from pydantic import BaseModel

# from app.event_broker.event_listener import Job
# from app.event_broker.task_manager.base_task_manager import BaseTaskManager
from app.lib.modules.agents.agent_setup.agent_setup import setup_agent
from app.lib.modules.agents.agent_setup.models.agent_setup import (
    AgentSetupSession,
    AgentSetupStatus,
)
from app.lib.modules.graphs.graph_task_executor.graph_executor import (
    TERMINAL_TASK_STATES,
)

logger = logging.getLogger("app")

TERMINAL_JOB_STATES = [
    AgentSetupStatus.COMPLETED,
    AgentSetupStatus.USER_INPUT_REQUIRED,
]


class Job:
    pass


class JobData(BaseModel):
    task: Dict[str, Any]
    agent_setup_session: Optional[AgentSetupSession] = None


class AgentSetupManager:
    """
    Task Manager for Graph Task execution.
    """

    MAX_PARALLEL_JOBS = 1000
    QUEUE_MAX_RETRIES = 5
    TRACE_NAME = "AgentSetup"

    async def parse_job_data(self, job: Job) -> AgentSetupSession:
        """Parse job data into an AgentSetupSession."""
        # job = Job.model_validate_json(job)
        path = job.path
        data = job.data
        agent_setup_data = JobData.model_validate_json(data)

        # Check if the Event Data is a Graph Task, otherwise raise exception
        if not path.lower() == "agent-setup":
            raise ValueError(
                f"Invalid path for AgentSetupManager: {path}, expected 'agent-setup'"
            )

        # Validate Agent Setup Data
        if not agent_setup_data:
            raise ValueError("Missing Agent Setup Data in Job Payload")

        # Parse AgentSetupSession as AgentGraphTask
        job.data = agent_setup_data
        agent_setup_session = AgentSetupSession.model_validate(agent_setup_data.task)

        # Set AgentSetupSession as the JobData for preserving unaltered properties
        job.data.agent_setup_session = agent_setup_session

        return agent_setup_session

    async def queue_task(self, task: AgentSetupSession, job: Job) -> None:
        """Queue a graph task for execution."""
        # Check if Task is in Terminal State, set END JOB Flag
        if task.status in TERMINAL_JOB_STATES:
            job.endJob = True

        # Convert Agent Graph Task to new Beam Task Payload
        updated_setup_session: AgentSetupSession = task

        # Set Job Payload
        job.data.task = updated_setup_session.model_dump()
        job.data.agent_setup_session = None

        logger.info(
            f"Submitting Agent Setup Job back to the Queue... EndJob? : {job.endJob}"
        )

        # Publish to Redis Queue using the event listener
        await self.publish_job(job=job)

    async def run_once(
        self,
        task: AgentSetupSession,
        trace_config: TraceConfig,
        job: Optional[Job] = None,
        enable_notifications: bool = True,
        **kwargs,
    ) -> AgentSetupSession:
        """
        Runs a Graph Task Execution Pipeline for a Single Stage

        Args:
            task: The graph task to execute
            trace_config: Trace configuration for the task
            job: The job associated with the task
            agent_graph: The agent graph associated with the task
            enable_notifications: Whether to enable notifications
            **kwargs: Additional parameters (for compatibility with base class)

        Returns:
            The updated graph task after execution
        """
        try:
            agent_setup_session = await setup_agent(
                agent_setup=task,
                streaming_handlers=[self.graph_streaming_handler],
                trace_config=trace_config,
                on_exit=(
                    partial(self.update_task_state, job=job)
                    if enable_notifications
                    else None
                ),
            )

            return agent_setup_session
        except Exception as e:
            logger.error(f"Task Manager || Error Running Agent Setup Session: {e}")
            raise e

    async def handle_task_failure(self, task: AgentSetupSession, job: Job) -> None:
        """Handle task execution failure."""
        logger.info("Handling Task Failure for Agent Setup...")
        # Set Task Status to Failed
        task.status = AgentSetupStatus.FAILED

        # Send Beam Platform Notifications for Failed Task State Updates
        await self.update_task_state(task=task, job=job)

        # Publish Updated Job to Redis Queue
        # NOTE: FAILED Status causes Job to be flagged for Termination in queue_task
        job.endJob = True
        await self.queue_task(task=task, job=job)

    async def update_task_state(self, task: AgentSetupSession, job: Job) -> None:
        """Update the Agent Setup State in Beam API."""
        # NOTE: Update Agent Setup States on Beam API
        logger.info("Updating Agent Setup Session on Beam API...")
        logger.info(f"Agent Setup Status: {task.task_status}")
        logger.info("Dispatching Agent Setup Update Job for Beam API")

        #  Update Job
        update_job = Job(
            target="beam-api",
            path="agent-setup-updates",
            data={
                "task": task.model_dump(),
            },
        )

        # Publish to Job Channel with Beam API Target
        await self.publish_job(job=update_job, clear_from_cache=False)

    async def graph_streaming_handler(chunk: Dict[str, Any]):
        logger.debug("Processing Graph Streaming Chunk....\n****************\n")

        logger.debug(chunk)

        logger.debug("\n****************\nDone Processing Graph Streaming Chunk....")

    async def run_until_complete(
        self,
        task: AgentSetupSession,
        trace_config: TraceConfig,
        enable_notifications: bool = False,
        **kwargs,
    ) -> AgentSetupSession:
        """Runs Agent Setup until it is completed or hits a terminal state"""
        while task.task_status not in TERMINAL_TASK_STATES:
            try:
                agent_setup_session = await self.run_once(
                    task=task,
                    trace_config=trace_config,
                    enable_notifications=enable_notifications,
                )
            except Exception as e:
                logger.error(f"Error Running Agent Setup Session: {e}")
                raise

        return agent_setup_session
