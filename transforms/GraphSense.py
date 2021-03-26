from maltego_trx.entities import Phrase

from maltego_trx.maltego import UIM_PARTIAL, UIM_FATAL
from maltego_trx.transform import DiscoverableTransform
import sys
import requests
import json


class GraphSense(DiscoverableTransform):
    """
    Lookup the name associated with a bitcoin address.
    """

    @classmethod
    def create_entities(cls, request, response):
        bitcoin_address = request.Value.strip()
        #print("Bitcoin : " + bitcoin_address)
        #entity_note = ""
        #graphsense_tag = ""
        
        try:
            graphsense_tag = cls.get_details(bitcoin_address)
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
                response.addUIMessage("The Bitcoin address was not found")
        except Exception as e:
            print(e)
            response.addUIMessage("An error occurred", messageType=UIM_PARTIAL)

    @staticmethod
    def load_config():
        with open("config.json") as json_data_file:
            config = json.load(json_data_file)
        return config

    @staticmethod
    def get_details(bitcoin_address):
        wallet_tag_label = ""
        req = ""
        tag = ""

        config = GraphSense.load_config()
        if "token" not in config or "currency" not in config or "api" not in config:
            return {"error": {"message":"Can not load data from config.json file"}}
        if config["token"] == "YOUR TOKEN":
            return {"error": {"message":"No GraphSense token have been set in the config.json file"}}

        try:
            req = requests.get(config["api"] + "/" + config["currency"] + "/addresses/" + bitcoin_address, headers={'Authorization': config["token"]})
            address = req.json()
            if "tags" in address:
                tags = address["tags"]
                if len(tags) > 0:
                    tag = tags[0]
                    if "label" in tag:
                        wallet_tag_label = tag["label"]
                if not wallet_tag_label: #if this address has no tag, we query Graphsense to find the cluster it belongs to. We use API /entity to get the cluster data
                    req = requests.get(config["api"] + "/" + config["currency"] + "/addresses/" + bitcoin_address + "/entity", headers={'Authorization': config["token"]})
                    address = req.json()
                    if "tags" in address:
                        entity_tags = address["tags"]
                        #tag = ""
                        if len(entity_tags) > 0:
                            entity_tag = entity_tags[0] #by default
                            i=0
                            go_again = True
                            while go_again and (i < len(entity_tags)):
                                if "source" in entity_tag: #we use source rather than label because while a cluster inherits the labels of its addresses, the source is within some of the tagged addresses.
                                    tag = entity_tags[i]
                                    go_again = False
                                i = i + 1
        except Exception as e:
            print(e)
        return tag

if __name__ == "__main__":
    print(GraphSense.get_details(sys.argv[1]))
