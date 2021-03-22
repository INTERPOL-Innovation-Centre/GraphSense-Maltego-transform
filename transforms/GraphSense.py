from maltego_trx.entities import Phrase

from maltego_trx.maltego import UIM_PARTIAL
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
        #GraphSenseTag = ""
        
        try:
            GraphSenseTag = cls.get_details(bitcoin_address)
            if GraphSenseTag:
                if "label" in GraphSenseTag:
                    entity = response.addEntity(Phrase, str(GraphSenseTag["label"]))
                    entity.setLinkLabel("To tags [GraphSense]")
                    entity.setType("maltego.CryptocurrencyOwner")
                    if "category" in GraphSenseTag:
                        entity.addProperty("OwnerType", "loose", str(GraphSenseTag["category"]))
                    if "source" in GraphSenseTag:
                        entity_note = "Source : " + str(GraphSenseTag["source"] + "\n")
                    if "abuse" in GraphSenseTag:
                        entity_note = str(entity_note) + "Abuse : " + str(GraphSenseTag["abuse"])
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

        config = GraphSense.load_config()
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
                    tag = ""
                    if len(entity_tags) > 0:
                        entity_tag = entity_tags[0] #by default
                        i=0
                        go_again = True
                        while go_again and i < len(tags):
                            if "source" in entity_tag: #we use source rather than label because while a cluster inherits the labels of its addresses, the source is within some of the tagged addresses.
                                entity_tag = entity_tags[i]
                                go_again = False
                            i = i + 1
        except Exception as e:
            print(e)
        return tag

if __name__ == "__main__":
    print(GraphSense.get_details(sys.argv[1]))
