"""Тесты коннекторов API на подменённых ответах (моки)."""

import pytest

from unittest.mock import patch, MagicMock

from src.infrastructure.api_connector import (
    AeroplanesAPI,
    NominatimAPI,
    OpenSkyAPI,
)


@pytest.fixture
def fake_coords():
    return {
        "lat_min": 27.0, "lat_max": 44.0,
        "lon_min": -19.0, "lon_max": 5.0,
    }


class TestNominatimAPI:

    def test_valid_country_returns_bbox(self):
        api = NominatimAPI()
        fake_response = MagicMock()
        fake_response.json.return_value = [
            {"boundingbox": ["27.6", "43.8", "-18.2", "4.3"]}
        ]
        with patch("src.infrastructure.api_connector.requests.get",
                   return_value=fake_response):
            coords = api.get_data("Spain")
        assert coords["lat_min"] == 27.6
        assert coords["lon_max"] == 4.3

    def test_cache_prevents_second_request(self):
        api = NominatimAPI()
        fake_response = MagicMock()
        fake_response.json.return_value = [
            {"boundingbox": ["27.6", "43.8", "-18.2", "4.3"]}
        ]
        with patch("src.infrastructure.api_connector.requests.get",
                   return_value=fake_response) as mock_get:
            api.get_data("Spain")
            api.get_data("Spain")
        assert mock_get.call_count == 1  # второй запрос из кэша

    def test_unknown_country_raises_value_error(self):
        api = NominatimAPI()
        fake_response = MagicMock()
        fake_response.json.return_value = []
        with patch("src.infrastructure.api_connector.requests.get",
                   return_value=fake_response):
            with pytest.raises(ValueError):
                api.get_data("НесуществующаяСтрана123")

    def test_empty_country_raises_value_error(self):
        api = NominatimAPI()
        with pytest.raises(ValueError):
            api.get_data("   ")


class TestOpenSkyAPI:

    def test_parse_state_fields(self, fake_coords):
        api = OpenSkyAPI()
        raw_state = ["a1b2c3", "IBE1234  ", "Spain", None, None, None,
                     None, None, None, 250.5, None, None, None, 10500.0]
        with patch("src.infrastructure.api_connector.requests.get") as mock_get:
            mock_get.return_value.json.return_value = {"states": [raw_state]}
            mock_get.return_value.raise_for_status.return_value = None
            planes = api.get_data(fake_coords)
        assert len(planes) == 1
        assert planes[0]["icao24"] == "a1b2c3"
        assert planes[0]["callsign"] == "IBE1234"  # пробелы обрезаны

    def test_null_states_returns_empty_list(self, fake_coords):
        api = OpenSkyAPI()
        with patch("src.infrastructure.api_connector.requests.get") as mock_get:
            mock_get.return_value.json.return_value = {"states": None}
            mock_get.return_value.raise_for_status.return_value = None
            assert api.get_data(fake_coords) == []


class TestAeroplanesAPI:

    def test_full_pipeline_skips_incomplete(self, fake_coords):
        """Фасад: борт без скорости не попадает в итоговый список."""
        raw_complete = ["aaa", "OK1", "Spain", None, None, None, None,
                        None, None, 250.0, None, None, None, 9000.0]
        raw_incomplete = ["bbb", "BAD", "Spain", None, None, None, None,
                          None, None, None, None, None, None, None]

        api = AeroplanesAPI()
        with patch.object(api._geo_api, "get_data", return_value=fake_coords), \
             patch("src.infrastructure.api_connector.requests.get") as mock_get:
            mock_get.return_value.json.return_value = {
                "states": [raw_complete, raw_incomplete]
            }
            mock_get.return_value.raise_for_status.return_value = None
            planes = api.get_aeroplanes("Spain")

        assert len(planes) == 1
        assert planes[0]["icao24"] == "aaa"
