from maltego_trx.maltego import MaltegoTransform, UIM_PARTIAL


def set_maltego_transformation_error(
    responseMaltego: MaltegoTransform,
    currency: str,
    query_type: str,
    address: str,
    error: str,
):

    if "504 Bad Gateway" in error:
        responseMaltego.addUIMessage(
            "\nThere was a Graphsense server 504 Bad Gateway response while creating the results:\n"
            + query_type
            + " for "
            + currency
            + "\n",
            UIM_PARTIAL,
        )
    if "(404)" in error:
        responseMaltego.addUIMessage(
            "\nNothing found in " + currency + " for : " + str(address) + "\n",
            UIM_PARTIAL,
        )
    else:
        responseMaltego.addUIMessage(error, UIM_PARTIAL)
