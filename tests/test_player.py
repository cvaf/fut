import pytest

from fut.player import Player


PID = 20000


@pytest.mark.parametrize(
    "expected_attributes, game",
    [(22, 22), (21, 21), (20, 20), (19, 19)],
    indirect=["expected_attributes"],
)
def test_player_download(expected_attributes, game):
    drop_keys = {"num_games", "num_goals", "num_assists", "update_date"}

    p = Player(pid=PID, game=game)
    actual_attributes = p.download()

    [(actual_attributes.pop(key), expected_attributes.pop(key)) for key in drop_keys]

    assert actual_attributes == expected_attributes


@pytest.mark.parametrize(
    "expected_prices, game", [(21, 21), (20, 20), (19, 19)], indirect=["expected_prices"]
)
def test_player_download_prices(expected_prices, game):
    p = Player(pid=PID, game=game)
    _ = p.download()
    assert p.download_prices() == expected_prices
