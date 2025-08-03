import logging
from uuid import uuid4

import pytest
from beam_ai_core.tracing.langfuse import TraceConfig

from app.lib.modules.agents.agent.agent import Agent, AgentConfig, AgentType
from app.lib.modules.agents.agent_setup.agent_setup import setup_agent
from app.lib.modules.agents.agent_setup.agent_setup_manager import AgentSetupManager
from app.lib.modules.agents.agent_setup.models.agent_setup import (
    AgentSetupSession,
    AgentSetupStatus,
)

logger = logging.getLogger("app")


@pytest.fixture()
def trace_config() -> TraceConfig:
    return TraceConfig(
        id=str(uuid4()),
        name="Agent Setup Flow Tests",
        agent_id="db6fe581-89ac-51dc-9c74-d1dc12eccf3d",
        user_id="86b1269e-46d0-5145-aaf5-8f70c14ed4b8",
        session_id="0e9fe28f-44b5-5bed-a858-a28353ba20b1",
    )


@pytest.fixture()
def agent(trace_config: TraceConfig) -> Agent:
    return Agent(
        id="test-agent",
        vector_db_id="f8f5c136-b4eb-5b3c-8466-e522902ac295",
        type=AgentType.AGENT_OS_AGENT,
        name="Invoice Processing Agent",
        description="""The Invoice Processing Agent is an AI-powered solution that automates 
        the entire accounts payable workflow from invoice receipt to payment approval. 
        It accurately extracts data from invoices, validates against purchase orders, 
        routes for approval, and schedules payments while maintaining compliance and 
        reducing processing time and errors by up to 80%. This agent seamlessly integrates 
        with existing ERP systems to provide real-time visibility into invoice status and payment forecasting.""",
        config=AgentConfig(
            agent_id="test-agent",
            vector_db_id="f8f5c136-b4eb-5b3c-8466-e522902ac295",
            workspace_id="b94a9558-07ab-5d3d-ba24-c318d782df1d",
        ),
    )


@pytest.fixture()
def process_instructions() -> str:
    return """## Invoice Processing Workflow Manual for Employees
### Purpose
This Standard Operating Procedure (SOP) outlines the comprehensive process for handling invoices from receipt through final archival, ensuring accuracy, compliance, and efficiency in our financial operations.

### Scope
Applies to all accounting and finance personnel responsible for invoice management across the organization.

### Responsibilities
- **Accounting Staff**: Primary execution of invoice processing
- **Department Managers**: Approval of invoices within their cost centers
- **Accounts Payable Manager**: Escalation and final resolution of complex cases

### Equipment and Tools
- Computer workstation
- Document scanner
- Enterprise resource planning (ERP) system
- Document management system
- Email client
- Task management platform

### Procedure

#### 1. Invoice Receipt and Initial Processing

**1.1 Invoice Intake**
- Collect invoices from all designated channels:
  - Digital email attachments
  - Scanned physical mail
  - Electronic document portals

**1.2 Document Preparation**
- Ensure all received invoices are:
  - Clearly legible
  - Complete and intact
  - Free from significant damage or obscuration

#### 2. Automated Data Extraction

**2.1 Optical Character Recognition (OCR)**
- Utilize advanced OCR technology to extract critical invoice details:
  - Vendor name
  - Invoice number
  - Total amount
  - Payment terms
  - Due date

**2.2 Data Validation**
- If automated extraction encounters challenges:
  - Flag for manual review
  - Generate task for accounting staff to manually verify

#### 3. Invoice Verification

**3.1 Cross-Referencing**
- Compare extracted invoice data against:
  - Existing purchase orders
  - Receiving documents
  - Vendor master records

**3.2 Discrepancy Management**
- Identify and document any inconsistencies:
  - Pricing variances
  - Quantity mismatches
  - Unauthorized purchases

#### 4. Approval Workflow

**4.1 Approval Determination**
- Assess invoice against organizational guidelines:
  - Amount thresholds
  - Department-specific approval rules
  - Vendor classification

**4.2 Routing Mechanism**
- For invoices requiring approval:
  - Identify appropriate approvers based on hierarchical matrix
  - Electronically route invoice through approval system
  - Track approval status in real-time

#### 5. Payment Processing

**5.1 Payment Scheduling**
- Upon successful approval:
  - Schedule payment according to vendor terms
  - Integrate with accounting system
  - Generate payment records

**5.2 Vendor Communication**
- For rejected invoices:
  - Compose detailed rejection notification
  - Specify exact reasons for non-acceptance
  - Provide clear instructions for resubmission

#### 6. Documentation and Archival

**6.1 Digital Archiving**
- Comprehensive documentation storage:
  - Complete invoice
  - Processing metadata
  - Approval trail
  - Payment confirmation

**6.2 Record Retention**
- Maintain digital records in compliance with:
  - Organizational policies
  - Legal and tax regulations
  - Audit requirements

### Special Circumstances

**Escalation Protocols**
- Invoices in discrepancy status beyond 14 days:
  1. Automatically escalate to Accounts Payable Manager
  2. Initiate comprehensive review
  3. Determine resolution or potential write-off

**Urgent Payment Considerations**
- Manual override permitted for time-sensitive invoices
- Requires explicit authorization from:
  - Department Head
  - Finance Director
  - Chief Financial Officer

### Quality Control

**Regular Audit Checkpoints**
- Monthly reconciliation of:
  - Processing accuracy
  - Approval efficiency
  - Payment timeliness

**Continuous Improvement**
- Quarterly review of invoice processing workflow
- Identify and implement system enhancements

### Appendices
- Approval Matrix
- Vendor Communication Templates
- Escalation Protocol Flowchart

### Version Control
- **Version**: 1.0
- **Effective Date**: [Current Date]
- **Last Reviewed**: [Review Date]
- **Next Review**: [Future Date]

*Note: This procedure is a living document. Suggestions for improvement are welcome and should be submitted to the Finance Operations Manager.*
"""


@pytest.fixture()
def agent_setup_session(
    process_instructions: str, agent: Agent, trace_config: TraceConfig
) -> AgentSetupSession:
    return AgentSetupSession(
        id=trace_config.session_id,
        user_id=trace_config.user_id,
        thread_id=str(uuid4()),
        agent=agent,
        process_instructions=process_instructions,
        status=AgentSetupStatus.QUEUED,
    )


@pytest.mark.asyncio()
async def test_agent_setup_flow(
    agent_setup_session: AgentSetupSession, trace_config: TraceConfig
):
    """Tests the Variance Across Runs to measure the variance in the LLM Responses"""

    # agent_setup_flows = [
    #     setup_agent(
    #         agent_setup=agent_setup_session,
    #         trace_config=trace_config,
    #     )
    #     for _ in range(1)
    # ]

    try:
        # _ = await asyncio.gather(*agent_setup_flows, return_exceptions=True)

        setup_session = await setup_agent(
            agent_setup=agent_setup_session,
            trace_config=trace_config,
            streaming_handlers=[AgentSetupManager.graph_streaming_handler],
        )

        logger.debug(f"Agent Setup Session: {setup_session.model_dump_json(indent=4)}")

        assert setup_session.agent_sop
        assert setup_session.generated_graph
        assert setup_session.custom_tools

    except Exception as e:
        pytest.fail(f"Failed when performing variance tests for Agent Setup: {e}")


# # NOTE: Accuracy Tests for Various Agent Setup Scenarios
# @pytest.mark.asyncio()
# async def test_graph_generation_accuracy(trace_config: TraceConfig):
#     """Tests the Accuracy of the Agent Setup for the Given Test Cases"""
#     accuracy_test_cases = task_detail_generation_test_cases()

#     parameter_extraction_tasks = [
#         generate_task_details(
#             node=test_case.node,
#             task_query=test_case.task_query,
#             trace_config=trace_config,
#         )
#         for test_case in accuracy_test_cases
#     ]

#     try:
#         _ = await asyncio.gather(*parameter_extraction_tasks, return_exceptions=True)

#     except Exception as e:
#         pytest.fail(
#             f"Failed when performing accuracy tests for Agent Setup: {e}"
#         )
