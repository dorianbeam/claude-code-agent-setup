import logging
import os
from typing import List

from pydantic import BaseModel, Field

from app.lib.modules.graphs.graph_task_executor.modules.test_case_generator.test_case_generator import (
    generate_test_cases,
)

logger = logging.getLogger("app")


class SopGenerationTestCase(BaseModel):
    agent_name: str = Field(description="Name of the AI Agent")
    agent_description: str = Field(
        description="Description about the AI Agent, responsibilities, capabilities and and use cases Agent can process"
    )
    process_description: str = Field(
        description="Comprehensive Description for a Business Process Description, on how a company/organization operates"
    )


async def sop_generation_test_cases() -> List[SopGenerationTestCase]:
    baseline_llm_cases = [
        SopGenerationTestCase(
            agent_name="Invoice Processing Agent",
            agent_description="""The Invoice Processing Agent is an AI-powered solution that automates 
        the entire accounts payable workflow from invoice receipt to payment approval. 
        It accurately extracts data from invoices, validates against purchase orders, 
        routes for approval, and schedules payments while maintaining compliance and 
        reducing processing time and errors by up to 80%. This agent seamlessly integrates 
        with existing ERP systems to provide real-time visibility into invoice status and payment forecasting.""",
            process_description="""
## Invoice Processing Workflow Manual for Employees
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
""",
        ),
    ]

    TESTING_CONTEXT = """You are testing an LLM based transformation feature where the main goal is to
    map a human driven process from a company or an organization, to a Standard Operating Procedure
    document explaining each individual step and are composed of automated actions performed by an 
    AI Agent. To maximize accuracy for the Transformation, you must come up with different examples of other
    business use case scenarios. Remember to avoid very similar or redundant Process Descriptions"""

    # Generate the Additional Test Cases via LLM and Dump as File
    # Get the Current OS File Path + ../generated_test_cases.json
    current_dir = os.path.dirname(__file__)
    generated_cases_file_path = os.path.join(current_dir, "generated_test_cases.json")

    logger.warning(f"Generated Test Cases File Path: {generated_cases_file_path}")

    generated_cases = await generate_test_cases(
        examples=baseline_llm_cases,
        output_path=generated_cases_file_path,
        testing_context=TESTING_CONTEXT,
        n=8,
    )

    logger.warning(f"Generated Test Cases: {generated_cases}")

    test_cases = baseline_llm_cases + generated_cases

    return test_cases
