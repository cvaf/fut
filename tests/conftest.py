import pytest

from .constants import ATTRIBUTES, PRICES


@pytest.fixture(scope="session")
def expected_attributes(request):
    return ATTRIBUTES.get(request.param)


@pytest.fixture(scope="session")
def expected_prices(request):
    return PRICES.get(request.param)