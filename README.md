# Census of Agriculture 2022 #
These are the script files I used to prepare and upload Ag census data from the USDA. The raw data were processed in ArcGIS Pro several Python scripts were used to prepare and publish the data to AGOL. 

The other script was used, along with the data file, to create views from the hosted feature layer; one view for each commodity of interest.

## What is here? ##
There are several files in this repository explained below.

* ag_census_data_processing.py: Main data processing script.
* update_FC_field_names.py: Make updates to the hosted feature layer field name aliases and long descriptions. Requires the Excel spreadsheet as input.
* UPDATE_ag_pivot_2022_county_sel_cmdty_FC.xlsx: Used to map the new aliases and long descriptions to the layer.
* create_commodity_view.py: Creates a new view based on the data defined in the commodity_attrs.py file.
* commodity_attrs.py: Defines the commodities and fields for the new view.
