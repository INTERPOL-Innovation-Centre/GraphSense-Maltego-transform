from maltego_trx.maltego import MaltegoMsg, MaltegoTransform, UIM_FATAL
from maltego_trx.transform import DiscoverableTransform

from extensions import registry

from api.utils import create_entity_with_details, get_currency, get_address_details, get_entity_details

@registry.register_transform(
	display_name='To Details',
	input_entity='maltego.Cryptocurrency',
	description='Returns details of a cryptocurerncy address.',
	output_entities=['maltego.Cryptocurrency']
)

class ToDetails(DiscoverableTransform):
	"""
	Lookup for all details associated with a Virtual Asset (balance, total in and out, date last and first Tx...)
	"""
	
	@classmethod
	def create_entities(cls, request: MaltegoMsg, responseMaltego: MaltegoTransform):
		
		query_type = "details"

		currencies=[]
		entity_details = request.Properties
		if 'cryptocurrency.wallet.name' in entity_details: # this means the source entity is a cluster (Wallet) and not a cryptocurrency address
			address = entity_details['cryptocurrency.wallet.name']
			currency = entity_details['currency']
			results = get_entity_details(currency,int(address))
			if ('1' in results):
				error = "Got an error getting the cluster details: " + results[1]
				return "", error
			else:
				results = results[0]
			#currency = "cluster"
			entity = create_entity_with_details(results,currency,query_type,responseMaltego)
			if entity != "" :
				#print(entity)
				return entity
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

		for currency in currencies:
			results = get_address_details(currency,address)
			if results[1] :
				if "504 Bad Gateway" in results[1]:# the Graphsense server is missing a </hr> in its HTTP504 response page which bugs Maltego hence the below. handling...
					responseMaltego.addUIMessage("\nThere was a Graphsense server 504 Bad Gateway response running the query " + query_type + " for " + currency + "\n",UIM_FATAL)
				else:
					responseMaltego.addUIMessage(results[1],UIM_FATAL)
				return
			else:
				responses = create_entity_with_details(results[0],currency,query_type, responseMaltego)
				if responses[1]:
					if "504 Bad Gateway" in responses[1]:
						responseMaltego.addUIMessage("\nThere was a Graphsense server 504 Bad Gateway response while creating the results:\n" + " for " + currency + "\n",UIM_FATAL)
					else:
						responseMaltego.addUIMessage(results[1],UIM_FATAL)
		return

if __name__ == "__main__":
	create_entities(sys.argv[1])