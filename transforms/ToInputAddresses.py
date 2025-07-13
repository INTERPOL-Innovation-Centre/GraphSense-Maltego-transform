import sys
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform, UIM_INFORM
from maltego_trx.transform import DiscoverableTransform

from extensions import registry

from api.utils import (
    create_entity_with_details,
    get_currency_from_entity_details,
    get_address_neighbors,
)

from .utils import set_maltego_transformation_error


@registry.register_transform(
    display_name="To Input Addresses",
    input_entity="maltego.Cryptocurrency",
    description="Returns input addresses of a cryptocurerncy address.",
    output_entities=["maltego.Cryptocurrency"],
)
class ToInputAddresses(DiscoverableTransform):
    """
    Lookup for all input addresses associated with a Virtual Asset (balance, total in and out, date last and first Tx...)
    """

    @classmethod
    def create_entities(
        cls, request: MaltegoMsg, responseMaltego: MaltegoTransform = None
    ):
        query_type = "input_addresses"

        entity_details = request.Properties
        if (
            "cryptocurrency.wallet.name" in entity_details
        ):  # this means the source entity is a cluster (Wallet) and not a cryptocurrency address
            address = int(entity_details["cryptocurrency.wallet.name"])
            currencies = [
                str(entity_details["currency"])
            ]  # if it is a cluster the currency is known
        # if 'properties.cryptocurrencyaddress' in entity_details: #Else, we are looking for tags on a specific address
        # address = entity_details['properties.cryptocurrencyaddress']
        else:
            if (
                "currency" in entity_details
            ):  # if a currency is already specified in the details, we use that currency and only that one. Else, we try to figure out what currency this could be and check all.
                currencies = [entity_details["currency"]]
            else:
                currencies = get_currency_from_entity_details(
                    request.Properties
                )  # We use regex to check what Cryptocurrency this is. This could return BTC and BCH since they are similar.
                if currencies[1]:
                    responseMaltego.addUIMessage(
                        f"\n{currencies[1]}\n", UIM_INFORM
                    )
                    return
                currencies = currencies[0]
            address = entity_details["properties.cryptocurrencyaddress"]

        for currency in currencies:
            (neighbors, error) = get_address_neighbors(
                currency, address, "in"
            )

            if error:
                set_maltego_transformation_error(
                    responseMaltego, currency, query_type, str(address), error
                )
            else:
                for neighbor in neighbors:
                    neighbor, error = create_entity_with_details(
                        (neighbor, [], error),
                        currency,
                        query_type,
                        responseMaltego,
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
    ToInputAddresses.create_entities(sys.argv[1])
