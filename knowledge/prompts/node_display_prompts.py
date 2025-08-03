"""
Node Display and Visualization Prompts

This module contains natural language guidance for determining how to visually display 
different types of nodes in agent graph workflows. The explanations here help decide
which node type to use based on step characteristics and how to style them appropriately.
"""

NODE_TYPE_SELECTION_GUIDANCE = """
# Node Type Selection Guide

When analyzing SOP steps to determine the appropriate node type, consider these characteristics:

## Trigger Nodes
Use 'trigger' node type when:
- The step represents the start of the entire process
- It's an external event that initiates the workflow (email received, timer, webhook)
- It's the first step that contains incoming data or user input
- The step description mentions "when", "upon receiving", "at scheduled time"

Visual representation: Stadium shape that clearly indicates this is an entry point
Display with distinct styling to highlight it's the workflow starting point

## Process Nodes  
Use 'process' node type when:
- The step performs standard data processing or transformation
- It's a straightforward operational step without complex decision-making
- The step involves basic data manipulation, formatting, or routing
- It's a linear workflow step that always proceeds to the next step

Visual representation: Clean rectangle that indicates standard processing
Use neutral colors to show it's a standard workflow component

## Decision Nodes
Use 'decision' node type when:
- The step has multiple possible outcomes or branches
- It involves conditional logic ("if this, then that")
- The step description mentions comparing, evaluating, or choosing between options
- Multiple "Branch" conditions are listed in the SOP step
- The step determines which path the workflow should take next

Visual representation: Diamond/rhombus shape that clearly shows branching
Use distinct colors to highlight decision points in the workflow

## Tool Nodes
Use 'tool' node type when:
- The step involves calling a specific API or external system
- It's an integration action that performs CRUD operations
- The step mentions specific service names (Salesforce, HubSpot, etc.)
- It involves authentication or API calls to external platforms
- The action is standardized and repeatable with defined inputs/outputs

Visual representation: Subroutine shape that indicates external system interaction
Style with integration-specific colors or icons when possible

## AI Agent Nodes
Use 'ai_agent' node type when:
- The step requires LLM reasoning or natural language processing
- It involves content generation, decision-making, or data extraction
- The tool category is "Prompt" with action types like generation/decision/extraction
- The step needs dynamic reasoning based on context
- It involves understanding, analyzing, or creating human-readable content

Visual representation: Circular shape that indicates intelligent processing
Use colors that suggest AI/automation capabilities

## Human Loop Nodes
Use 'human_loop' node type when:
- The step requires human intervention or approval
- Manual input or verification is needed
- The step mentions user consent, approval, or manual review
- An escalation to human agents is required
- The workflow needs to pause for human decision-making

Visual representation: Double circle that emphasizes human involvement
Use colors that clearly distinguish manual steps from automated ones

## Merge Nodes
Use 'merge' node type when:
- Multiple workflow paths converge into a single step
- The step combines data or results from parallel processes
- Different branches of the workflow join back together
- The step aggregates or consolidates information from multiple sources

Visual representation: Asymmetric shape that shows convergence
Position to clearly show multiple inputs converging

## End Nodes
Use 'end' node type when:
- The step represents process completion or termination
- It's a final action that concludes the workflow
- The step has "Exit Conditions" defined
- No further steps follow after this point
- The workflow reaches a natural conclusion

Visual representation: Stadium shape with flat end indicating termination
Style to clearly show this is a workflow endpoint

# Visual Styling Guidelines

## Performance Indicators
- Add ⚡ symbol for critical performance steps
- Add ⭐ symbol for high-priority steps  
- Use consistent symbol placement and sizing

## Error Handling Indicators
- Add 🛡️ symbol for steps with error handling capabilities
- Show error flow paths with different line styles
- Use consistent error indication across all node types

## Monitoring Indicators  
- Add 📊 symbol for steps that include monitoring or tracking
- Indicate data collection points clearly
- Show monitoring flow separately from main workflow

## Color Coding Strategy
- Use consistent color families for each node type
- Ensure sufficient contrast for accessibility
- Apply colors that intuitively match the node's function
- Maintain visual hierarchy through color intensity

## Node Labeling
- Keep labels concise but descriptive
- Include step numbers for workflow clarity
- Show key parameters or conditions when space permits
- Use consistent text formatting and sizing

# When to Use Each Display Element

## Shape Selection Logic
The shape should immediately communicate the node's function:
- Rounded shapes (stadium, circle) for start/end or intelligent processing
- Angular shapes (rectangle, diamond) for standard processing or decisions  
- Specialized shapes (subroutine, asymmetric) for specific functions

## Connection Styling
- Use solid lines for guaranteed transitions
- Use dashed lines for conditional paths
- Use dotted lines for error or exception flows
- Label connections with conditions when necessary

## Layout Considerations
- Arrange nodes to show logical flow from left to right or top to bottom
- Group related nodes visually
- Ensure adequate spacing for readability
- Minimize line crossings for clarity

This guidance ensures consistent and intuitive visual representation of agent workflows
that clearly communicates the process flow and decision points to both technical and 
non-technical stakeholders.
"""

# Additional helper constants for display logic
NODE_SHAPES = {
    "trigger": ("([", "])"),      # Stadium shape for triggers
    "process": ("[", "]"),        # Rectangle for processes  
    "decision": ("{", "}"),       # Rhombus for decisions
    "tool": ("[[", "]]"),         # Subroutine shape for tools
    "ai_agent": ("((", "))"),     # Circle for AI agents
    "human_loop": ("(((", ")))"), # Double circle for human interaction
    "merge": (">", "]"),          # Asymmetric shape for merge
    "end": ("([", "])")           # Stadium with flat end
}

PERFORMANCE_INDICATORS = {
    "critical": "⚡",
    "high": "⭐", 
    "normal": "",
    "low": ""
}

STATUS_INDICATORS = {
    "error_handling": "🛡️",
    "monitoring": "📊",
    "user_input": "👤",
    "escalation": "🚨"
}

COLOR_SCHEMES = {
    "trigger": "#e1f5fe",      # Light blue - entry point
    "process": "#f3e5f5",      # Light purple - standard processing
    "decision": "#fff3e0",     # Light orange - decision point
    "tool": "#e8f5e8",         # Light green - external integration
    "ai_agent": "#fce4ec",     # Light pink - AI processing
    "human_loop": "#fff8e1",   # Light yellow - human intervention
    "merge": "#f1f8e9",        # Light lime - convergence
    "end": "#ffebee"           # Light red - termination
}