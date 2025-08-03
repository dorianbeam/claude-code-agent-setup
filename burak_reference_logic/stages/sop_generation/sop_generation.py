import logging

from beam_ai_core.executor.core import execute_step
from beam_ai_core.executor.pydantic_utils import get_output_format
from beam_ai_core.llm.llms import LLM, LLMConfig
from beam_ai_core.tracing.langfuse import TraceConfig

from app.lib.modules.agents.agent.agent import Agent
from app.lib.modules.agents.agent_setup.stages.sop_generation.sop_generation_prompts import (
    sop_generation_prompt,
)
from app.lib.modules.agents.agent_setup.stages.sop_generation.sop_generation_pydantic import (
    GeneratedSOP,
)
from app.lib.modules.memory_v2.task_memory import AgentTaskMemory

logger = logging.getLogger("app")


async def generate_sop(
    agent: Agent,
    process_details: str,
    agent_memory: AgentTaskMemory,
    trace_config: TraceConfig,
) -> str:

    # Set the Prompt Slug For Langfuse
    trace_config.prompt_slug = "SOPGeneration/v1"

    try:
        # NOTE: Grab File Data If needed Here... + Streaming Somehow

        generated_sop = await execute_step(
            template=sop_generation_prompt,
            input_data={
                "agent_details": str(agent),
                "process_details": process_details,
                "output_format": get_output_format(GeneratedSOP),
            },
            llm_config=LLMConfig(force_select_model=LLM.GPT40.value),
            response_type=GeneratedSOP,
            trace_config=trace_config,
        )

        return generated_sop.standard_operating_procedure

    except Exception as sop_generation_exc:
        logger.error(f"Failed to Generate Graph: {sop_generation_exc}")
        raise
