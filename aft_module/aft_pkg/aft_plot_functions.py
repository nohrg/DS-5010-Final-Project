'''
AFT Data Visualization Tool
Plot Functions
'''
'''-------------------------- Imports & Constants --------------------------'''

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from .aft_data_org import DATA

'''----------------------------- Plot Functions ----------------------------'''

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


def total_program_enrollment_bar(programs:list[str],
                                 years:list[str],
                                 demographics:str,
                                 groupmode:str) -> go.Figure:
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
    filtered_df = filter_dataframe(
        df=filter_dataframe(
            df=DATA,
            column_name="Program (name)", 
            filters=programs
            ), 
        column_name="Acad Yr (start)", 
        filters=years
        )

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
                           groupmode:str, ) -> go.Figure:
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
    Yields:
    """
    filtered_df = filter_dataframe(
        df=filter_dataframe(
            df=DATA,
            column_name="Program (name)", 
            filters=programs
            ), 
        column_name="Acad Yr (start)", 
        filters=years
        ).sort_values(groupby)
    
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