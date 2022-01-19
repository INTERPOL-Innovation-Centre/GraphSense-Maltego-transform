from maltego_trx.maltego import MaltegoMsg, MaltegoTransform, UIM_FATAL
from maltego_trx.transform import DiscoverableTransform

from extensions import registry

from api.utils import create_entity_with_details, get_currency, get_address_details, get_entity_details, get_currency_from_entity_details

@registry.register_transform(
	display_name='To Tags',
	input_entity='maltego.Cryptocurrency',
	description='Returns known attribution tags',
	output_entities=['maltego.Cryptocurrency']
)

class ToTags(DiscoverableTransform):
	"""
	Lookup the attribution tags associated with a Virtual Asset and the entity (cluster) it belongs to.
	"""
	
	@classmethod
	def create_entities(cls, request: MaltegoMsg, responseMaltego: MaltegoTransform):
		
		query_type = "tags"
		
		currencies=[]
		entity_details = request.Properties
		if 'cryptocurrency.wallet.name' in entity_details: # If so, we are looking for tags in a cluster
			query_type = "entity_tags"
			currencies.append(entity_details['currency'])
			address = int(entity_details['cluster_ID'])
		else :
			if 'properties.cryptocurrencyaddress' in entity_details: #Else, we are looking for tags on a specific address
				address = str(entity_details['properties.cryptocurrencyaddress'])
				currencies += get_currency(address) # We use regex to check what Cryptocurrency this is. This could return BTC and BCH since they are similar.
			else:
				currencies = get_currency_from_entity_details(entity_details) # We use the input entity properties to find what cryptocurrency this is. This avoids duplicates.
#				address = entity_details['address']
# 			if address[:2] == "bc": #beech32 BTC addresses include "bc" at the begining, no need to check if it is another currency (like bch).
# 				#address = address[2:] Not needed because Graphsense can handle bcxxx addresses.
# 				currencies = ["btc"] #we know this is BTC, no need to check for BCH or other currencies.
# 			#else:

		for currency in currencies:
			if (query_type == "tags"):
				results = get_address_details(currency,address)
			else:
				results = get_entity_details(currency,address)
			
			if results[1] :
				if (results[1].find("504")):# the Graphsense server is missing a </hr> in its HTTP504 response page which bugs Maltego hence the below. handling...
					responseMaltego.addUIMessage("\nThere was a Graphsense server 504 Bad Gateway response running the query " + query_type + " for " + currency + "\n",UIM_FATAL)
				else:
					responseMaltego.addUIMessage(results[1],UIM_FATAL)
				return
			else:
				responses = create_entity_with_details(results[0],currency,query_type, responseMaltego)
				if responses[1]:
					if (results[1].find("504")):
						responseMaltego.addUIMessage("\nThere was a Graphsense server 504 Bad Gateway response while creating the results:\n" + " for " + currency + "\n",UIM_FATAL)
					else:
						responseMaltego.addUIMessage(results[1],UIM_FATAL)
		return


if __name__ == "__main__":
	create_entities(sys.argv[1])