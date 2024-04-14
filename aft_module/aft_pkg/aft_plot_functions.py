'''
AFT Data Visualization Tool
Plot Functions
'''
'''-------------------------- Imports & Constants --------------------------'''

# pre-existing python libraries
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# our custom-made libraries
from .aft_data_org import DATA

'''----------------------------- Data Functions ----------------------------'''
# dataframe manipulations

def filter_dataframe(*, df:pd.DataFrame, 
                     column_name:str, 
                     filters:list) -> pd.DataFrame:
    """
    Function-- filter_dataframe
        returns a filtered dataframe with the correct values
    Parameters:
        df (pd.DataFrame): dataframe to filter
        column_name (str): name of the column to search through
        filters (list): list of values to search for
    Returns:
        pd.DataFrame: the filtered dataframe
    """
    return df[df[column_name].isin(filters)]


def pivot_dataframe(*, df: pd.DataFrame, 
                    index:list[str]):
    """
    Function-- pivot_dataframe
        outputs a pivot table, use with treemap()
    Parameters:
        df (pd.DataFrame)
        index (list[str]): column indicies to use
    Returns:
        pd.DataFrame
    """
    pivot = df.pivot_table(
        index=list(index),
        columns="Program (name)",
        values="Person ID",
        aggfunc="count",
        fill_value=0
    ).reset_index(level =[0,1])
    return pivot


def melt_pivottable(df: pd.DataFrame, id_variables: list[str], 
                    var_name: str, value_name: str) -> pd.DataFrame:
    """
    Function-- melt_pivottable
        turns a Pandas 2-level pivot table into a one-dimensional pivot table,
        use with treemap()
    Parameters:
        df (pd.DataFrame): dataframe to melt
        id_variables (list[str]): main column indices used in the pivot table
        var_name (str): column to group counts by
        value_name (str): column with counts for each row
    Returns:
        pd.DataFrame
    """
    melted = pd.melt(df, id_vars=list(id_variables), var_name=var_name, 
                     value_name=value_name)
    return melted

'''----------------------------- Plot Functions ----------------------------'''
# plot generation

def total_program_enrollment_bar(programs:list[str],
                                 years:list[str],
                                 demographics:str,
                                 groupmode:str,
                                 grades:str) -> go.Figure:
    """
    Function-- total_program_enrollment_bar
        creates a histogram with the selected programs and their combined
        enrollment in the selected years, organizing by demographics and 
        program codes as needed
    Parameters:
        program_codes (list[str]): selected program codes
        programs (list[str]): selected program names
        years (list[int]): selected years
        demographics (str): color filter for the histogram
    Returns: plotly figure
    """
    if grades == "hs":
        grade_level = [9, 10, 11, 12]
    elif grades=="ms":
        grade_level = [7, 8]
    else:
        grade_level = [7,8,9,10,11,12]
        
    filtered_df = filter_dataframe(df = filter_dataframe(
        df=filter_dataframe(
            df=DATA,
            column_name="Program (name)", 
            filters=programs
            ), 
        column_name="Acad Yr (start)", 
        filters=[i for i in range(min(years), max(years)+1)]
        ), column_name="Grade at Time of Activity", filters=grade_level)

    fig = px.histogram(
        filtered_df,
        x="Program (name)",
        color = demographics,
        barmode = groupmode
    )\
        .update_xaxes(tickangle = -45)
    return fig


def program_comparison_bar(programs:list[str], 
                           years:list[str], 
                           groupby:str,
                           demographics:str, 
                           groupmode:str,
                           grades:str) -> go.Figure:
    """
    Function-- program_comparison_bar
        creates enrollment comparison charts
    Parameters:
        program_codes (list[str]): selected program codes
        programs (list[str]): selected programs
        years (list[str]): selected years
        demographics (str): color filter for the histograms
        groupmode (str): stacked or grouped bar charts
        groupby (str): demographic to organize charts by (default is by program)
    Returns:
        go.Figure: plotly figure split by the selected groupby mode
    """
    if grades == "hs":
        grade_level = [9, 10, 11, 12]
    elif grades=="ms":
        grade_level = [7, 8]
    else:
        grade_level = [7,8,9,10,11,12]
    
    filtered_df = filter_dataframe(df = filter_dataframe(
        df=filter_dataframe(
            df=DATA,
            column_name="Program (name)", 
            filters=programs
            ), 
        column_name="Acad Yr (start)", 
        filters=[i for i in range(min(years), max(years)+1)]
        ), column_name="Grade at Time of Activity", filters=grade_level)\
            .sort_values(groupby)
    
    fig = px.histogram(
        filtered_df,
        x="Acad Yr (start)",
        color = demographics,
        labels = {
            "Acad Yr (start)": "Academic Year"
        },
        facet_col=groupby,
        facet_col_wrap=2,
        barmode=groupmode,
        height = 900
    )\
        .update_traces(bingroup=None)\
        .update_layout(bargap=0.05, bargroupgap=0.1)\
        .update_xaxes(tickangle=-45, tickmode="linear", showticklabels=True)\
        .for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    return fig


def treemap(years:range, program_codes:list[str], 
            id_variables:list[str]):
    """
    Function-- treemap
        turns a dataframe into a treemap with the 10 most popular programs
        based on the selected demographics and program codes
    Parameters:
        years (range)
        program_codes (list[str]): selected program codes to examine
        id_variables (list[str]): selected demographics, takes 2 variables
    Returns:
        go.Figure: a treemap with the 10 most popular programs among selected
        demographics
    """
    
    column:str="Program (name)"
    value_name:str="Total"
    
    filtereddf = filter_dataframe(
        df=filter_dataframe(df=DATA, 
                            column_name="Acad Yr (start)", 
                            filters=[i for i in range(min(years), max(years)+1)]), 
        column_name="Code", 
        filters=program_codes)
    pivot = pivot_dataframe(df=filtereddf, index=id_variables)
    melted = melt_pivottable(pivot, id_variables=id_variables, 
                             var_name=column, value_name=value_name)\
                                .sort_values(by="Total", ascending=False)\
                                .groupby(id_variables)\
                                .head(10).reset_index(drop=True)
    
    fig = px.treemap(melted, path=(id_variables + [column]), values = value_name)\
        .update_traces(textinfo="label+value")\
        .update_layout(margin = dict(t=15, l=15, r=15, b=15))
    
    return fig