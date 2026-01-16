from typing import List, Tuple, Dict, Any, Optional
from maltego_trx.maltego import MaltegoTransform, UIM_PARTIAL, UIM_INFORM
from api.utils import get_currency_from_entity_details

def set_maltego_transformation_error(
    responseMaltego: MaltegoTransform,
    currency: str,
    query_type: str,
    address: str,
    error: str,
):
    """Sets a formatted error message in Maltego's UI."""
    if "504 Bad Gateway" in error:
        msg = f"\nGraphSense server 504 error during {query_type} for {currency} on {address}\n"
    elif "(404)" in error:
        msg = f"\nNothing found in {currency} for: {address}\n"
    else:
        msg = f"Error ({currency}): {error}"
    
    responseMaltego.addUIMessage(msg, UIM_PARTIAL)

def extract_address_and_currencies(properties: Dict[str, Any]) -> Tuple[Optional[str], List[str], Optional[str]]:
    """ Extracts address and list of currencies to check from Maltego properties. """
    
    # Handle Cluster/Wallet ID
    if "cryptocurrency.wallet.name" in properties or "cluster_ID" in properties:
        val = properties.get("cryptocurrency.wallet.name") or properties.get("cluster_ID")
        try:
            address = str(int(val)) # Ensure it's a numeric ID
        except (ValueError, TypeError):
            return None, [], "Invalid Cluster/Wallet ID format (expected integer)"
            
        currency = properties.get("currency")
        if not currency:
            return None, [], "Cluster found but currency is missing"
        return address, [str(currency)], None

    # Handle Standard Address
    address = properties.get("properties.cryptocurrencyaddress")
    if not address:
        return None, [], "No cryptocurrency address found in properties"

    if "currency" in properties:
        return address, [properties["currency"]], None
    
    # Auto-detect currency
    currencies, error = get_currency_from_entity_details(properties)
    if error:
        return address, [], error
        
    return address, currencies, None
