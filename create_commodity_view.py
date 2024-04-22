"""
-------------------------------------------------------------------------------
File: create_commodity_view.py
Author: Mark E. Gilbert
Date: 2024-04-18: Converted from Notebook to srcipt file.
Update: 2024-04-20: Read in the view item metadata from an external file.
Description: Creates a new AGOL feature layer view from an existing hosted 
feature layer. The command line argument is the item ID for the hosted feature
layer. The external file, commodity_attrs.py, defines a dictionary for each
commodity that includes service, name, item title, and other item details. 
It also includes the list of fields that should be visible for the view. 
Processing includes updating the view item description page as well as setting 
delete protection and moving the view to a different folder.

Command example: pyton create_commodity_view.py d534e5eb24b749ba9efea678b5d9612e

TODOs
- Confirm the name of the 'move_to' folder.
- Ensure the snippet_template reads as you would like it.
- Ensure the description_template reads as you would like it
- Ensure the credits read as you would like it.
- Ensure the license information is correct for your data.

"""

# Imports
#
import arcgis
from arcgis.gis import GIS
from arcgis.features import FeatureLayerCollection
import sys
from commodity_attrs_DEV import commodity_meta

# Constants
#
move_to_folder = "AG Census"

snippet_template = "[REPLACE] in the United States at the county level as reported in the 2022 Census of Agriculture."

description_template = "<div>The <a href='https://www.nass.usda.gov/AgCensus/' target='_blank'>Census of Agriculture</a>, \
produced by the United States Department of Agriculture (USDA), provides a complete count of America's farms, ranches \
and the people who grow our food. The census is conducted every five years, most recently in 2022, and provides an in-depth \
look at the agricultural industry.</div><div><br /></div><div>This layer was produced from data obtained from the USDA \
<a href='https://www.nass.usda.gov/datasets/' target='_blank'>National Agriculture Statistics Service (NASS) Large \
Datasets</a> download page. The data were transformed and prepared for publishing using the Pivot Table tool geoprocessing \
tool in ArcGIS Pro and joined to county boundaries. The county boundaries are 2022 vintage and come from Living Atlas ACS \
2022 feature layers.</div><div><br /></div><div><b><u>Dataset Summary</u></b></div><div><b>Phenomenon Mapped</b>: \
2022 [REPLACE]</div><div><b>Coordinate System</b>: Web Mercator Auxiliary Sphere</div><div><b>Extent</b>: \
48 Contiguous United States, Alaska, and Hawaii</div><div><b>Source</b>: <a href='https://www.nass.usda.gov/index.php' \
target='_blank'>USDA National Agricultural Statistics Service</a></div><div><b>Publication Date</b>: 2022</div><div><br />\
</div><div><b><u>Attributes</u></b></div><div>Note that some values are suppressed as &quot;Withheld to avoid disclosing \
data for individual operations&quot;, &quot;Not applicable&quot;, or &quot;Less than half the rounding unit&quot;. These \
have been codded in the data as -999, -888, and -777 respectively.</div><div><ul><li> </li></ul></div><div></div><div>\
For data collection purposes in Alaska, one or more county equivalent entities (borough, census area, city, municipality) \
are included in an agriculture census area.</div>"

credits = "Esri, US Census Bureau, US Department of Agriculture"

license = "<img src='https://downloads.esri.com/blogs/arcgisonline/esrilogo_new.png' /> This work is licensed under \
the Esri Master License Agreement.<br /><div><a href='https://goto.arcgis.com/termsofuse/viewsummary' target='_blank'><b>\
View Summary</b></a> | <a href='https://goto.arcgis.com/termsofuse/viewtermsofuse' target='_blank'><b>View Terms of Use</b>\
</a></div>"


def main():

    # Get the HFL item ID from the command line
    #
    in_hfl_item_id = str(sys.argv[1])

    for commodity, meta in commodity_meta.items():

        print(f"Processing {commodity.title()} with hosted feature layer ID: {in_hfl_item_id}")

        view_name = meta['v_name']
        title = meta['v_title']
        snippet = snippet_template.replace("[REPLACE]", meta['snippet_lead'])
        description = description_template.replace("[REPLACE]", meta['phenom'])
        tags = meta['tags']
        visible_fields = meta['fields']


        # Log into ArcGIS Online
        # This command uses a previously saved local profile to connect to the GIS.
        # See https://developers.arcgis.com/python/guide/working-with-different-authentication-schemes/ for additional details
        #
        # Create a profile so I don't have to enter credentials after the first time
        #
        dest_org = GIS("https://arcgis.com", username="mgilbert_content", profile="mgilbert_content")
        print(f"\tSuccessfully logged in as: {dest_org.properties.user.username}")

        # Search for the source hosted feature layer
        #
        source_search = dest_org.content.search(query=in_hfl_item_id)[0] 
        source_flc = FeatureLayerCollection.fromitem(source_search)
        print(f"\tSource: {source_search.title}")

        # Create the view layer
        # Assumes the view name does not already exist
        #
        view_item = source_flc.manager.create_view(name=view_name)

        # Move to folder
        #
        mv_status = view_item.move(move_to_folder)
        print(f"\tView moved: {mv_status['success']}")

        # Update the title and other properties
        #
        view_item.update(item_properties=
                        {
                            'title': title,
                            'description': description,
                            'tags': tags,
                            'snippet': snippet,
                            'accessInformation': credits,
                            'licenseInfo': license
                        })

        print(f"\tView renamed to {title}")

        # Set delete protection
        #
        protect_res = view_item.protect(enable=True)
        print(f"\tDelete protection: {protect_res['success']}")

        # Turn off attributes not needed in the view

        # Get a list of fields from the view layer
        #
        view_flds = view_item.layers[0].properties.fields

        # Set only the fields we want to visible, also include OID
        #
        vis_flds = [
            {"name": f"{f.name}", "visible": True}
            if f.name in visible_fields
            or f.type == "esriFieldTypeOID"
            else {"name": f"{f.name}", "visible": False}
            for f in view_flds
        ]

        # Update the view definition
        #
        layer_def = {"fields": vis_flds}
        view_item.layers[0].manager.update_definition(layer_def)
        print(f"\tFeature layer view created\n\t ItemID : {view_item.id}\n\t URL:{view_item.url}")


if __name__ == '__main__':
    main()