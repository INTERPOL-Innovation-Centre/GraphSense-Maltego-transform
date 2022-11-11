from maltego_trx.maltego import MaltegoMsg, MaltegoTransform, UIM_INFORM
from maltego_trx.transform import DiscoverableTransform

from extensions import registry

from api.utils import create_entity_with_details, get_currency_from_entity_details, get_address_details, get_entity_details

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
		
		entity_details = request.Properties
		if 'cryptocurrency.wallet.name' in entity_details: # this means the source entity is a cluster (Wallet) and not a cryptocurrency address
			address = int(entity_details['cryptocurrency.wallet.name'])
			currencies = [str(entity_details['currency'])] #if it is a cluster the currency is known
		#if 'properties.cryptocurrencyaddress' in entity_details: #Else, we are looking for tags on a specific address
			#address = entity_details['properties.cryptocurrencyaddress']
		else:
			if "currency" in entity_details: #if a currency is already specified in the details, we use that currency and only that one. Else, we try to figure out what currency this could be and check all.
				currencies = [entity_details['currency']]
			else:
				currencies = get_currency_from_entity_details(request.Properties) # We use regex to check what Cryptocurrency this is. This could return BTC and BCH since they are similar.
				if currencies[1]:
					responseMaltego.addUIMessage("\n" + currencies[1] + "\n",UIM_INFORM)
					return
				currencies = currencies[0]
			address = entity_details['properties.cryptocurrencyaddress']

		for currency in currencies:	
			if 'cryptocurrency.wallet.name' in entity_details:
				results = get_entity_details(currency,address)
			else:
				results = get_address_details(currency,address)
			if results[2] :
				if "504 Bad Gateway" in results[2]:# the Graphsense server is missing a </hr> in its HTTP504 response page which bugs Maltego hence the below. handling...
					responseMaltego.addUIMessage("\nThere was a Graphsense server 504 Bad Gateway response running the query " + query_type + " for " + currency + "\n",UIM_INFORM)
				if "(404)" in results[2]:
					responseMaltego.addUIMessage("\nNothing found in " + currency + " for : " + str(address) + "\n",UIM_INFORM)
				else:
					responseMaltego.addUIMessage("There was an unknown error: " + results[2] + "\n",UIM_INFORM)
				#return
			else:
				responses = create_entity_with_details(results,currency,query_type,responseMaltego)
				if responses[1]:
					if "504 Bad Gateway" in responses[1]:
						responseMaltego.addUIMessage("\nThere was a Graphsense server 504 Bad Gateway response while creating the results:\n" + " for " + currency + "\n",UIM_INFORM)
					if "(404)" in responses[1]:
						responseMaltego.addUIMessage("\nNothing found in " + currency + " for : " + str(address) + "\n",UIM_INFORM)
					else:
						responseMaltego.addUIMessage("There was an unknown error: " + responses[1] + "\n",UIM_INFORM)
		return

if __name__ == "__main__":
	create_entities(sys.argv[1])