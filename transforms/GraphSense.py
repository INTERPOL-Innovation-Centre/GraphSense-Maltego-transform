from maltego_trx.entities import Phrase

from maltego_trx.maltego import UIM_PARTIAL, UIM_FATAL
from maltego_trx.transform import DiscoverableTransform
import sys
import requests
import re as regex
import json


class GraphSense(DiscoverableTransform):
    """
    Lookup the name associated with a Virtual_Asset address.
    """

    @classmethod
    def create_entities(cls, request, response):
        Virtual_Asset_address = request.Value.strip()
        try:
            graphsense_tag = cls.get_details(Virtual_Asset_address)
            if graphsense_tag:
                if "error" in graphsense_tag:
                    response.addUIMessage(graphsense_tag["error"]["message"], messageType=UIM_FATAL)
                if "label" in graphsense_tag:
                    entity = response.addEntity(Phrase, graphsense_tag["label"])
                    entity.setLinkLabel("To tags [GraphSense]")
                    entity.setType("maltego.CryptocurrencyOwner")
                    if "category" in graphsense_tag:
                        entity.addProperty("OwnerType", "loose", graphsense_tag["category"])
                    if "source" in graphsense_tag:
                        entity_note = "Source : " + graphsense_tag["source"] + "\n"
                    if "abuse" in graphsense_tag:
                        entity_note = entity_note + "Abuse : " + graphsense_tag["abuse"]
                    if entity_note:
                        entity.setNote(entity_note)
            else:
                response.addUIMessage("The Virtual_Asset address was not found")
        except Exception as e:
            print(e)
            response.addUIMessage("An error occurred", messageType=UIM_PARTIAL)

    @staticmethod
    def load_config():
        with open("config.json") as json_data_file:
            config = json.load(json_data_file)
        return config

    @staticmethod
    def get_details(Virtual_Asset_address):
        wallet_tag_label = ""
        req = ""
        tag = ""
        i = 0
        currency = ""
        currencies = [""]
        #supported_currencies are "btc", "bch", "ltc", "zec", "eth" (note: a BTC address could also be a bch address)
        Virtual_Asset_match = regex.search(r"\b([13][a-km-zA-HJ-NP-Z1-9]{25,34})|bc(0([ac-hj-np-z02-9]{39}|[ac-hj-np-z02-9]{59})|1[ac-hj-np-z02-9]{8,87})\b", Virtual_Asset_address)
        if Virtual_Asset_match:
           currencies[i] = "btc"
           i += 1
        Virtual_Asset_match = regex.search(r"\b(bitcoincash\:)?[qp]([0-9a-zA-Z]{41})\b", Virtual_Asset_address)
        if Virtual_Asset_match:
           currencies[i] = "bch"
        Virtual_Asset_match = regex.search(r"\b[LM3][a-km-zA-HJ-NP-Z1-9]{25,33}\b", Virtual_Asset_address)
        if Virtual_Asset_match:
           currencies[i] = "ltc"
        else :
           Virtual_Asset_match = regex.search(r"\b[tz][13][a-km-zA-HJ-NP-Z1-9]{33}\b", Virtual_Asset_address)
           if Virtual_Asset_match:
              currencies[i] = "zec"
           else :
              Virtual_Asset_match = regex.search(r"\b(0x)?[0-9a-fA-F]{40}\b", Virtual_Asset_address)
              if Virtual_Asset_match:
                 currencies[i] = "eth"

        config = GraphSense.load_config()
        if "token" not in config or "api" not in config:
            return {"error": {"message":"Can not load data from config.json file"}}
        if config["token"] == "YOUR TOKEN":
            return {"error": {"message":"No GraphSense token have been set in the config.json file"}}
            
        for currency in currencies:
           try:
               req = requests.get(config["api"] + "/" + currency + "/addresses/" + Virtual_Asset_address, headers={'Authorization': config["token"]})
               address = req.json()
               if "tags" in address:
                   tags = address["tags"]
                   if len(tags) > 0:
                       tag = tags[0]
                       if "label" in tag:
                           wallet_tag_label = tag["label"]
                   #if this address has no tag, we query Graphsense to find the cluster it belongs to. We use API /entity to get the cluster data
                   if not wallet_tag_label: 
                       # Test address : 15G9wyGRDssFXsfwEm1ihdJs2xabVPDu68
                       req = requests.get(config["api"] + "/" + currency + "/addresses/" + Virtual_Asset_address + "/entity", headers={'Authorization': config["token"]})
                       address = req.json()
                       if "tags" in address:
                           entity_tags = address["tags"]
                           for entity_tag in entity_tags:
                               #we use source rather than label because while a cluster inherits the labels of its addresses, the source is within some of the tagged addresses.
                               if "source" in entity_tag:
                                   tag = entity_tag
                                   break
           except Exception as e:
               print(e)
               
        return tag

if __name__ == "__main__":
    print(GraphSense.get_details(sys.argv[1]))
