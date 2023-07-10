import sys
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform, UIM_INFORM
from maltego_trx.transform import DiscoverableTransform

from extensions import registry

from api.utils import (
    create_entity_with_details,
    get_currency_from_entity_details,
    get_address_details,
)


from .utils import set_maltego_transformation_error


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
    def create_entities(
        cls, request: MaltegoMsg, responseMaltego: MaltegoTransform
    ):

        query_type = "cluster"

        entity_details = request.Properties
        if "properties.cryptocurrencyaddress" in entity_details:
            address = entity_details["properties.cryptocurrencyaddress"]
        else:
            address = entity_details["address"]
        if (
            address[:2] == "bc"
        ):  # beech32 BTC addresses include "bc" at the begining, we want to remove that.
            # address = address[2:] Not needed because Graphsense can handle bcxxx addresses.
            currencies = [
                "btc"
            ]  # we know this is BTC, no need to check for BCH or other currencies.
        else:
            if (
                "currency" in entity_details
            ):  # if a currency is already specified in the details, we use that currency and only that one. Else, we try to figure out what currency this could be and check all.
                currencies = [entity_details["currency"]]
            else:
                currencies = get_currency_from_entity_details(
                    request.Properties
                )  # We use regex to check what Cryptocurrency this is. This could return BTC and BCH since they are similar.
                if currencies[2]:
                    responseMaltego.addUIMessage(
                        "\n" + currencies[1] + "\n", UIM_INFORM
                    )
                    return
                currencies = currencies[0]
            address = entity_details["properties.cryptocurrencyaddress"]

        for currency in currencies:
            addr, tags, error = get_address_details(currency, address)
            if error:
                set_maltego_transformation_error(
                    responseMaltego, currency, query_type, str(address), error
                )

            else:
                entity, error = create_entity_with_details(
                    (addr, tags, error), currency, query_type, responseMaltego
                )
                if error:
                    set_maltego_transformation_error(
                        responseMaltego,
                        currency,
                        query_type,
                        str(address),
                        error,
                    )
        return


if __name__ == "__main__":
    ToCluster.create_entities(sys.argv[1])
