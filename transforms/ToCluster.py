import sys
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform, UIM_INFORM
from maltego_trx.transform import DiscoverableTransform

from extensions import registry
from api.utils import create_entity_with_details, get_address_details
from .utils import set_maltego_transformation_error, extract_address_and_currencies

@registry.register_transform(
    display_name="To Cluster",
    input_entity="maltego.Cryptocurrency",
    description="Returns the cluster details to which the address belongs.",
    output_entities=["maltego.Cryptocurrency"],
)
class ToCluster(DiscoverableTransform):
    """
    Lookup for the cluster (Entity ID) associated with a Virtual Asset
    """

    @classmethod
    def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):
        query_type = "cluster"
        address, currencies, error = extract_address_and_currencies(request.Properties)

        if error:
            response.addUIMessage(error, UIM_INFORM)
            return

        for currency in currencies:
            obj, tags, api_error = get_address_details(currency, address)

            if api_error:
                set_maltego_transformation_error(response, currency, query_type, address, api_error)
            else:
                _, err = create_entity_with_details((obj, tags, ""), currency, query_type, response)
                if err:
                    set_maltego_transformation_error(response, currency, query_type, address, err)

if __name__ == "__main__":
    ToCluster.create_entities(sys.argv[1])
