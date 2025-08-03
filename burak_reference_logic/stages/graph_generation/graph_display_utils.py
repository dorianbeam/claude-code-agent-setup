"""
Enhanced Graph Display Utilities

This module provides advanced visualization capabilities for workflow graphs,
including improved Mermaid diagram generation with better styling and features.
"""

import base64
import json
from typing import Dict, List, Any, Tuple, Optional
import logging

logger = logging.getLogger("app")


def generate_mermaid_live_link(mermaid_graph: str) -> str:
    """
    Generates URL for mermaid.live with enhanced styling and features.
    
    Args:
        mermaid_graph: The Mermaid diagram definition
        
    Returns:
        URL for mermaid.live editor
    """
    _graph_data = {
        "code": mermaid_graph, 
        "mermaid": {
            "theme": "default",
            "themeVariables": {
                "primaryColor": "#4f46e5",
                "primaryTextColor": "#ffffff",
                "primaryBorderColor": "#3730a3",
                "lineColor": "#6b7280",
                "sectionBkgColor": "#f3f4f6",
                "altSectionBkgColor": "#e5e7eb",
                "gridColor": "#d1d5db",
                "tertiaryColor": "#fef3c7"
            }
        }
    }
    data_json = json.dumps(_graph_data, separators=(",", ":")).encode("utf-8")

    # Base64 link
    base64_encoded = base64.b64encode(data_json).decode()
    base64_url = f"https://mermaid.live/edit#base64:{base64_encoded}"

    return base64_url


def generate_enhanced_mermaid_graph(graph: Dict[str, Any]) -> str:
    """
    Generate an enhanced Mermaid diagram from a workflow graph with improved styling.
    
    Args:
        graph: The workflow graph dictionary
        
    Returns:
        Mermaid diagram definition string
    """
    try:
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        error_flows = graph.get("error_flows", [])
        
        # Start the diagram
        mermaid_lines = [
            "graph TD",
            "    %% Enhanced Workflow Graph",
            f"    %% Graph: {graph.get('name', 'Unnamed')}",
            f"    %% Version: {graph.get('version', '1.0.0')}",
            ""
        ]
        
        # Add nodes with enhanced styling
        node_definitions = _generate_node_definitions(nodes)
        mermaid_lines.extend(node_definitions)
        mermaid_lines.append("")
        
        # Add edges with conditions
        edge_definitions = _generate_edge_definitions(edges)
        mermaid_lines.extend(edge_definitions)
        mermaid_lines.append("")
        
        # Add error flows if present
        if error_flows:
            error_flow_definitions = _generate_error_flow_definitions(error_flows, nodes)
            mermaid_lines.extend(error_flow_definitions)
            mermaid_lines.append("")
        
        # Add styling
        styling_definitions = _generate_styling_definitions(nodes)
        mermaid_lines.extend(styling_definitions)
        
        return "\n".join(mermaid_lines)
        
    except Exception as e:
        logger.error(f"Failed to generate enhanced Mermaid graph: {e}")
        return _generate_fallback_mermaid_graph(graph)


def _generate_node_definitions(nodes: List[Dict[str, Any]]) -> List[str]:
    """Generate Mermaid node definitions with appropriate shapes and labels."""
    definitions = ["    %% Node Definitions"]
    
    for node in nodes:
        node_id = node.get("id", "unknown")
        node_type = node.get("type", "process")
        node_name = node.get("name", node_id)
        
        # Escape special characters in node names
        safe_name = _escape_mermaid_text(node_name)
        
        # Choose shape based on node type
        shape_start, shape_end = _get_node_shape(node_type)
        
        # Add performance indicators if available
        performance_indicator = ""
        if "performance" in node:
            criticality = node["performance"].get("criticality", "")
            if criticality == "critical":
                performance_indicator = " ⚡"
            elif criticality == "high":
                performance_indicator = " ⭐"
        
        # Add error handling indicator
        error_indicator = ""
        if node.get("error_handling"):
            error_indicator = " 🛡️"
        
        # Add monitoring indicator
        monitoring_indicator = ""
        if node.get("monitoring"):
            monitoring_indicator = " 📊"
        
        full_label = f"{safe_name}{performance_indicator}{error_indicator}{monitoring_indicator}"
        
        definitions.append(f"    {node_id}{shape_start}\"{full_label}\"{shape_end}")
    
    return definitions


def _generate_edge_definitions(edges: List[Dict[str, Any]]) -> List[str]:
    """Generate Mermaid edge definitions with conditions and styling."""
    definitions = ["    %% Edge Definitions"]
    
    for edge in edges:
        from_node = edge.get("from")
        to_node = edge.get("to")
        
        if not from_node or not to_node:
            continue
        
        # Get condition information
        condition = edge.get("condition", {})
        if isinstance(condition, dict):
            condition_type = condition.get("type", "always")
            condition_desc = condition.get("description", "")
        else:
            condition_type = "conditional" if condition else "always"
            condition_desc = str(condition) if condition else ""
        
        # Choose edge style based on condition type
        if condition_type == "error":
            edge_style = "-.->|❌|"
        elif condition_type == "conditional":
            edge_style = "-->|✓|" if condition_desc else "-->"
        else:
            edge_style = "-->"
        
        # Add condition label if present
        if condition_desc and condition_type != "error":
            safe_condition = _escape_mermaid_text(condition_desc[:30])  # Limit length
            definitions.append(f"    {from_node} {edge_style} {to_node}")
            definitions.append(f"    {from_node} -.->|{safe_condition}| {to_node}")
        else:
            definitions.append(f"    {from_node} {edge_style} {to_node}")
    
    return definitions


def _generate_error_flow_definitions(error_flows: List[Dict[str, Any]], nodes: List[Dict[str, Any]]) -> List[str]:
    """Generate Mermaid definitions for error flows."""
    definitions = ["    %% Error Flow Definitions"]
    
    # Create a lookup for node types
    node_types = {node.get("id"): node.get("type") for node in nodes}
    
    for i, error_flow in enumerate(error_flows):
        trigger = error_flow.get("trigger", {})
        recovery_strategy = error_flow.get("recovery_strategy", {})
        
        source_nodes = trigger.get("source_nodes", [])
        recovery_path = recovery_strategy.get("path", [])
        
        # Create error handler node
        error_handler_id = f"error_handler_{i}"
        error_type = trigger.get("type", "error")
        
        definitions.append(f"    {error_handler_id}{{\"🚨 {error_type.replace('_', ' ').title()}\"}}")
        
        # Connect source nodes to error handler
        for source_node in source_nodes:
            if source_node in node_types:
                definitions.append(f"    {source_node} -.->|error| {error_handler_id}")
        
        # Connect error handler to recovery path
        if recovery_path:
            first_recovery_node = recovery_path[0]
            definitions.append(f"    {error_handler_id} -.->|recover| {first_recovery_node}")
    
    return definitions


def _generate_styling_definitions(nodes: List[Dict[str, Any]]) -> List[str]:
    """Generate Mermaid styling definitions for different node types."""
    definitions = ["    %% Styling Definitions"]
    
    # Group nodes by type for styling
    node_types = {}
    for node in nodes:
        node_type = node.get("type", "process")
        node_id = node.get("id")
        
        if node_type not in node_types:
            node_types[node_type] = []
        node_types[node_type].append(node_id)
    
    # Define colors for each node type
    type_colors = {
        "trigger": "fill:#10b981,stroke:#059669,stroke-width:3px,color:#ffffff",
        "process": "fill:#3b82f6,stroke:#1d4ed8,stroke-width:2px,color:#ffffff",
        "decision": "fill:#f59e0b,stroke:#d97706,stroke-width:2px,color:#ffffff",
        "tool": "fill:#8b5cf6,stroke:#7c3aed,stroke-width:2px,color:#ffffff",
        "ai_agent": "fill:#ec4899,stroke:#db2777,stroke-width:2px,color:#ffffff",
        "human_loop": "fill:#06b6d4,stroke:#0891b2,stroke-width:2px,color:#ffffff",
        "merge": "fill:#84cc16,stroke:#65a30d,stroke-width:2px,color:#ffffff",
        "end": "fill:#ef4444,stroke:#dc2626,stroke-width:3px,color:#ffffff"
    }
    
    # Apply styling to nodes
    for node_type, node_ids in node_types.items():
        if node_type in type_colors:
            color_def = type_colors[node_type]
            for node_id in node_ids:
                definitions.append(f"    classDef {node_type}Style {color_def}")
                definitions.append(f"    class {node_id} {node_type}Style")
    
    # Add special styling for critical nodes
    critical_nodes = [
        node.get("id") for node in nodes 
        if node.get("performance", {}).get("criticality") == "critical"
    ]
    
    if critical_nodes:
        definitions.append("    classDef criticalStyle stroke:#dc2626,stroke-width:4px,stroke-dasharray: 5 5")
        for node_id in critical_nodes:
            definitions.append(f"    class {node_id} criticalStyle")
    
    return definitions


def _get_node_shape(node_type: str) -> Tuple[str, str]:
    """Get the appropriate Mermaid shape for a node type."""
    shapes = {
        "trigger": ("([", "])"),      # Stadium shape for triggers
        "process": ("[", "]"),        # Rectangle for processes
        "decision": ("{", "}"),       # Rhombus for decisions
        "tool": ("[[", "]]"),         # Subroutine shape for tools
        "ai_agent": ("((", "))"),     # Circle for AI agents
        "human_loop": ("(((", ")))"), # Double circle for human interaction
        "merge": (">", "]"),          # Asymmetric shape for merge
        "end": ("([", "])")           # Stadium with flat end
    }
    
    return shapes.get(node_type, ("[", "]"))  # Default to rectangle


def _escape_mermaid_text(text: str) -> str:
    """Escape special characters in Mermaid text."""
    if not text:
        return ""
    
    # Replace problematic characters
    text = text.replace('"', "'")
    text = text.replace('\n', ' ')
    text = text.replace('\r', ' ')
    text = text.replace('\t', ' ')
    
    # Limit length to prevent diagram issues
    if len(text) > 50:
        text = text[:47] + "..."
    
    return text


def _generate_fallback_mermaid_graph(graph: Dict[str, Any]) -> str:
    """Generate a simple fallback Mermaid graph if enhanced generation fails."""
    try:
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        
        mermaid_lines = [
            "graph TD",
            "    %% Fallback Workflow Graph",
            ""
        ]
        
        # Simple node definitions
        for node in nodes:
            node_id = node.get("id", "unknown")
            node_name = _escape_mermaid_text(node.get("name", node_id))
            mermaid_lines.append(f"    {node_id}[\"{node_name}\"]")
        
        mermaid_lines.append("")
        
        # Simple edge definitions
        for edge in edges:
            from_node = edge.get("from")
            to_node = edge.get("to")
            if from_node and to_node:
                mermaid_lines.append(f"    {from_node} --> {to_node}")
        
        return "\n".join(mermaid_lines)
        
    except Exception as e:
        logger.error(f"Fallback Mermaid generation failed: {e}")
        return "graph TD\n    A[Error generating diagram]"


def generate_graph_summary(graph: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a summary of the workflow graph for quick understanding.
    
    Args:
        graph: The workflow graph dictionary
        
    Returns:
        Dictionary containing graph summary information
    """
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    error_flows = graph.get("error_flows", [])
    
    # Count nodes by type
    node_type_counts = {}
    for node in nodes:
        node_type = node.get("type", "unknown")
        node_type_counts[node_type] = node_type_counts.get(node_type, 0) + 1
    
    # Calculate complexity metrics
    complexity_metrics = {
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "error_flows": len(error_flows),
        "complexity_ratio": len(edges) / max(len(nodes), 1),
        "node_types": node_type_counts
    }
    
    # Identify entry and exit points
    entry_points = [node.get("id") for node in nodes if node.get("type") == "trigger"]
    exit_points = [node.get("id") for node in nodes if node.get("type") == "end"]
    
    # Calculate graph depth (longest path)
    max_depth = _calculate_graph_depth(nodes, edges)
    
    # Identify critical nodes
    critical_nodes = [
        node.get("id") for node in nodes 
        if node.get("performance", {}).get("criticality") in ["critical", "high"]
    ]
    
    return {
        "graph_info": {
            "id": graph.get("graph_id"),
            "name": graph.get("name"),
            "version": graph.get("version"),
            "description": graph.get("description")
        },
        "complexity": complexity_metrics,
        "structure": {
            "entry_points": entry_points,
            "exit_points": exit_points,
            "max_depth": max_depth,
            "critical_nodes": critical_nodes
        },
        "quality": {
            "has_error_handling": len(error_flows) > 0,
            "has_monitoring": any(node.get("monitoring") for node in nodes),
            "documentation_complete": all(node.get("description") for node in nodes)
        }
    }


def _calculate_graph_depth(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> int:
    """Calculate the maximum depth (longest path) in the graph."""
    try:
        # Build adjacency list
        adjacency = {}
        for node in nodes:
            adjacency[node.get("id")] = []
        
        for edge in edges:
            from_node = edge.get("from")
            to_node = edge.get("to")
            if from_node and to_node and from_node in adjacency:
                adjacency[from_node].append(to_node)
        
        # Find trigger nodes as starting points
        trigger_nodes = [node.get("id") for node in nodes if node.get("type") == "trigger"]
        
        if not trigger_nodes:
            return 0
        
        # DFS to find maximum depth
        max_depth = 0
        visited = set()
        
        def dfs(node, depth):
            nonlocal max_depth
            if node in visited:
                return
            
            visited.add(node)
            max_depth = max(max_depth, depth)
            
            for neighbor in adjacency.get(node, []):
                dfs(neighbor, depth + 1)
            
            visited.remove(node)
        
        for trigger in trigger_nodes:
            dfs(trigger, 1)
        
        return max_depth
        
    except Exception as e:
        logger.error(f"Failed to calculate graph depth: {e}")
        return 0
