import os

from dynaconf import Dynaconf

current_directory = os.getcwd()
secret_path = f'{current_directory}/.secrets.toml'

env_settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=[secret_path],
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
