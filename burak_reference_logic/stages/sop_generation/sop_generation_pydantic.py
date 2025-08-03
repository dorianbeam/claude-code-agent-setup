from pydantic import BaseModel, Field


class GeneratedSOP(BaseModel):
    expert_reasoning: str = Field(
        description="Detailed Train-of-Thought from the Expert on how the Standard Operating Procedure is assembled. Minimum 25 Sentences."
    )
    standard_operating_procedure: str = Field(
        description="THe SOP for the Agent containing all Process handling details."
    )
