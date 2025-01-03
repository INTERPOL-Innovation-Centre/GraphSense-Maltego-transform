# from maltego_trx.maltego import MaltegoEntity, MaltegoTransform
from maltego_trx.overlays import OverlayPosition, OverlayType

from graphsense.configuration import Configuration

import json

import re as regex

from graphsense.api import addresses_api, entities_api
from graphsense.api_client import ApiClient, ApiException

from datetime import datetime


def open_config():
    error = ""
    try:
        with open("config.json") as json_data_file:
            config = json.load(json_data_file)
        if "api_key" not in config or "api_url" not in config:
            print("Error message: Check the format of your config.json file")
        else:
            configuration = Configuration(
                host=config["api_url"], api_key={"api_key": config["api_key"]}
            )
    except ApiException as e:
        error = "Could not read config.json. Error: " + str(e)
    return configuration, error


def get_currency(virtual_asset_address):
    # supported_currencies are "btc"(not!), "bch", "ltc", "zec", "eth" (note: a BTC address could also be a bch address)
    currency = []
    virtual_asset_match = regex.search(
        r"\b([13][a-km-zA-HJ-NP-Z1-9]{25,34})|bc(0([ac-hj-np-z02-9]{39}|[ac-hj-np-z02-9]{59})|1[ac-hj-np-z02-9]{8,87})\b",
        virtual_asset_address,
    )
    if virtual_asset_match:
        currency.append("btc")
    virtual_asset_match = regex.search(
        r"\b((?:bitcoincash|bchtest):)?([0-9a-zA-Z]{34})\b",
        virtual_asset_address,
    )
    if virtual_asset_match:
        currency.append("bch")
    virtual_asset_match = regex.search(
        r"\b[LM3][a-km-zA-HJ-NP-Z1-9]{25,33}\b", virtual_asset_address
    )
    if virtual_asset_match:
        currency.append("ltc")
    virtual_asset_match = regex.search(
        r"\b[tz][13][a-km-zA-HJ-NP-Z1-9]{33}\b", virtual_asset_address
    )
    if virtual_asset_match:
        currency.append("zec")
    virtual_asset_match = regex.search(
        r"\b(0x)?[0-9a-fA-F]{40}\b", virtual_asset_address
    )
    if virtual_asset_match:
        currency.append("eth")
    if not currency:
        return [], "Currency not supported"
    return currency, []


def get_currency_from_entity_details(entity_details):
    currency = []
    if "BTCAddress" in entity_details:
        currency = ["btc"]
    if "BCHAddress" in entity_details:
        currency = ["bch"]
    if "LTCAddress" in entity_details:
        currency = ["ltc"]
    if "ZECAddress" in entity_details:
        currency = ["zec"]
    if "ETHAddress" in entity_details:
        currency = ["eth"]
    if not currency:
        currency = get_currency(
            entity_details["properties.cryptocurrencyaddress"]
        )
        if currency[1]:
            error = ["Currency not supported for: " + str(entity_details)]
            return [], error
    currency = currency[0]
    return currency, ""


def get_address_details(currency, address):
    error = ""
    configuration = open_config()[0]

    with ApiClient(configuration) as api_client:
        api_instance = addresses_api.AddressesApi(api_client)
        address_obj = []
        try:
            # Retrieve the address object
            address_obj = api_instance.get_address(currency, str(address))
        except Exception as e:
            error = "Exception when calling AddressesApi: " + str(e)
        tags = []
        # if 'address' in address_obj:
        try:
            tags = api_instance.list_tags_by_address(currency, str(address))
        except Exception as e:
            error = "Exception when calling List_tags_by_address: " + str(e)
        return address_obj, tags, error


def get_entity_details(currency, entity):
    error = ""
    configuration = open_config()[0]

    with ApiClient(configuration) as api_client:
        api_instance = entities_api.EntitiesApi(api_client)
        try:
            entity_obj = api_instance.get_entity(currency, entity)
        except Exception as e:
            error = "Exception when calling EntitiesApi: " + str(e)
            entity_obj = []
        tags = []
        try:
            # Retrieve the tags in the address object   <>>>>>> Currently this does not work !!!
            tags = api_instance.list_address_tags_by_entity(currency, entity)
        except Exception as e:
            error = (
                "Exception when calling list_address_tags_by_entity: " + str(e)
            )
        return entity_obj, tags, error


def create_entity_with_details(
    json_result, currency, query_type, response
):  # Query_type is one of : "known_entities", "tags", "details", "cluster"

    error = ""
    if currency == "btc":
        set_type = "maltego.BTCAddress"
        set_factor = 10e7  # Satoshi
    if currency == "bch":
        set_type = "maltego.BCHAddress"
        set_factor = 10e7  # Satoshi
    if currency == "ltc":
        set_type = "maltego.LTCAddress"
        set_factor = 10e7  # Litoshi
    if currency == "zec":
        set_type = "maltego.ZECAddress"
        set_factor = 10e7  # Zatoshi
    if currency == "eth":
        set_type = "maltego.ETHAddress"
        set_factor = 10e17  # Gwei

    if query_type == "details":
        if not (
            "address" in json_result[0]
        ):  # This means this is a cluster not a cryptocurrency address
            set_type = "maltego.CryptocurrencyWallet"
            cluster_ID = json_result[0][
                "entity"
            ]  # the Cluster ID is known as "entity" in GraphSense API json result
            entity = response.addEntity(set_type, cluster_ID)
            json_result = get_entity_details(currency, json_result[0]["entity"])
            if json_result[2]:
                error = (
                    "Got an error checking the cluster details: "
                    + json_result[2]
                )
                return "", error  # end this and report the error
            # json_result = json_result[0]
            entity.addProperty(
                "num_addresses",
                "Number of addresses",
                value=json_result[0]["no_addresses"],
            )
        else:
            if "properties.cryptocurrencyaddress" in json_result[0]:
                address = json_result[0]["properties.cryptocurrencyaddress"]
            else:
                address = json_result[0]["address"]
            entity = response.addEntity(set_type, address)

        entity.addOverlay(
            "", OverlayPosition.NORTH_WEST, OverlayType.TEXT
        )  # first we reset the overlay
        if (json_result[1]["address_tags"]) or (
            "best_address_tag" in json_result[1]
        ):
            tags = json_result[1]
            if not ("Wallet" in set_type):
                entity.addOverlay(
                    "Businessman", OverlayPosition.NORTH_WEST, OverlayType.IMAGE
                )
            else:
                if ("address_tags" in tags) or (
                    "entity_tags" in tags
                ):  # or ('label' in tags):
                    entity.addOverlay(
                        "Businessman",
                        OverlayPosition.NORTH_WEST,
                        OverlayType.IMAGE,
                    )

        balance_value = json_result[0]["balance"]["value"] / set_factor

        total_received_value = (
            json_result[0]["total_received"]["value"] / set_factor
        )
        total_sent_value = json_result[0]["total_spent"]["value"] / set_factor
        balance_fiat_value = json_result[0]["balance"]["fiat_values"][0][
            "value"
        ]
        balance_fiat_currency = json_result[0]["balance"]["fiat_values"][0][
            "code"
        ]
        num_transactions = (
            json_result[0]["no_incoming_txs"]
            + json_result[0]["no_outgoing_txs"]
        )
        cluster_ID = json_result[0]["entity"]
        total_throughput = total_received_value + total_sent_value
        last_tx_datetime = datetime.fromtimestamp(
            json_result[0]["last_tx"]["timestamp"]
        )
        first_tx_datetime = datetime.fromtimestamp(
            json_result[0]["first_tx"]["timestamp"]
        )

        if not (
            "Wallet" in set_type
        ):  # we do not want to overwrite these details if we are documenting a cluster.
            entity.addProperty("currency", "Currency", value=currency)
            entity.addProperty(
                "cluster_ID", "Cluster ID", "loose", value=cluster_ID
            )
        entity.addProperty(
            "final_balance",
            "Final balance (" + currency + ")",
            value=balance_value,
        )
        entity.addProperty(
            "final_balance_fiat",
            "Final balance (" + balance_fiat_currency + ")",
            value=balance_fiat_value,
        )
        entity.addProperty(
            "total_throughput", "Total throughput", value=total_throughput
        )
        entity.addProperty(
            "total_received", "Total received", value=total_received_value
        )
        entity.addProperty("total_sent", "Total sent", value=total_sent_value)
        entity.addProperty(
            "num_transactions", "Number of transactions", value=num_transactions
        )
        entity.addProperty(
            "num_in_transactions",
            "Number of incoming transactions",
            value=json_result[0]["no_incoming_txs"],
        )
        entity.addProperty(
            "num_out_transactions",
            "Number of outgoing transactions",
            value=json_result[0]["no_outgoing_txs"],
        )
        entity.addProperty(
            "Last_tx", "Last transaction (UTC)", value=last_tx_datetime
        )
        entity.addProperty(
            "First_tx", "First transaction (UTC)", value=first_tx_datetime
        )

    if query_type == "cluster":
        icon_name = set_type[8:]
        if icon_name == "ZECAddress":
            icon_name = "zcash_icon_fullcolor"
        set_type = "maltego.CryptocurrencyWallet"
        cluster_ID = json_result[0][
            "entity"
        ]  # the Cluster ID is known as "entity" in GraphSense API json result

        json_result = get_entity_details(currency, cluster_ID)
        if json_result[2]:
            error = "Got an error getting the cluster ID: " + json_result[2]
            return "", error
        else:
            json_result1 = json_result[1]
            json_result = json_result[0]

        balance_value = json_result["balance"]["value"] / set_factor
        total_received_value = (
            json_result["total_received"]["value"] / set_factor
        )
        total_sent_value = json_result["total_spent"]["value"] / set_factor
        balance_fiat_value = json_result["balance"]["fiat_values"][0]["value"]
        balance_fiat_currency = json_result["balance"]["fiat_values"][0]["code"]
        num_transactions = (
            json_result["no_incoming_txs"] + json_result["no_outgoing_txs"]
        )
        cluster_ID = json_result["entity"]
        total_throughput = total_received_value + total_sent_value
        last_tx_datetime = datetime.fromtimestamp(
            json_result["last_tx"]["timestamp"]
        )
        first_tx_datetime = datetime.fromtimestamp(
            json_result["first_tx"]["timestamp"]
        )

        entity = response.addEntity(set_type, cluster_ID)
        entity.setLinkLabel(
            str("To Cluster [Graphense] " + "(" + currency) + ")"
        )
        entity.addProperty("cryptocurrency.wallet.name", value=cluster_ID)
        entity.addProperty("cluster_ID", "Cluster ID", value=cluster_ID)
        entity.addProperty(
            "currency", "Currency", "strict", value=currency
        )  # we want this to be strict matching so that Maltego doesn't merge two clusters that are different (one is btc and the other bch for instance).
        entity.addProperty(
            "final_balance",
            "Final balance (" + currency + ")",
            value=balance_value,
        )
        entity.addProperty(
            "final_balance_fiat",
            "Final balance (" + balance_fiat_currency + ")",
            value=balance_fiat_value,
        )
        entity.addProperty(
            "total_throughput", "Total throughput", value=total_throughput
        )
        entity.addProperty(
            "total_received", "Total received", value=total_received_value
        )
        entity.addProperty("total_sent", "Total sent", value=total_sent_value)
        entity.addProperty(
            "num_transactions", "Number of transactions", value=num_transactions
        )
        entity.addProperty(
            "num_in_transactions",
            "Number of incoming transactions",
            value=json_result["no_incoming_txs"],
        )
        entity.addProperty(
            "num_out_transactions",
            "Number of outgoing transactions",
            value=json_result["no_outgoing_txs"],
        )
        entity.addProperty(
            "Last_tx", "Last transaction (UTC)", value=last_tx_datetime
        )
        entity.addProperty(
            "First_tx", "First transaction (UTC)", value=first_tx_datetime
        )
        entity.addProperty(
            "Number_addresses",
            "Number of Addresses",
            value=json_result["no_addresses"],
        )
        entity.addOverlay(
            json_result["no_addresses"],
            OverlayPosition.SOUTH_WEST,
            OverlayType.TEXT,
        )
        entity.addOverlay(icon_name, OverlayPosition.WEST, OverlayType.IMAGE)
        entity.addOverlay(
            "", OverlayPosition.NORTH_WEST, OverlayType.TEXT
        )  # first we reset the overlay
        if (
            (json_result1["address_tags"])
            or ("tags" in json_result1)
            or ("best_address_tag" in json_result1)
        ):
            entity.addOverlay(
                "Businessman", OverlayPosition.NORTH_WEST, OverlayType.IMAGE
            )

    if query_type == "tags":
        tags = []
        set_type = "maltego.CryptocurrencyOwner"

        json_result = get_address_details(
            currency, json_result[0]["address"]
        )  # We query the entity to get the "Address" and the "Entity" (cluster) tags if any.

        if json_result[2]:
            error = "Got an error getting the address tags: " + json_result[2]
            return "", error
        else:
            json_result = json_result[1]
        if ("tags" in json_result) or ("best_address_tag" in json_result):
            tags = json_result["best_address_tag"]
        if "address_tags" in json_result:
            tags = json_result["address_tags"]
        else:
            if "label" in tags:
                tags = json_result["label"]
        if tags:
            if "error" in tags:
                error = str(
                    "error in address tags: " + tags["error"]["message"]
                )
            # Create new entity for each tag we found
            # If we have the same tag multiple times, Maltego will merge them automatically
            # Tags without a label are non-public, we create them with an indication of who should be contacted for details (tagpack creator)
            for tag in tags:
                if "label" in tag:
                    if tag["label"]:
                        entity = response.addEntity(
                            "Cryptocurrency", tag["label"]
                        )
                        entity.setLinkLabel(
                            "To tags [GraphSense] (" + tag["currency"] + ")"
                        )
                        entity.setType("maltego.CryptocurrencyOwner")
                    else:
                        entity = response.addEntity(
                            "Cryptocurrency",
                            "Undisclosed, contact: " + tag["tagpack_creator"],
                        )
                        entity.setLinkLabel(
                            "To tags [GraphSense] (" + tag["currency"] + ")"
                        )
                        entity.setType("maltego.CryptocurrencyOwner")
                        entity.setIconURL("Unknown")
                if "category" in tag:
                    entity.addProperty("OwnerType", "loose", tag["category"])
                # if "address" in tag:
                # 	entity.addProperty("Address", "Address", "strict", value=tag["address"])
                # 	entity.addProperty("Cryptocurrency", "Cryptocurrency", "strict", value=tag["currency"])
                if "source" in tag:
                    entity.addProperty(
                        "Source_URI", "Source", "loose", value=tag["source"]
                    )
                    uri_link = str(
                        '<a href="'
                        + str(tag["source"])
                        + '">'
                        + str(tag["source"])
                        + "</a>"
                    )
                    entity.addDisplayInformation(uri_link, "Source URI")
                if "tagpack_creator" in tag:
                    entity.addProperty(
                        "tagpack_creator",
                        "Tagpack Creator",
                        "strict",
                        value=tag["tagpack_creator"],
                    )
                if "tagpack_title" in tag:
                    entity.addProperty(
                        "tagpack_title",
                        "Tagpack Title",
                        "loose",
                        value=tag["tagpack_title"],
                    )
                if "abuse" in tag:
                    entity.addProperty(
                        "Abuse_type", "Abuse type", "loose", value=tag["abuse"]
                    )
                if "category" in tag:
                    entity.addProperty(
                        "Category", "Category", "loose", value=tag["category"]
                    )
                if "confidence_level" in tag:
                    entity.addProperty(
                        "Confidence_level",
                        "Confidence Level",
                        "loose",
                        value=tag["confidence_level"],
                    )
                    entity.setWeight(int(tag["confidence_level"]))
        else:
            entity = ""
            error = "No attribution tags found for this address in " + currency

    if query_type == "entity_tags":  # (that's the tags at cluster level)
        tags = []
        set_type = "maltego.CryptocurrencyOwner"
        json_result = get_entity_details(
            currency, json_result[0]["entity"]
        )  # "entity" = Entity Wallet which is the GraphSense Cluster ID
        if json_result[2]:
            error = (
                "Got an error getting the cluster tags: "
                + json_result[2]
                + ". Entity: "
                + str(json_result[0]["entity"])
            )
            return "", error
        else:
            json_result = json_result[1]
        if ("tags" in json_result) or ("best_address_tag" in json_result):
            tags = json_result["best_address_tag"]
        if "address_tags" in json_result:
            tags = json_result["address_tags"]
        else:
            if "label" in tags:
                tags = json_result["label"]
        if tags:
            if "error" in tags:
                error = str(
                    "error in address tags: " + tags["error"]["message"]
                )
            # Create new entity for each tag we found
            # If we have the same tag multiple times, Maltego will merge them automatically
            # Tags without a label are non-public, we create them with an indication of who should be contacted for details (tagpack creator)
            for tag in tags:
                if "label" in tag:
                    if tag["label"]:
                        entity = response.addEntity(
                            "Cryptocurrency", tag["label"]
                        )
                        entity.setLinkLabel(
                            "To tags [GraphSense] (" + tag["currency"] + ")"
                        )
                        entity.setType("maltego.CryptocurrencyOwner")
                    else:
                        entity = response.addEntity(
                            "Cryptocurrency",
                            "Undisclosed, contact: " + tag["tagpack_creator"],
                        )
                        entity.setLinkLabel(
                            "To tags [GraphSense] (" + tag["currency"] + ")"
                        )
                        entity.setType("maltego.CryptocurrencyOwner")
                        entity.setIconURL("Unknown")
                if "category" in tag:
                    entity.addProperty("OwnerType", "loose", tag["category"])
                # if "address" in tag:
                # 	entity.addProperty("Address", "Address", "strict", value=tag["address"])
                # 	entity.addProperty("Cryptocurrency", "Cryptocurrency", "strict", value=tag["currency"])
                if "source" in tag:
                    entity.addProperty(
                        "Source_URI", "Source", "loose", value=tag["source"]
                    )
                    uri_link = str(
                        '<a href="'
                        + str(tag["source"])
                        + '">'
                        + str(tag["source"])
                        + "</a>"
                    )
                    entity.addDisplayInformation(uri_link, "Source URI")
                if "tagpack_creator" in tag:
                    entity.addProperty(
                        "tagpack_creator",
                        "Tagpack Creator",
                        "strict",
                        value=tag["tagpack_creator"],
                    )
                if "tagpack_title" in tag:
                    entity.addProperty(
                        "tagpack_title",
                        "Tagpack Title",
                        "loose",
                        value=tag["tagpack_title"],
                    )
                if "abuse" in tag:
                    entity.addProperty(
                        "Abuse_type", "Abuse type", "loose", value=tag["abuse"]
                    )
                if "category" in tag:
                    entity.addProperty(
                        "Category", "Category", "loose", value=tag["category"]
                    )
                if "confidence_level" in tag:
                    entity.addProperty(
                        "Confidence_level",
                        "Confidence Level",
                        "loose",
                        value=tag["confidence_level"],
                    )
                    entity.setWeight(int(tag["confidence_level"]))
        else:
            entity = ""
            error = "No attribution tags found for this cluster in " + currency

    entity = ""

    return entity, error
