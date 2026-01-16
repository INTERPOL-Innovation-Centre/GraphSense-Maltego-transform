import json
import logging
import re as regex
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

from graphsense.api import addresses_api, entities_api
from graphsense.api_client import ApiClient, ApiException
from graphsense.configuration import Configuration
from maltego_trx.overlays import OverlayPosition, OverlayType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Currency Constants
CURRENCY_CONFIG = {
    "btc": {"type": "maltego.BTCAddress", "factor": 1e8, "label": "Satoshi"},
    "bch": {"type": "maltego.BCHAddress", "factor": 1e8, "label": "Satoshi"},
    "ltc": {"type": "maltego.LTCAddress", "factor": 1e8, "label": "Litoshi"},
    "zec": {"type": "maltego.ZECAddress", "factor": 1e8, "label": "Zatoshi"},
    "eth": {"type": "maltego.ETHAddress", "factor": 1e18, "label": "Wei"},  # Graphsence uses Wei/Gwei? factor 1e18 is standard for ETH->Wei
}

class GraphSenseClient:
    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GraphSenseClient, cls).__new__(cls)
        return cls._instance

    def _load_config(self) -> Configuration:
        if self._config:
            return self._config

        try:
            with open("config.json") as f:
                config_data = json.load(f)
            
            if "api_key" not in config_data or "api_url" not in config_data:
                raise ValueError("Invalid config.json format")

            self._config = Configuration(
                host=config_data["api_url"],
                api_key={"api_key": config_data["api_key"]}
            )
            return self._config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise

    def get_addresses_api(self, api_client: ApiClient) -> addresses_api.AddressesApi:
        return addresses_api.AddressesApi(api_client)

    def get_entities_api(self, api_client: ApiClient) -> entities_api.EntitiesApi:
        return entities_api.EntitiesApi(api_client)

    def get_api_client(self) -> ApiClient:
        return ApiClient(self._load_config())


def get_currency(address: str) -> Tuple[List[str], str]:
    """Detects possible currencies for a given address using regex."""
    currencies = []
    
    # BTC Regex
    if regex.search(r"\b([13][a-km-zA-HJ-NP-Z1-9]{25,34})|bc(0([ac-hj-np-z02-9]{39}|[ac-hj-np-z02-9]{59})|1[ac-hj-np-z02-9]{8,87})\b", address):
        currencies.append("btc")
    
    # BCH Regex
    if regex.search(r"\b((?:bitcoincash|bchtest):)?([0-9a-zA-Z]{34})\b", address):
        currencies.append("bch")
    
    # LTC Regex
    if regex.search(r"\b[LM3][a-km-zA-HJ-NP-Z1-9]{25,33}\b", address):
        currencies.append("ltc")
    
    # ZEC Regex
    if regex.search(r"\b[tz][13][a-km-zA-HJ-NP-Z1-9]{33}\b", address):
        currencies.append("zec")
    
    # ETH Regex
    if regex.search(r"\b(0x)?[0-9a-fA-F]{40}\b", address):
        currencies.append("eth")

    if not currencies:
        return [], "Currency not supported"
    return currencies, ""


def get_currency_from_entity_details(entity_details: Dict) -> Tuple[List[str], str]:
    """Extracts currency from Maltego entity details or fallback to regex detection."""
    for key, curr in [("BTCAddress", "btc"), ("BCHAddress", "bch"), ("LTCAddress", "ltc"), ("ZECAddress", "zec"), ("ETHAddress", "eth")]:
        if key in entity_details:
            return [curr], ""
    
    address = entity_details.get("properties.cryptocurrencyaddress")
    if address:
        return get_currency(address)
    
    return [], "No address or currency found in entity details"


def get_address_details(currency: str, address: str) -> Tuple[Optional[Any], List[Any], str]:
    client = GraphSenseClient()
    try:
        with client.get_api_client() as api_client:
            api = client.get_addresses_api(api_client)
            address_obj = api.get_address(currency, address)
            tags = api.list_tags_by_address(currency, address)
            return address_obj, tags, ""
    except ApiException as e:
        return None, [], f"GraphSense API error (Address): {e}"
    except Exception as e:
        return None, [], f"Unexpected error: {e}"


def get_entity_details(currency: str, entity_id: int) -> Tuple[Optional[Any], List[Any], str]:
    client = GraphSenseClient()
    try:
        with client.get_api_client() as api_client:
            api = client.get_entities_api(api_client)
            entity_obj = api.get_entity(currency, entity_id)
            tags = api.list_address_tags_by_entity(currency, entity_id)
            return entity_obj, tags, ""
    except ApiException as e:
        return None, [], f"GraphSense API error (Entity): {e}"
    except Exception as e:
        return None, [], f"Unexpected error: {e}"


def _add_common_properties(entity, details, currency: str):
    conf = CURRENCY_CONFIG.get(currency, {"factor": 1e8})
    factor = conf["factor"]

    balance = details.balance
    total_received = details.total_received
    total_spent = details.total_spent
    
    # Basic Props
    entity.addProperty("final_balance", f"Final balance ({currency})", value=balance.value / factor)
    if balance.fiat_values:
        fiat = balance.fiat_values[0]
        entity.addProperty("final_balance_fiat", f"Final balance ({fiat.code})", value=fiat.value)
    
    entity.addProperty("total_received", "Total received", value=total_received.value / factor)
    entity.addProperty("total_sent", "Total sent", value=total_spent.value / factor)
    entity.addProperty("total_throughput", "Total throughput", value=(total_received.value + total_spent.value) / factor)
    
    # Tx Counts
    entity.addProperty("num_transactions", "Number of transactions", value=details.no_incoming_txs + details.no_outgoing_txs)
    entity.addProperty("num_in_transactions", "Number of incoming transactions", value=details.no_incoming_txs)
    entity.addProperty("num_out_transactions", "Number of outgoing transactions", value=details.no_outgoing_txs)
    
    # Dates
    if details.first_tx:
        entity.addProperty("First_tx", "First transaction (UTC)", value=datetime.fromtimestamp(details.first_tx.timestamp))
    if details.last_tx:
        entity.addProperty("Last_tx", "Last transaction (UTC)", value=datetime.fromtimestamp(details.last_tx.timestamp))


def create_entity_with_details(
    api_result: Tuple[Any, Any, str],
    currency: str,
    query_type: str,
    response
) -> Tuple[Optional[Any], str]:
    """Helper to create Maltego entities from API results."""
    obj, tags_obj, error = api_result
    if error:
        return None, error

    conf = CURRENCY_CONFIG.get(currency)
    if not conf:
        return None, f"Unsupported currency: {currency}"

    if query_type == "details":
        # Check if it's a cluster or address
        is_cluster = not hasattr(obj, 'address')
        
        if is_cluster:
            entity_type = "maltego.CryptocurrencyWallet"
            entity_value = str(obj.entity)
            entity = response.addEntity(entity_type, entity_value)
            entity.addProperty("num_addresses", "Number of addresses", value=obj.no_addresses)
        else:
            entity_type = conf["type"]
            entity_value = obj.address
            entity = response.addEntity(entity_type, entity_value)
            entity.addProperty("currency", "Currency", value=currency)
            entity.addProperty("cluster_ID", "Cluster ID", "loose", value=obj.entity)

        _add_common_properties(entity, obj, currency)

        # Overlay logic
        has_tags = False
        if hasattr(tags_obj, 'address_tags') and tags_obj.address_tags:
            has_tags = True
        elif hasattr(tags_obj, 'entity_tags') and tags_obj.entity_tags:
             has_tags = True
        
        if has_tags:
            entity.addOverlay("Businessman", OverlayPosition.NORTH_WEST, OverlayType.IMAGE)

        return entity, ""

    if query_type == "cluster":
        entity = response.addEntity("maltego.CryptocurrencyWallet", str(obj.entity))
        entity.setLinkLabel(f"To Cluster [GraphSense] ({currency})")
        entity.addProperty("cryptocurrency.wallet.name", value=str(obj.entity))
        entity.addProperty("cluster_ID", "Cluster ID", value=str(obj.entity))
        entity.addProperty("currency", "Currency", "strict", value=currency)
        entity.addProperty("Number_addresses", "Number of Addresses", value=obj.no_addresses)
        
        _add_common_properties(entity, obj, currency)
        
        entity.addOverlay(obj.no_addresses, OverlayPosition.SOUTH_WEST, OverlayType.TEXT)
        # Use simple logic for icons
        icon_name = conf["type"][8:]
        if icon_name == "ZECAddress": icon_name = "zcash_icon_fullcolor"
        entity.addOverlay(icon_name, OverlayPosition.WEST, OverlayType.IMAGE)

        if (hasattr(tags_obj, 'address_tags') and tags_obj.address_tags) or \
           (hasattr(tags_obj, 'entity_tags') and tags_obj.entity_tags):
            entity.addOverlay("Businessman", OverlayPosition.NORTH_WEST, OverlayType.IMAGE)
            
        return entity, ""

    if query_type in ["tags", "entity_tags"]:
        # tags_obj here is actually the tags list from the API
        tags = []
        if hasattr(tags_obj, 'address_tags'):
            tags = tags_obj.address_tags
        elif hasattr(tags_obj, 'entity_tags'):
            tags = tags_obj.entity_tags
        elif isinstance(tags_obj, list):
            tags = tags_obj

        if not tags:
            return None, f"No attribution tags found for this query in {currency}"

        for tag in tags:
            label = getattr(tag, 'label', None)
            if label:
                entity = response.addEntity("maltego.CryptocurrencyOwner", label)
            else:
                creator = getattr(tag, 'tagpack_creator', 'Unknown')
                entity = response.addEntity("maltego.CryptocurrencyOwner", f"Undisclosed, contact: {creator}")
                entity.setIconURL("Unknown")
            
            entity.setLinkLabel(f"To tags [GraphSense] ({currency})")
            
            # Map properties safely
            safe_add_prop(entity, "OwnerType", getattr(tag, 'category', None), "loose")
            safe_add_prop(entity, "Source_URI", getattr(tag, 'source', None), "loose")
            if hasattr(tag, 'source') and tag.source:
                entity.addDisplayInformation(f'<a href="{tag.source}">{tag.source}</a>', "Source URI")
            
            safe_add_prop(entity, "tagpack_creator", getattr(tag, 'tagpack_creator', None), "strict")
            safe_add_prop(entity, "tagpack_title", getattr(tag, 'tagpack_title', None), "loose")
            safe_add_prop(entity, "Abuse_type", getattr(tag, 'abuse', None), "loose")
            safe_add_prop(entity, "Category", getattr(tag, 'category', None), "loose")
            
            conf_level = getattr(tag, 'confidence_level', None)
            if conf_level is not None:
                entity.addProperty("Confidence_level", "Confidence Level", "loose", value=conf_level)
                try:
                    entity.setWeight(int(conf_level))
                except:
                    pass

        return None, "" # Return dummy since entities are added to response directly

    return None, f"Unknown query type: {query_type}"


def safe_add_prop(entity, name: str, value: Any, matching: str = "loose"):
    if value is not None:
        entity.addProperty(name, name.replace("_", " "), matching, value=value)
