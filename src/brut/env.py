from pathlib import Path

from environ import config, group, to_config, var


@config(prefix="MEGU")
class MeguEnv:
    plugin_dir: Path = var(converter=Path)


@config(prefix="LOG")
class LogEnv:
    loki_url: str | None = var(default=None)
    level: str = var(default="INFO")


@config(prefix="BRUT")
class BrutEnv:

    database_path: Path = var(converter=Path)
    redis_url: str = var()
    config_path: Path = var(converter=Path)
    store_dir: Path = var(converter=Path)
    megu: MeguEnv = group(MeguEnv)
    log: LogEnv = group(LogEnv)


def get_env() -> BrutEnv:
    return to_config(BrutEnv)


instance = get_env()
