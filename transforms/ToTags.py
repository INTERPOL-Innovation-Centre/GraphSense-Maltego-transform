import sys
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform, UIM_INFORM
from maltego_trx.transform import DiscoverableTransform

from extensions import registry
from api.utils import create_entity_with_details, get_address_details, get_entity_details
from .utils import set_maltego_transformation_error, extract_address_and_currencies

@registry.register_transform(
    display_name="To Tags",
    input_entity="maltego.Cryptocurrency",
    description="Returns known attribution tags",
    output_entities=["maltego.Cryptocurrency"],
)
class ToTags(DiscoverableTransform):
    """
    Lookup the attribution tags associated with a Virtual Asset and the entity (cluster) it belongs to.
    """

    @classmethod
    def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):
        address, currencies, error = extract_address_and_currencies(request.Properties)

        if error:
            response.addUIMessage(error, UIM_INFORM)
            return

        is_wallet = "cryptocurrency.wallet.name" in request.Properties or "cluster_ID" in request.Properties
        query_type = "entity_tags" if is_wallet else "tags"

        for currency in currencies:
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
    ToTags.create_entities(sys.argv[1])
