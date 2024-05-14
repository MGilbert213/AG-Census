"""
-------------------------------------------------------------------------------
File: update_FC_field_names.py
Author: Mark E. Gilbert
Date: 2024-04-16: Converted from Notebook to srcipt file.
Description: This script is used to update the original feature class attribute names to something shorter
since publishing using the Python API does not support the larger character length names. The attribute 
alias and other properties get updated using Lisa B's Python script in a later step.

Command example: python update_FC_field_names.py
                        "C:\\path_to_workspace\\Ag Census 2022.gdb"
                        ag_pivot_2022_county_sel_cmdty
                        C:\\path_to_file\\UPDATE_ag_pivot_2022_county_sel_cmdty_FC.xlsx

TODOs:
- Update path_to_file for the data file
- Update path_to_workspace for the workspace

"""

# Imports
#
import arcpy
import pandas as pd
import time
import sys

def main():
    print("Begin processing")

    begin_time = time.time()

    # Get command line parameters
    #
    fgdb_path = str(sys.argv[1])
    in_fc_name = str(sys.argv[2])
    xref_xlsx = str(sys.argv[3])

    arcpy.env.workspace = fgdb_path

    # Just update the attribute name property and leave alias. Alias will be updated along with long description and
    # other AGOl properties using Lisa B's Python script.
    #
    src_name_data = pd.read_excel(xref_xlsx, "Update")

    src_name_dict = src_name_data.set_index("Source_Name").T.to_dict("list")

    fld_name_dict = {}

    for fld in arcpy.ListFields(in_fc_name):
        if fld.name in src_name_dict:
            print(f"\tUpdating {fld.name} to {src_name_dict[fld.name][0]}")
            try:
                arcpy.management.AlterField(in_fc_name, fld.name, src_name_dict[fld.name][0])
                
            except arcpy.ExecuteError:
                print(arcpy.GetMessages())
                
        else:
            print("\tNot found")
 
    elapsed_time = time.time() - begin_time
    print(f"Processing complete.\nOverall Elapsed time: {elapsed_time:0,.2f} seconds]")


if __name__ == "__main__":
    main()