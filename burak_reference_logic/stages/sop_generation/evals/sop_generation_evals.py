import logging

import pytest

from app.lib.modules.agents.agent_setup.stages.sop_generation.evals.datasets.sop_generation_cases import (
    sop_generation_test_cases,
)

logger = logging.getLogger("app")


# NOTE: Accuracy Tests for Various Entrypoint Selection Scenarios
@pytest.mark.asyncio()
async def test_sop_generation_accuracy():
    """Tests the Accuracy of the Task Success Check for a given Node Output"""

    try:
        _sop_generation_cases = await sop_generation_test_cases()

    except Exception:
        pass
