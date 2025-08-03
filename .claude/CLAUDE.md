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
**Purpose**: Convert process description into Standard Operating Procedure

**Input**: 
- Agent details and capabilities
- Business process descriptionfrom exis

**Actions**:
1. Use SOP generation prompt from `knowledge/prompts/sop_generation_prompts.py`
2. Generate expert reasoning (minimum 25 sentences)
3. Create structured SOP with all required elements

**Output**: Save `sop.md` in main agent graph folder

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
- Available integration schemas in `tools/` folder

**Actions**:
1. Identify nodes with `tool_category: "integration"`
2. Look up matching tools in `tools/` folder based on action_type
3. For each match:
   - Copy integration action schema
   - Save as individual node file in `nodes/` folder
   - Include node_id, tool_name, integration_name, parameters

**Output**: Integration node files in `nodes/` folder

**Integration Tool Format**:
```json
{
  "node_id": "step_id",
  "tool_name": "tool_name", 
  "tool_description": "description",
  "tool_type": "integration",
  "action_type": "read|create|update|delete",
  "integration_name": "service_name",
  "input_parameters": [],
  "output_parameters": []
}
```

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
```json
{
  "node_id": "step_id",
  "tool_name": "tool_name",
  "tool_description": "description", 
  "tool_type": "prompt",
  "action_type": "generation|decision|extraction|verification",
  "prompt": "LLM prompt text with instructions",
  "input_parameters": [],
  "output_parameters": []
}
```

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