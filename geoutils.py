# geoutils.py

# library containing utilities to help with the handling and manipulation of
# geographical boundary data from Statistics Canada.

import pathlib, numpy as np, pandas as pd, geopandas as gpd, constraint as csp


# Statscan boundary data names for provinces and subidvisions
STATCAN_PR = "lpr_000b16a_e.zip"
STATCAN_CSD = "lcsd000b16a_e.zip"


def to_geojson(filename, filters={}, color=None):
    """ 
    Convert statcan boundary data to a geojson file. When `filters` is not empty, filter the data.
    When `color_col` is set, add region coloring using Graph coloring via CSP
    
    Parameters
    ----------
    filename : str
        the name of the .zip file to be parsed
    
    filters : dict of str
        key-value pairs such that the key is a valid Statcan attribute and the value is value to filter by.
        
    color : bool 
        whether or not add region coloring based on 5-color graph coloring. 
    """
    path = pathlib.Path(filename)
    df = gpd.read_file(f"zip://{path}")
    
    # parse data based on the given filters
    for key in filters:
        df = df.loc[df[key] == filters[key]]
    
    # add regional coloring based on the graph coloring problem
    if color:
        col = get_id_col(df)
        if not col:
            print("Error: No unique UID found: region coloring skipped.")
        else:
            color_map = color_regions(df, col, 5)
            df["COLOR"] = -1
            for node in color_map:
                df.loc[df[col] == node, "COLOR"] = color_map[node]
    
    # convert coordinate system from NAD83 used by statcan, to EPSG:4326 used in GPS
    df = df.to_crs("EPSG:4326")
    
    # write to output to geojson file
    df.to_file(path.stem + ".json", driver="GeoJSON")


def get_id_col(df):
    """ Get the UID column of the given statcan data. if no unique UID is found, return None
    
    Parameters
    ----------
    df : pandas.DataFrame
        the data to perform the action on
        
    Returns
    -------
    str or None
    """
    uids = df.filter(regex='.*UID$', axis=1)
    for uid in uids:
        if len(df[uid].unique()) == len(df[uid]):
            return uid
    return None


def color_regions(df, col, num_colors):
    """
    Color a graph using CSP.
    
    Parameters
    ----------
    df : geopandas.GeoDataFrame
        a dataframe containing geographic data.
        
    col : str
        the name of column containing unique values for reach row
    
    num_colors : int
        the number of colors to be used. domain = [0, `num_colors`)
    
    Returns
    -------
    dict of int
        key-value pairs where the key is a node and the value is the color
    """
    problem = csp.Problem()
    domain = range(num_colors)
    
    # create adjacency matrix of the graph, G(V,E), such that V = the regions 
    nodes = df[col].to_numpy()
    matrix = np.array([df.geometry.touches(geo) for geo in df.geometry])
    np.fill_diagonal(matrix, False)
    matrix = pd.DataFrame(matrix, index=nodes, columns=nodes)
    
    # add variables and constraints to the problem
    for xi in matrix:
        problem.addVariable(xi, domain)
        for xj in matrix[matrix[xi] == True].index:
            problem.addConstraint(lambda a,b: a != b, (xi, xj))
        
    return problem.getSolution()
    
    
# call for sask rm map project
if __name__ == "__main__":
    to_geojson(STATCAN_PR, filters={"PRNAME": "Saskatchewan"})
    to_geojson(STATCAN_CSD, filters={"PRNAME": "Saskatchewan", "CSDTYPE": "RM"}, color=True)