"""
-------------------------------------------------------------------------------
File: ag_census_processing.py
Author: Mark E. Gilbert
Date: 2024-05-01: Created.
Description: End to end ag census processing. Begins by downloading the complete
datafile, extracts and loads into ArcGIS Pro, processess it by pivioting the data
and subsetting, cleans attribute names.

Command example: python ag_census_data_processing.py 2002 "county"

"""

# Imports
#
from arcgis.gis import GIS
from arcgis.features import FeatureLayerCollection
import arcpy
import sys
import os
import requests
import gzip
import shutil
import time

# Constants
#
# TODO: Update LOCAL_PATH and COMMODITY_DESC.
# TODO: FLD_MAP_TEMPLATE also needs to reflect the actual location of the downloaded file.
#
LOCAL_PATH = r'C:\Users\mark9020\Downloads'

COMMODITY_DESC = [
    'ALMONDS', 'ANIMAL TOTALS', 'BARLEY', 'CATTLE', 'CHICKENS', 'CORN', 'COTTON', 'CROP TOTALS', 
    'FARM OPERATIONS', 'GOVT PROGRAMS', 'GRAIN', 'GRAPES', 'HAY', 'HOGS', 'LABOR', 'MACHINERY TOTALS', 
    'MILK', 'PRODUCERS', 'RICE', 'SORGHUM', 'SOYBEANS', 'TRACTORS', 'TRUCKS', 'TURKEYS', 'WHEAT'
    ]

URL_TEMPLATE = r"https://www.nass.usda.gov/datasets/qs.census[VINTAGE].txt.gz"
FGDB_TEMPLATE = r"C:\Users\mark9020\Documents\ArcGIS\Projects\Ag Census\Ag Census [VINTAGE].gdb"

# TODO: Update the path to the source input file in fld_map to reflect the new file. 
#
FLD_MAP_TEMPLATE = r'SOURCE_DESC "SOURCE_DESC" true true false 60 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,SOURCE_DESC,0,7999;' \
        r'SECTOR_DESC "SECTOR_DESC" true true false 60 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,SECTOR_DESC,0,7999;' \
        r'GROUP_DESC "GROUP_DESC" true true false 80 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,GROUP_DESC,0,7999;' \
        r'COMMODITY_DESC "COMMODITY_DESC" true true false 80 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,COMMODITY_DESC,0,7999;' \
        r'CLASS_DESC "CLASS_DESC" true true false 180 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,CLASS_DESC,0,7999;' \
        r'PRODN_PRACTICE_DESC "PRODN_PRACTICE_DESC" true true false 180 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,PRODN_PRACTICE_DESC,0,7999;' \
        r'UTIL_PRACTICE_DESC "UTIL_PRACTICE_DESC" true true false 180 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,UTIL_PRACTICE_DESC,0,7999;' \
        r'STATISTICCAT_DESC "STATISTICCAT_DESC" true true false 80 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,STATISTICCAT_DESC,0,7999;' \
        r'UNIT_DESC "UNIT_DESC" true true false 60 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,UNIT_DESC,0,7999;' \
        r'SHORT_DESC "SHORT_DESC" true true false 512 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,SHORT_DESC,0,7999;' \
        r'DOMAIN_DESC "DOMAIN_DESC" true true false 256 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,DOMAIN_DESC,0,7999;' \
        r'DOMAINCAT_DESC "DOMAINCAT_DESC" true true false 512 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,DOMAINCAT_DESC,0,7999;' \
        r'AGG_LEVEL_DESC "AGG_LEVEL_DESC" true true false 40 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,AGG_LEVEL_DESC,0,7999;' \
        r'STATE_ANSI "STATE_ANSI" true true false 2 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,STATE_ANSI,-1,-1;' \
        r'STATE_FIPS_CODE "STATE_FIPS_CODE" true true false 2 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,STATE_FIPS_CODE,-1,-1;' \
        r'STATE_ALPHA "STATE_ALPHA" true true false 2 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,STATE_ALPHA,0,7999;' \
        r'STATE_NAME "STATE_NAME" true true false 30 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,STATE_NAME,0,7999;' \
        r'ASD_CODE "ASD_CODE" true true false 2 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,ASD_CODE,-1,-1;' \
        r'ASD_DESC "ASD_DESC" true true false 60 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,ASD_DESC,0,7999;' \
        r'COUNTY_ANSI "COUNTY_ANSI" true true false 3 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,COUNTY_ANSI,-1,-1;' \
        r'COUNTY_CODE "COUNTY_CODE" true true false 3 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,COUNTY_CODE,-1,-1;' \
        r'COUNTY_NAME "COUNTY_NAME" true true false 30 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,COUNTY_NAME,0,7999;' \
        r'REGION_DESC "REGION_DESC" true true false 80 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,REGION_DESC,0,7999;' \
        r'ZIP_5 "ZIP_5" true true false 5 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,ZIP_5,0,7999;' \
        r'WATERSHED_CODE "WATERSHED_CODE" true true false 8 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,WATERSHED_CODE,-1,-1;' \
        r'WATERSHED_DESC "WATERSHED_DESC" true true false 120 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,WATERSHED_DESC,0,7999;' \
        r'CONGR_DISTRICT_CODE "CONGR_DISTRICT_CODE" true true false 2 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,CONGR_DISTRICT_CODE,0,7999;' \
        r'COUNTRY_CODE "COUNTRY_CODE" true true false 4 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,COUNTRY_CODE,-1,-1;' \
        r'COUNTRY_NAME "COUNTRY_NAME" true true false 60 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,COUNTRY_NAME,0,7999;' \
        r'LOCATION_DESC "LOCATION_DESC" true true false 120 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,LOCATION_DESC,0,7999;' \
        r'YEAR "YEAR" true true false 4 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,YEAR,-1,-1;' \
        r'FREQ_DESC "FREQ_DESC" true true false 30 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,FREQ_DESC,0,7999;' \
        r'BEGIN_CODE "BEGIN_CODE" true true false 2 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,BEGIN_CODE,-1,-1;' \
        r'END_CODE "END_CODE" true true false 2 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,END_CODE,-1,-1;' \
        r'REFERENCE_PERIOD_DESC "REFERENCE_PERIOD_DESC" true true false 40 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,REFERENCE_PERIOD_DESC,0,7999;' \
        r'WEEK_ENDING "WEEK_ENDING" true true false 10 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,WEEK_ENDING,0,7999;' \
        r'LOAD_TIME "LOAD_TIME" true true false 8 Date 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,LOAD_TIME,-1,-1;' \
        r'VALUE "VALUE" true true false 24 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,VALUE,0,7999;' \
        r'CV_PCT "CV_%" true true false 7 String 0 0,First,#,C:\Users\mark9020\Downloads\qs.census[VINTAGE].txt,CV__,0,7999'

# Functions
#
def download_file(url, path):
    """
    Downloads a file from the given URL using HTTP and saves it locally.

    Args:
        url (str): The URL of the file to download.
        path (str): The local path to save the download file.

    Returns:
        str: The path to the downloaded file on the local system.
    """

    file_name = os.path.basename(url)
    response = requests.get(url)
    file_path = f"{path}/{file_name}"
    
    with open(file_path, "wb") as file:
        file.write(response.content)
    
    return file_path, file_name


def decompress_gz_file(file_path):
    """
    Decompresses a .gz file and returns the path to the uncompressed file.

    Args:
        file_path (str): The path to the .gz file.

    Returns:
        str: The path to the uncompressed file.
    """
    # Create the path for the uncompressed file
    uncompressed_file_path = file_path[:-3]

    # Open the .gz file and the uncompressed file
    with gzip.open(file_path, 'rb') as gz_file, open(uncompressed_file_path, 'wb') as uncompressed_file:
        # Copy the contents from the .gz file to the uncompressed file
        shutil.copyfileobj(gz_file, uncompressed_file)

    return uncompressed_file_path


def load_raw_data(in_file, out_name, fld_map):
    """
    Imports a text file into a table using arcpy using a custom field map.

    Args:
        in_file (str): The path to the text file.

    Returns:
        Result: The result of the import operation.
    """
    export_results = arcpy.conversion.ExportTable(in_file, out_name,
        field_mapping = fld_map
        )
    
    return export_results

def prepare_raw_data(in_table):
    """
    Prepare the raw text data into a functional FGDB table. This
    includes correcting FIPS codes, transforming str in numeric, and
    creating new fields where needed.

    Args:
        in_table (str): The name of the table to modify
    
    Returns:
        Results: The results of the operations.
    """
    sum_results_status = 0

    # Creates a new field called Supp_Code and uses CalculateField to
    # populate the field with a striped down code
    #
    print("\tCreating Supp_Code field...")
    try:
        supp_code_result = arcpy.management.CalculateField(
            in_table=in_table,
            field="Supp_Code",
            expression="convert_supp_code(!VALUE!)",
            expression_type="PYTHON3",
            code_block="""def convert_supp_code(in_value):
            if in_value in("(D)","(X)","(Z)"):
                rtn_text = in_value[1]
                return rtn_text""",
            field_type="TEXT",
            enforce_domains="NO_ENFORCE_DOMAINS"
            )
        
        if supp_code_result.status == 4:
            print(f"\tSuccess: created Supp_Code field")
        else:
            print(f"\tError: creating Supp_Code field {supp_code_result.status}")
        

    except arcpy.ExecuteError:
        print(arcpy.GetMessages())
    
    sum_results_status += supp_code_result.status

    # Creates a new field called VALUE_Num and uses CalculateField to
    # populate the field.
    #
    print("\tCreating VALUE_Num field...")
    try:
        value_num_result = arcpy.management.CalculateField(
            in_table=in_table,
            field="VALUE_Num",
            expression="create_value_num(!VALUE!)",
            expression_type="PYTHON3",
            code_block="""def create_value_num(in_value):
            match in_value:
                case "(D)":
                    return -999
                case "(X)":
                    return -888
                case "(Z)":
                    return -777
                case _:
                    return in_value""",
            field_type="DOUBLE",
            enforce_domains="NO_ENFORCE_DOMAINS"
            )
        
        if value_num_result.status == 4:
            print(f"\tSuccess: created VALUE_Num field")
        else:
            print(f"\tError: creating VALUE_Num field {value_num_result.status}")

    except arcpy.ExecuteError:
        print(arcpy.GetMessage())
    
    sum_results_status += value_num_result.status

    # Correct the state FIPS code field by pre-pending a zero to
    # any value that only has a single character.
    #
    print("\tCorrecting state FIPS code...")
    try:
        st_ansi_result = arcpy.management.CalculateField(
            in_table=in_table,
            field="STATE_ANSI",
            expression="correct_st_fips(!STATE_ANSI!)",
            expression_type="PYTHON3",
            code_block="""def correct_st_fips(in_value):
            match len(in_value):
                case 1:
                    return "0" + in_value
                case _:
                    return in_value""",
            field_type="TEXT",
            enforce_domains="NO_ENFORCE_DOMAINS"
            )

        st_fips_result = arcpy.management.CalculateField(
                in_table=in_table,
                field="STATE_FIPS_CODE",
                expression="!STATE_ANSI!",
                expression_type="PYTHON3",
                code_block="",
                field_type="TEXT",
                enforce_domains="NO_ENFORCE_DOMAINS"
                )
        
        if (st_ansi_result.status == 4 and st_fips_result.status == 4):
            print(f"\tSuccess: corrected state FIPS code")
        else:
            print(f"\tError: correcting state FIPS code st_ansi_result {st_ansi_result.status} st_fips_result {st_fips_result.status}")

    except arcpy.ExecuteError:
        print(arcpy.GetMessage())

    sum_results_status += st_ansi_result.status + st_fips_result.status

    # Correct the county FIPS code field by pre-pending one or two
    # zeros to any value that only has one or two characters. County FIPS
    # should be three characters.
    #
    print("\tCorrecting county FIPS code...")
    try:
        cnty_code_result = arcpy.management.CalculateField(
            in_table=in_table,
            field="COUNTY_CODE",
            expression="add_leading_zeros(!COUNTY_CODE!)",
            expression_type="PYTHON3",
            code_block="""def add_leading_zeros(in_value):
            match len(in_value):
                case 1:
                    return "00" + in_value
                case 2:
                    return "0" + in_value
                case _:
                    return in_value""",
            field_type="TEXT",
            enforce_domains="NO_ENFORCE_DOMAINS"
            )

        cnty_ansi_result = arcpy.management.CalculateField(
                in_table=in_table,
                field="COUNTY_ANSI",
                expression="!COUNTY_CODE!",
                expression_type="PYTHON3",
                code_block="",
                field_type="TEXT",
                enforce_domains="NO_ENFORCE_DOMAINS"
                )
        
        if (cnty_code_result.status == 4 and cnty_ansi_result.status == 4):
            print(f"\tSuccess: corrected county FIPS code")
        else:
            print(f"\tError: correcting county FIPS code cnty_code_result {cnty_code_result.status} cnty_ansi_result {cnty_ansi_result.status}")

    except arcpy.ExecuteError:
        print(arcpy.GetMessage())

    sum_results_status += cnty_code_result.status + cnty_ansi_result.status

    # Creates a new field called GEOID and uses CalculateField to
    # populate it with state and county FIPS.
    #
    print("\tCreating GEOID field...")
    try:
        geoid_result = arcpy.management.CalculateField(
            in_table=in_table,
            field="GEOID",
            expression="create_geoid(!STATE_FIPS_CODE!, !COUNTY_CODE!, !AGG_LEVEL_DESC!)",
            expression_type="PYTHON3",
            code_block="""def create_geoid(st_fips, county_fips, agg_level):
            if agg_level == "COUNTY":
                return st_fips + county_fips
            else:
                return None""",
            field_type="TEXT",
            enforce_domains="NO_ENFORCE_DOMAINS"
            )
        
        if geoid_result.status == 4:
            print(f"\tSuccess: created GEOID field")
        else:
            print(f"\tError: creating GEOID field {geoid_result.status}")
            
    except arcpy.ExecuteError:
        print(arcpy.GetMessage())
    
    sum_results_status += geoid_result.status
    
    # Creates a new field called Long_Desc and uses CalculateField to
    # populate it with SHORT_DESC, DOMAIN_DESC, DOMAINCAT_DESC separated
    # by pipe with spaces.
    #
    print("\tCreating Long_Desc field...")
    try:
        long_desc_result = arcpy.management.CalculateField(
            in_table=in_table,
            field="Long_Desc",
            expression='!SHORT_DESC! + "_" + !DOMAIN_DESC! + "_" + !DOMAINCAT_DESC!',
            expression_type="PYTHON3",
            code_block="",
            field_type="TEXT",
            enforce_domains="NO_ENFORCE_DOMAINS"
            )
        
        if long_desc_result.status == 4:
            print(f"\tSuccess: created GEOID field")
        else:
            print(f"\tError: creating GEOID field {long_desc_result.status}")
            
    except arcpy.ExecuteError:
        print(arcpy.GetMessage())
    
    sum_results_status += long_desc_result.status
    
    return sum_results_status


def subset_and_pivot(in_table, geo_type, vintage, commodity_list):
    """
    Subset the source data by limiting it to a single geograpy type (county, state, national).
    Then use the Pivot Table GP tool to transform the rows into columns.

    Args:
        in_table (str): The name of the table to modify
        geo_type (str): The name of the geography level to filter the data
        vintage (str): The year of the census data
        commodity_list (str): A list of strings used for filtering
    
    Returns:
        Results: The results of the operations.
    """
    sel_clause = f"AGG_LEVEL_DESC = '{geo_type}' And COMMODITY_DESC IN {*commodity_list,}"
    out_table = f"ag_pivot_{vintage}_county_sel_cmdty"
    
    try:            
        src_selection = arcpy.management.SelectLayerByAttribute(in_table, where_clause=sel_clause)
        
    except arcpy.ExecuteError:
        print(arcpy.GetMessage())
        
    if src_selection.status == 4:
        print(f"\t{src_selection[1]} records selected...")
    else:
        print(f"\tError: select result {src_selection.status}")

    try:
        pivot_rslt = arcpy.management.PivotTable(in_table=src_selection[0],
                                                 fields="GEOID",
                                                 pivot_field="Long_Desc",
                                                 value_field="VALUE_Num",
                                                 out_table=out_table
                                                )
    except arcpy.ExecuteError:
        print(arcpy.GetMessage())
        
    return pivot_rslt


def main():
    """
    Any additional information.

    """
    print("Begin processing...")
    begin_time = time.time()

    # Get command line parameters
    #
    census_vintage = str(sys.argv[1])
    geo_name = str(sys.argv[2]).upper()

    download_url = URL_TEMPLATE.replace("[VINTAGE]", census_vintage)
    fgdb_path = FGDB_TEMPLATE.replace("[VINTAGE]", census_vintage)
    field_map = FLD_MAP_TEMPLATE.replace("[VINTAGE]", census_vintage)

    print(f"\tDownloading {download_url} to {LOCAL_PATH} to process the {geo_name} level..")
 
    if not os.path.exists(fgdb_path):
        arcpy.management.CreateFileGDB(os.path.dirname((fgdb_path)), os.path.basename(fgdb_path))

    arcpy.env.workspace = fgdb_path
    arcpy.env.overwriteOutput = True

   # Download the current ag census data file
    #
    print("\tDownloading file...")
    dl_file_path, dl_file_name = download_file(download_url, LOCAL_PATH)
    print(f"\t{dl_file_name} downloaded from {download_url}")

    # Decompress data file
    #
    print("\tDecompressiong file...")
    file_decomp = decompress_gz_file(dl_file_path)
    print(f"\tData file decompressed to {file_decomp}")

    # Load raw data file into Pro
    #
    print("\tLoading census file into FGDB...")
    table_name = f"ag_census_{census_vintage}_source"
    load_results = load_raw_data(file_decomp, table_name, field_map)

    if load_results.status == 4:
        print(f"\tSuccess: data loaded into ArcGIS Pro")
    else:
        print(f"\tError: data load status {load_results.status}")

    # Process the imported raw data file
    #
    print(f"\tProcessing the raw data file...")
    rtn_process = prepare_raw_data(table_name)

    if rtn_process == 32:
        print(f"\tSuccess: data processed with code {rtn_process}")
    else:
        print(f"\tError: something went wrong rtn_process {rtn_process}")

    # Subset the source dataset by geography type and run Pivot Table
    # Pass the list of commodities to include
    #
    print(f"\tSubsetting data and pivoting...")

    rtn_pivot = subset_and_pivot(table_name, geo_name, census_vintage, COMMODITY_DESC)
    if rtn_pivot.status == 4:
        print(f"\tSucces: subset and pivot completed")
    else:
        print(f"\tError: {rtn_pivot.status}")
        
    elapsed_time = time.time() - begin_time
    print(f"Processing complete.\nOverall Elapsed time: {elapsed_time:0,.2f} seconds]")


if __name__ == '__main__':
    main()