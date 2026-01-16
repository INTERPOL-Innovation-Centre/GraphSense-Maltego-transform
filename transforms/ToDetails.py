import sys
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform, UIM_INFORM
from maltego_trx.transform import DiscoverableTransform

from extensions import registry
from api.utils import create_entity_with_details, get_address_details, get_entity_details
from .utils import set_maltego_transformation_error, extract_address_and_currencies

@registry.register_transform(
    display_name="To Details",
    input_entity="maltego.Cryptocurrency",
    description="Returns details of a cryptocurrency address.",
    output_entities=["maltego.Cryptocurrency"],
)
class ToDetails(DiscoverableTransform):
    """
    Lookup for all details associated with a Virtual Asset (balance, total in and out, date last and first Tx...)
    """

    @classmethod
    def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):
        query_type = "details"
        address, currencies, error = extract_address_and_currencies(request.Properties)

        if error:
            response.addUIMessage(error, UIM_INFORM)
            return

        for currency in currencies:
            # If it's a numeric ID, it's a wallet/entity
            is_wallet = "cryptocurrency.wallet.name" in request.Properties or "cluster_ID" in request.Properties
            
            if is_wallet:
                obj, tags, api_error = get_entity_details(currency, int(address))
            else:
                obj, tags, api_error = get_address_details(currency, address)

            if api_error:
                set_maltego_transformation_error(response, currency, query_type, address, api_error)
            else:
                _, err = create_entity_with_details((obj, tags, ""), currency, query_type, response)
                if err:
                    set_maltego_transformation_error(response, currency, query_type, address, err)

if __name__ == "__main__":
    ToDetails.create_entities(sys.argv[1])
