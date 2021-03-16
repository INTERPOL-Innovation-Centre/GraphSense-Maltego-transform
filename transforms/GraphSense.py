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

        try:
            wallet_name = cls.get_name(bitcoin_address)
            if wallet_name:
                response.addEntity(Phrase, wallet_name)
            else:
                response.addUIMessage("The Bitcoin address was not found")
        except:
            response.addUIMessage("An error occurred.", messageType=UIM_PARTIAL)

    @staticmethod
    def load_config():
        with open("config.json") as json_data_file:
            config = json.load(json_data_file)
        return config

    @staticmethod
    def get_name(bitcoin_address):
        wallet_name = ""
        config = GraphSense.load_config()
        try:
            req = requests.get(config["api"] + "/" + config["currency"] + "/addresses/" + bitcoin_address, headers={'Authorization': config["token"]})
            address = req.json()
            if "tags" in address:
                tags = address["tags"]
                if len(tags) > 0:
                    tag = tags[0]
                    if "label" in tag:
                        wallet_name = tag["label"]
            if not wallet_name:
                req = requests.get(config["api"] + "/" + config["currency"] + "/addresses/" + bitcoin_address + "/entity", headers={'Authorization': config["token"]})
                address = req.json()
                if "tags" in address:
                    tags = address["tags"]
                    if len(tags) > 0:
                        tag = tags[0]
                        if "label" in tag:
                            wallet_name = tag["label"]
        except Exception as e:
            print(e)
        return wallet_name

if __name__ == "__main__":
    print(GraphSense.get_names(sys.argv[1]))
