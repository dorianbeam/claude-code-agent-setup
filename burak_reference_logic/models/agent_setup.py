from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Literal, Optional

from beam_ai_core.tracing.langfuse import TraceConfig
from pydantic import BaseModel, ConfigDict, Field

from app.lib.modules.agents.agent.agent import Agent
from app.lib.modules.graphs.agent_graph.graph_creation.strategies.multi_node.generate_graph_pydantic import (
    GeneratedGraph,
)
from app.lib.modules.graphs.agent_graph.models.agent_graph import AgentGraph
from app.lib.modules.memory_v2.task_memory import AgentTaskMemory


class AgentSetupStatus(Enum):
    QUEUED = "QUEUED"
    IN_PROGRESS = "IN_PROGRESS"
    USER_INPUT_REQUIRED = "USER_INPUT_REQUIRED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AgentSetupStage(Enum):
    SOP_GENERATION = "SOP_GENERATION"
    GRAPH_GENERATION = "GRAPH_GENERATION"
    TOOL_MATCHING = "TOOL_MATCHING"
    TOOL_GENERATION = "TOOL_GENERATION"
    CONNECT_INTEGRATIONS = "CONNECT_INTEGRATIONS"


class AgentSetupFileUpload(BaseModel):
    # URL or Name of the File
    file_name: str
    file_type: Literal["FILE", "URL"]
    file_status: Literal["UPLOADED", "FAILED"]


class AgentSetupStageMetadata(BaseModel):
    stage: AgentSetupStage
    timestamp: str
    success: bool
    output: str


class AgentSetupState(BaseModel):
    next: AgentSetupStage
    stages: List[AgentSetupStageMetadata] = Field(default_factory=list)


class AgentGraphTool(BaseModel):
    node_id: str
    # Tool Name
    tool_name: str
    # Tool Description
    tool_description: str
    # Short Description
    short_description: Optional[str] = None
    # Tool Type
    tool_type: Literal["integration", "prompt"]
    # Action Type
    action_type: str

    # Generated Prompt, for Custom GPT Tools
    prompt: Optional[str] = None

    # Tool Parameters
    input_parameters: List[Dict[str, Any]] = Field(default_factory=list)
    # Structured Outputs for GPT Tools
    output_parameters: Optional[List[Dict[str, Any]]] = Field(default_factory=list)

    # Integration Name for Beam/Custom Integration type tools. None for GPT.
    integration_name: Optional[str] = None


class AgentSetupSession(BaseModel):
    id: str
    user_id: str
    thread_id: str
    agent: Agent
    # File Uploads
    file_uploads: List[AgentSetupFileUpload] = Field(default_factory=list)

    # Provided Process Details
    process_instructions: Optional[str] = None
    # Generated Process Details
    agent_sop: Optional[str] = None
    # Generated Agent Graph
    generated_graph: Optional[GeneratedGraph] = None
    agent_graph: Optional[AgentGraph] = None

    # Selected Tools by Node
    integration_tools: List[AgentGraphTool] = Field(default_factory=list)
    custom_tools: List[AgentGraphTool] = Field(default_factory=list)

    # Current Status
    status: AgentSetupStatus
    # Setup Stages
    setup_state: Optional[AgentSetupState] = None

    start_time: Optional[str] = None
    end_time: Optional[str] = None


class AgentGraphCreationState(BaseModel):
    agent_setup_session: AgentSetupSession
    agent_memory: AgentTaskMemory | None = None
    streaming_handlers: List[Callable[[dict], Awaitable[None]]] = Field(
        default_factory=list
    )
    trace_config: TraceConfig

    # Allow AgentMemory / TraceConfig type to be Non-Pydantic
    model_config = ConfigDict(arbitrary_types_allowed=True)
