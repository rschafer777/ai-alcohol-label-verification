from __future__ import annotations

import pytest
from labelverify.domain.grouping import _brands_are_compatible


@pytest.mark.parametrize(
    ("values", "compatible"),
    [
        ({"HARBOR LIGHTSE", "HARBOR LIGHTS"}, True),
        ({"VALLE", "VALLE DI PIETRA"}, True),
        ({"JACK DANIEL'S", "JACK DANIEL DISTILLERY"}, True),
        ({"SILVER OAK", "SILVER SPRINGS BREWING"}, False),
        ({"OLD FORESTER", "FORESTER HILL WINERY"}, False),
        ({"GRAND MARNIER", "GRAND TETON BREWING"}, False),
    ],
)
def test_brand_reads_are_compatible_only_when_they_describe_one_name(
    values: set[str], compatible: bool
) -> None:
    assert _brands_are_compatible(values) is compatible
