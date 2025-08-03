# Agent Graph Generation System

This system creates multi-agent workflows from business process descriptions using a 5-step pipeline that produces the same output as the original `agent_setup_original_logic` implementation.

## Workflow Steps

### Step 0: Preparation
**Purpose**: Create organized folder structure for agent graph outputs

**Actions**:
1. Create main folder for the agent graph: `agent_graph_{timestamp}` 
2. Create `nodes/` subfolder to store individual node files

**Output**: Folder structure ready for subsequent steps

### Step 1: SOP Generation
**Purpose**: Convert process description into Standard Operating Procedure with integration availability assessment

**Input**: 
- Agent details and capabilities
- Business process description
- Available integration tools in `knowledge/tools/` folder

**Actions**:
1. Use SOP generation prompt from `knowledge/prompts/sop_generation_prompts.py`
2. Generate expert reasoning (minimum 25 sentences)
3. **Review existing integrations**: Scan `knowledge/tools/` folder to identify available integration tools
4. **Assess integration gaps**: Compare required integrations from process description against available tools
5. **Escalate missing integrations**: If critical integrations are unavailable, trigger human escalation workflow
6. Create structured SOP with all required elements, marking integration availability status

**Output**: Save `sop.md` in main agent graph folder

**Integration Review Process**:
- **Available Integrations**: Mark steps that can use existing tools from `knowledge/tools/`
- **Missing Integrations**: Flag steps requiring unavailable integrations
- **Escalation Trigger**: When critical integrations are missing, escalate to human for:
  - Tool procurement decisions
  - Alternative workflow paths
  - Manual process approval
- **Fallback Strategies**: Document alternative approaches when integrations are unavailable

**SOP Structure Requirements**:
- Trigger Events
- Step Number, Objective, Description
- Required Context 
- Tool Category (Integration/Prompt)
- Action Type (read/create/update/delete for Integration, generation/decision/extraction/verification for Prompt)
- Branches with conditions
- Exit Conditions (optional)

### Step 2: Graph Concept
**Purpose**: Define node types and high-level node information from SOP

**Input**: Generated SOP from Step 1

**Actions**:
1. Parse SOP steps
2. Assign node types based on step characteristics:
   - `trigger` - Entry points/trigger events
   - `process` - Standard integration actions  
   - `decision` - Branching logic/verification steps
   - `tool` - Specific tool execution
   - `ai_agent` - AI-powered operations
   - `human_loop` - Human interaction points
   - `merge` - Convergence pointsp
   - `end` - Terminal steps
3. Create high-level node definitions

**Output**: Save `graph_concept.json` with node types and basic info

### Step 3: Tool Matching (Integration Actions Only)
**Purpose**: Match integration actions to available tools

**Input**: 
- Graph concept from Step 2
- Available integration schemas in `knowledge/tools/` folder

**Actions**:
1. Identify nodes with `tool_category: "integration"`
2. Look up matching tools in `knowledge/tools/` folder based on action_type
3. For each match:
   - Copy integration action schema
   - Save as individual node file in `nodes/` folder
   - Include node_id, tool_name, integration_name, parameters

**Output**: Integration node files in `nodes/` folder

**Integration Tool Format**:
Based on `standard_beam_tool_sample.json` schema, each integration node contains:
```json
{
  "toolConfiguration": {
    "originalTool": {
      "toolFunctionName": "integration_action_name",
      "toolName": "Integration Tool Display Name",
      "type": "beam_tool",
      "integrationId": "integration-uuid",
      "meta": {
        "tool_name": "Integration Tool Display Name",
        "function_name": "integration_action_name",
        "requires_consent": false,
        "action_type": "read|create|update|delete",
        "integration_name": "service_name",
        "integration_provider_details": {
          "request": {
            "endpoint": "/api/v1/endpoint",
            "method": "GET|POST|PUT|DELETE",
            "query": ["param1", "param2"],
            "body": {"field": "type"}
          },
          "response": {
            "data": "object",
            "status": "string"
          }
        },
        "integration_provider_auth": "api_key|oauth2|bearer",
        "apiKeyType": "header|query",
        "parameter": "auth_parameter_name"
      },
      "inputParams": [
        {
          "paramName": "input_field",
          "fillType": "ai_fill|user_input|static",
          "question": "What data should be processed?",
          "paramDescription": "Description of input parameter",
          "required": true,
          "dataType": "string|object|array"
        }
      ],
      "outputParams": [
        {
          "paramName": "result_field", 
          "paramDescription": "Description of output parameter",
          "id": "output_param_id"
        }
      ]
    },
    "agentId": "agent_uuid",
    "id": "node_configuration_uuid"
  },
  "nodes": ["connected_node_ids"],
  "id": "node_uuid"
}
```

**Key Integration Fields**:
- `toolConfiguration.originalTool` - Complete beam_tool definition
- `meta.integration_provider_details` - API endpoint and authentication specs
- `inputParams`/`outputParams` - Parameter schemas with validation
- `integration_provider_auth` - Authentication method (api_key, oauth2, bearer)
- Authentication parameters and API configuration details

### Step 4: Prompt Generation
**Purpose**: Generate prompts for all non-integration nodes

**Input**: 
- Graph concept from Step 2
- Existing integration nodes from Step 3

**Actions**:
1. Identify nodes with `tool_category: "prompt"` 
2. For each prompt node:
   - Generate specialized LLM prompt based on action_type
   - Define input/output parameters
   - Create structured prompt definitions
   - Save as individual node file in `nodes/` folder

**Output**: Prompt node files in `nodes/` folder

**Prompt Tool Format**:
Based on `generic_custom_tool_sample.json` schema, each prompt node contains:
```json
{
  "toolConfiguration": {
    "originalTool": {
      "toolFunctionName": "custom_prompt_processor",
      "toolName": "AI Processing Tool Name",
      "type": "custom_tool",
      "integrationId": null,
      "meta": null,
      "prompt": "Detailed LLM prompt with specific instructions for the action_type:\n- For 'generation': Create content based on provided context\n- For 'decision': Analyze data and make reasoned decisions\n- For 'extraction': Extract specific information from documents\n- For 'verification': Validate and check data accuracy",
      "inputParams": [
        {
          "paramName": "input_data",
          "fillType": "ai_fill|user_input|static",
          "question": "What data should be processed?",
          "paramDescription": "Input data for AI processing",
          "required": true,
          "dataType": "string|object|array"
        }
      ],
      "outputParams": [
        {
          "paramName": "processed_result",
          "paramDescription": "Result of AI processing operation",
          "id": "result_param_id"
        }
      ],
      "preferredModel": "gpt-4|gpt-3.5-turbo",
      "description": "Custom tool for AI-powered processing operations"
    },
    "agentId": "agent_uuid", 
    "id": "node_configuration_uuid"
  },
  "nodes": ["connected_node_ids"],
  "id": "node_uuid",
  "customConfiguration": {
    "action_type": "generation|decision|extraction|verification",
    "max_tokens": 2000,
    "temperature": 0.7,
    "timeout_seconds": 30,
    "retry_attempts": 3
  },
  "executionContext": {
    "environment": "production",
    "resource_limits": {
      "memory": "512MB",
      "execution_time": "30s"
    }
  }
}
```

**Key Prompt Tool Fields**:
- `toolConfiguration.originalTool.prompt` - Complete LLM prompt with instructions
- `customConfiguration.action_type` - Type of AI operation (generation/decision/extraction/verification) 
- `preferredModel` - LLM model selection (gpt-4, gpt-3.5-turbo)
- `executionContext` - Resource limits and environment configuration
- Model parameters (max_tokens, temperature) for fine-tuned responses

### Step 5: Graph Assembly
**Purpose**: Assemble complete agent graph from all components

**Input**:
- Graph concept from Step 2
- All node files from `nodes/` folder
- Original SOP for edge/branching logic

**Actions**:
1. Collect all node definitions
2. Generate edges based on SOP branching logic
3. Create complete graph structure with nodes, edges, and metadata
4. Validate graph completeness and correctness

**Output**: Save `agent_graph.json` in main folder

**Final Graph Assembly Process**:
The final agent graph is assembled programmatically by reading all individual node files from the `nodes/` folder. The resulting structure is complex and extensive (typically thousands of lines) containing:

- **Complete tool definitions** with full metadata, authentication, and parameters
- **Rich node configurations** including toolConfiguration, originalTool, connections
- **Comprehensive prompt definitions** for AI-powered nodes
- **Integration specifications** with API endpoints and parameter schemas
- **Agent metadata** and workflow orchestration details

**Assembly Logic**:
1. Scan `nodes/` folder for all `.json` files
2. Parse each node file and extract complete tool configurations
3. Build full `graph.nodes[]` array with toolConfiguration objects
4. Preserve all tool metadata, prompts, parameters, and integration details
5. Generate edges from SOP branching logic
6. Combine into complete agent graph matching production schema

**Structure Complexity**:
- Real agent graphs contain 100+ nodes with full configurations
- 30+ tools with complete beam_tool and custom_tool definitions
- Extensive nested objects for authentication, parameters, and integrations
- Full prompt definitions with context and reasoning logic

**For Schema Reference**: See `knowledge/examples/`:
- `agent_graph_minimal_schema.json` - High-level structure overview
- `agent_graph_nodes_schema.json` - Complete node configuration schemas  
- `agent_graph_tools_schema.json` - Full tool definition schemas
- `agent_graph_consolidated_overview.json` - Comprehensive analysis

**Note**: The final `agent_graph.json` file will be extensive due to complete tool definitions, prompts, and metadata - typically 10,000+ lines for production workflows.

## Node Types (Matching Original Implementation)

- `trigger` - Process entry points (stadium shape)
- `process` - Standard workflow steps (rectangle)  
- `decision` - Branching logic (rhombus)
- `tool` - Tool execution (subroutine shape)
- `ai_agent` - AI operations (circle)
- `human_loop` - Human interaction (double circle)
- `merge` - Convergence points (asymmetric)
- `end` - Terminal nodes (stadium with flat end)

## Tool Categories & Action Types

### Integration Actions
- `read` - Fetch/retrieve data
- `create` - Create new records
- `update` - Modify existing data  
- `delete` - Remove data

### Prompt Actions
- `generation` - Content generation
- `decision` - Decision making/reasoning
- `extraction` - Data extraction from documents
- `verification` - Data validation/checking

## Human Escalation Process

### Escalation Triggers
The system escalates to human intervention when:

1. **Missing Critical Integrations**: Required integrations for core business processes are unavailable
2. **Tool Gaps**: No suitable tools exist for essential SOP steps  
3. **Authentication Issues**: Integration tools require credentials or permissions not available
4. **Compliance Requirements**: Business processes require human approval or oversight
5. **Complex Decision Points**: Logic too complex for automated decision-making

### Escalation Workflow

**Step 1: Gap Detection**
- During SOP generation, identify missing integrations by comparing required vs. available tools
- Flag steps that cannot be automated with current tool inventory
- Assess business impact: Critical, High, Medium, Low

**Step 2: Escalation Notification**
- Generate human-readable summary of missing tools and their business impact
- Include suggested alternatives or workarounds if available
- Provide timeline implications for tool procurement vs. manual processes

**Step 3: Human Decision Points**
- **Proceed with gaps**: Accept manual processes for missing integrations
- **Acquire tools**: Pause workflow generation pending tool procurement
- **Alternative workflows**: Redesign process to use available tools
- **Hybrid approach**: Automate where possible, manual for gaps

**Step 4: Documentation**
- Record decisions and rationale for future reference
- Update process documentation with approved manual steps or tool alternatives
- Create follow-up tasks for tool procurement if applicable

### Escalation Outputs
- **Decision Log**: Record of human decisions and reasoning
- **Modified SOP**: Updated process reflecting human-approved approach
- **Tool Acquisition Plan**: List of tools to procure with business justification
- **Manual Process Documentation**: Detailed steps for human-performed tasks

## File Organization

After completion, the folder structure will be:
```
agent_graph_{timestamp}/
├── sop.md                    # Step 1 output
├── graph_concept.json        # Step 2 output  
├── agent_graph.json         # Step 5 final output
└── nodes/                   # Individual node files
    ├── node_step1.json      # Integration tools from Step 3
    ├── node_step2.json      # Prompt tools from Step 4
    └── ...
```

## Output Compatibility

This system produces identical output format to the original `agent_setup_original_logic`:
- Same node types and action types
- Compatible AgentSetupSession structure
- Matching GeneratedGraph schema
- Identical tool definitions
- Same stage progression logic