""" read in the property concentration spreadsheet and create a dictionary identifying
props by state, county, city, address """

from pathlib import Path
import pandas as pd
from bekutils import clean_field

addr_xls = Path("/Users/Denise/Library/CloudStorage/Dropbox/Postcard " \
           "Files/InputFiles/ROVCleaverAddressRemoveList.xlsx").expanduser()

df = pd.read_excel(addr_xls, sheet_name="Addresses", header=0, )
df.columns = [str(col).lower() for col in df.columns]
df.fillna("", inplace=True)

addr_concentration_dict= dict([
    ((state, city, address),{'desc': desc, 'remove': remove})
    for state, city, address, desc, remove
    in zip(df['state'].apply(lambda x: clean_field(x)),
           df['city'].apply(lambda x: clean_field(x)),
           df['address'].apply(lambda x: clean_field(x)),
           df['desc'].str.strip(),
           df['remove'].str.strip()
          )
    ])

def conc_addr(concentration_dict: dict, state: str | None = None, city: str | None = None, address: str | None = None) -> bool:
    """Check whether a state/city/address combination is in the concentration dictionary.

    State, city, and address are cleaned using the 'clean_field' function
    before lookup.

    Args:
        concentration_dict: Dictionary mapping (state, city, address) tuples
            to concentration metadata.
        state: State code or name.
        city: City name.
        address: Street address.

    Returns:
        True if the cleaned address is found in concentration_dict,
        False otherwise.
    """

    from bekutils import clean_field

    concentrated = (True if (clean_field(state), clean_field(city), clean_field(address)) in
                             concentration_dict else False)
    return concentrated


def conc_addr_desc(concentration_dict: dict, state: str | None = None, city: str | None = None, address: str | None = None) -> str:
    """Return the description for a concentrated address entry.

    State, city, and address are cleaned using the 'clean_field' function
    before lookup.

    Args:
        concentration_dict: Dictionary mapping (state, city, address) tuples
            to concentration metadata.
        state: State code or name.
        city: City name.
        address: Street address.

    Returns:
        The 'desc' string for the matching address entry, or an empty string
        if not found in concentration_dict.
    """

    from bekutils import clean_field

    desc = concentration_dict.get((clean_field(state), clean_field(city),
                                               clean_field(address)), {'desc': "", 'remove': ""})['desc']
    return desc

def conc_addr_remove_desc(concentration_dict: dict, state: str | None = None, city: str | None = None, address: str | None = None) -> str:
    """Return the removal description for a concentrated address entry.

    State, city, and address are cleaned using the 'clean_field' function
    before lookup.

    Args:
        concentration_dict: Dictionary mapping (state, city, address) tuples
            to concentration metadata.
        state: State code or name.
        city: City name.
        address: Street address.

    Returns:
        The 'remove' string for the matching address entry, or an empty string
        if not found in concentration_dict.
    """

    from bekutils import clean_field

    desc = concentration_dict.get((clean_field(state), clean_field(city),
                                               clean_field(address)), {'desc': "", 'remove': ""})['remove']
    return desc

print(f"{ conc_addr_desc(addr_concentration_dict,'al','selma','11bellrd')=}")
print(f"{ conc_addr_remove_desc(addr_concentration_dict,'al','selma','11bellrd')=}")
print(f"{ conc_addr_desc(addr_concentration_dict,'alx','selma','11bellrd')=}")
print(f"{ conc_addr_remove_desc(addr_concentration_dict,'alx','selma','11bellrd')=}")
print(f"{ conc_addr_desc(addr_concentration_dict,'al','phenixcity','1839leeroad208apt208')=}")
print(f"{ conc_addr_remove_desc(addr_concentration_dict,'al','phenixcity','1839leeroad208apt208')=}")

a=1
