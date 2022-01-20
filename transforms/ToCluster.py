from maltego_trx.maltego import MaltegoMsg, MaltegoTransform, UIM_INFORM
from maltego_trx.transform import DiscoverableTransform

from extensions import registry

from api.utils import create_entity_with_details, get_currency_from_entity_details, get_address_details

@registry.register_transform(
	display_name='To Cluster',
	input_entity='maltego.Cryptocurrency',
	description='Returns the cluster details to which the address belongs.',
	output_entities=['maltego.Cryptocurrency']
)

class ToCluster(DiscoverableTransform):
	"""
	Lookup for the cluster (Entity ID) associated with a Virtual Asset
	"""
	
	@classmethod
	def create_entities(cls, request: MaltegoMsg, responseMaltego: MaltegoTransform):
		
		query_type = "cluster"

		entity_details = request.Properties
		if 'properties.cryptocurrencyaddress' in entity_details:
			address = entity_details['properties.cryptocurrencyaddress']
		else:
			address = entity_details['address']
		if address[:2] == "bc": #beech32 BTC addresses include "bc" at the begining, we want to remove that.
			#address = address[2:] Not needed because Graphsense can handle bcxxx addresses.
			currencies = ["btc"] #we know this is BTC, no need to check for BCH or other currencies.
		else:
			currencies = get_currency_from_entity_details(entity_details) # We use regex to check what Cryptocurrency this is. This could return BTC and BCH since they are similar.
			if currencies[1]:
				responseMaltego.addUIMessage("\n" + currencies[1] + "\n",UIM_INFORM)
				return
			currencies = currencies[:1]
			address = entity_details['properties.cryptocurrencyaddress']
				
		for currency in currencies:
			results = get_address_details(currency,address)
			if results[1] :
				if "504 Bad Gateway" in results[1]:# the Graphsense server is missing a </hr> in its HTTP504 response page which bugs Maltego hence the below. handling...
					responseMaltego.addUIMessage("\nThere was a Graphsense server 504 Bad Gateway response running the query " + query_type + " for " + currency + "\n",UIM_INFORM)
				if "(404)" in results[1]:
					responseMaltego.addUIMessage("\nNothing found in " + currency + " for : " + str(address) + "\n",UIM_INFORM)
				else:
					responseMaltego.addUIMessage(results[1],UIM_INFORM)
				return
			else:
				responses = create_entity_with_details(results[0],currency,query_type, responseMaltego)
				if responses[1]:
					if "504 Bad Gateway" in responses[1]:
						responseMaltego.addUIMessage("\nThere was a Graphsense server 504 Bad Gateway response while creating the results:\n" + " for " + currency + "\n",UIM_INFORM)
					if "(404)" in responses[1]:
						responseMaltego.addUIMessage("\nNothing found in " + currency + " for : " + str(address) + "\n",UIM_INFORM)
					else:
						responseMaltego.addUIMessage(responses[1],UIM_INFORM)
		return

if __name__ == "__main__":
	create_entities(sys.argv[1])