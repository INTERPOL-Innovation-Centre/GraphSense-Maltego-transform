# extensions.py
from maltego_trx.decorator_registry import TransformRegistry

from settings import api_key_setting
from settings import api_url_setting

registry = TransformRegistry(
        owner="INTERPOL Innovation Centre",
        author="Vincent Danjean <v.danjean@interpol.int>",
        host_url="http://0.0.0.0:8080",
        seed_ids=["interpol.graphsense"]
)

# The rest of these attributes are optional

# metadata
registry.version = "0.1"

# transform suffix to indicate datasource
registry.display_name_suffix = " [GRAPHSENSE]"

registry.global_settings = [api_key_setting, api_url_setting]