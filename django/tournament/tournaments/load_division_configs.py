from pathlib import Path
import yaml


def load_division_configs(filename):
    config_path = Path(filename)
    if not config_path.is_absolute():
        config_path = Path(__file__).resolve().parent / config_path

    with config_path.open(encoding="utf-8") as config_file:
        division_configs = yaml.safe_load(config_file) or {}

    if not isinstance(division_configs, dict):
        raise ValueError("Division config must be a mapping keyed by division slug.")

    for division_slug, division_config in division_configs.items():
        if not isinstance(division_config, dict):
            raise ValueError(f"Division '{division_slug}' config must be a mapping.")

        if "name" not in division_config:
            raise ValueError(f"Division '{division_slug}' must define 'name'.")

        teams = division_config.get("teams", [])
        if not isinstance(teams, list):
            raise ValueError(f"Division '{division_slug}' teams must be a list.")

        teams_count = division_config.get("teams_count", len(teams))
        if teams_count != len(teams):
            raise ValueError(
                f"Division '{division_slug}' teams_count ({teams_count}) does not match the number of teams ({len(teams)})."
            )

    return division_configs