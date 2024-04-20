'''
AFT Data Visualization Tool
Plot Functions
'''
'''-------------------------- Imports & Constants --------------------------'''

# pre-existing python libraries
import pandas as pd
import numpy as np
import scipy.stats as stats
import plotly.express as px
import plotly.graph_objects as go

# our custom-made libraries
from .aft_data_org import DATA

# Resolves potential errors related to deprecated downcasting methods and
# automatically adapts to future versions of pandas.
pd.set_option('future.no_silent_downcasting', True)

'''----------------------------- Data Functions ----------------------------'''
# dataframe manipulations

def grade_level(grades:str="all") -> list[int]:
    """
    Function-- grade_level
        takes a string and returns a list of numbers for the grade level
    Parameters:
        grades (str, optional): options are hs, ms, or all. Defaults to "all".
    Returns:
        list[int]: list of integers with selected years
    """
    if grades == "hs":
        grade_level = [9, 10, 11, 12]
    elif grades=="ms":
        grade_level = [7, 8]
    else:
        grade_level = [7,8,9,10,11,12]
    return grade_level


def filter_dataframe(*, # requires kwargs to have kwarg name in calls
    df:pd.DataFrame,
    column_name:str,
    filters:list
    ) -> pd.DataFrame:
    """
    Function-- filter_dataframe
        returns a filtered dataframe with the only the selected values in
        the column
        
    Parameters:
        df (pd.DataFrame): dataframe to filter
        column_name (str): name of the column to search through
        filters (list): list of values to search for
        
    Returns:
        pd.DataFrame: filtered dataframe
    """
    return df[df[column_name].isin(filters)]


def pivot_dataframe(*, # requires kwargs to have kwarg name in calls
    df: pd.DataFrame,
    index:list[str]
    ) -> pd.DataFrame:
    """
    Function-- pivot_dataframe
        outputs a partially-flattened pivot table, use with treemap()
        
    Parameters:
        df (pd.DataFrame)
        index (list[str]): column indicies to use
        
    Returns:
        pd.DataFrame: pivoted dataframe
    """
    pivot = df.pivot_table(
        index=list(index),
        columns="Program (name)",
        values="Person ID",
        aggfunc="count",
        fill_value=0
    ).reset_index(level =[i for i in range(len(list(index)))])
    # reset index helps organize the pivot table for melt_pivottable()
    return pivot


def melt_pivottable(
    df: pd.DataFrame,
    id_variables: list[str],
    var_name: str,
    value_name: str
    ) -> pd.DataFrame:
    """
    Function-- melt_pivottable
        turns a Pandas pivot table into a one-dimensional dataframe,
        use with treemap()
        
    Parameters:
        df (pd.DataFrame): dataframe to melt
        id_variables (list[str]): main column indices used in the pivot table
        var_name (str): column to group counts by
        value_name (str): column with counts for each row
        
    Returns:
        pd.DataFrame: each row is a count of program enrollment by the selected
        id varibles
    """
    melted = pd.melt(
        df,
        id_vars=list(id_variables),
        var_name=var_name,
        value_name=value_name
        )
    return melted


def concatenate_program_details(row: pd.Series) -> str:
    '''
    Function-- concatenate_program_details
        Concatenates important program details into a single string
        This function is used to add a 'Full Name' column to the aps data frame

    Parameters:
        row (pd.Series): Pandas Series corresponding to a single row of 
        a DataFrame
            It should contain the columns: 
                'Program (Gender)', 'Program (Level)', and 'Program (name)',
            from which non-NaN values will be concatenated

    Returns:
        str: A string formed by concatenating the non-NaN values of
        'Program (Gender)', 'Program (Level)', and 'Program (name)' columns,
        separated by spaces.
            Returns an empty string if all specified columns contain NaN values
    '''
    # List to hold the non-NaN values
    details = []

    for column in ['Program (Gender)', 'Program (Level)', 'Program (name)']:
        # Append the value if it is not NaN
        if pd.notna(row[column]):
            details.append(row[column])
    # Join the details with a space and return
    return ' '.join(details)


def filter_top_progs(
    df: pd.DataFrame, 
    years:list[int], 
    program_codes: list[str],
    grades:str="hs", 
    n:int=15
    )-> pd.DataFrame:
    '''
    Function-- filter_top_progs
        filters the dataframe to only include the most popular programs
    
    Parameters:
        df (pd.Dataframe) : afternoon program dataframe to be filtered
        years (list[int]): selected years range
        start_gr (int) : start grade (inclusive).  Default is 9th grade.
        end_gr (int) : end grade (inclusive).  Default is 12th grade
        n (int) : Filter by top n most enrolled programs.  Default is top 10
        progs.

    Return:
        aps_top (pd.Dataframe): a dataframe filtered using the above parameters
        with the top n programs
    '''
    # add a column at end of df of program 'Full name'
    df['Full name'] = df.apply(concatenate_program_details, axis=1)

    # apply filters
    aps_top = filter_dataframe(
        df=filter_dataframe(
            df=filter_dataframe(
                df=df,
                column_name="Code",
                filters=program_codes),
            column_name="Acad Yr (start)",
            filters=[i for i in range(min(years), max(years)+1)]
        ),
        column_name='Grade at Time of Activity',
        filters=grade_level(grades)
        )

    # Create an array of the top enrolled programs
    top_enrolled_progs = aps_top['Full name'].value_counts().head(n).index

    # Filter the DataFrame to only keep top_enrolled_programs
    aps_top = filter_dataframe(
        df=aps_top, 
        column_name="Full name", 
        filters=top_enrolled_progs
        )

    return aps_top

## helper functions to run Cramer's V test to create heatmap df
'''
    Sources: Background on Cramer's V test obtained from
    ChatGPT & https://www.statology.org/cramers-v-in-python/

    Cramer's V is a measure of the strength of association 
    between two nominal variables.

    It ranges from 0 to 1 where:

        0 indicates no association between the two variables.
        1 indicates a strong association between the two variables.
    
    It is calculated as:
    
    Cramer's V = √((X2/n) / min(c-1, r-1))

    where:

        X2: The Chi-square statistic
        n: Total sample size
        r: Number of rows
        c: Number of columns
'''    

def create_enrollment_dict(aps_top:pd.DataFrame) -> dict:
    '''
    Function-- create_enrollment_dict
        Creates a dictionary of sets where:
            key = an aps_top_prog name
            value = set of all unique Person IDs who enrolled in that program

    Parameters:
        aps_top (pd.DataFrame) : data frame of all student enrollment choices

    Return:
        program_dict (dict) : dictionary of sets

    Note: 
        Leveraging operation efficiency of most set operators being O(1)
        to hopefully improve runtime.
    '''
    # create an array of all top unique program names (using 'Full Name')
    aps_top_progs = aps_top['Full name'].unique()

    # initialize blank dict
    program_dict = {}

    # iterate through all aps_top_progs to create sets of all 
    # unique student IDs in each program
    for each in aps_top_progs:
        unique_ID_in_prog = aps_top[aps_top['Full name'] == each]
        
        # coercing .unique() from array -> set
        # which should reduce run time in create_contingency_table()
        program_dict[each] = set(unique_ID_in_prog['Person ID'].unique())

    # finally, add key-value pair of ALL unique Person ID's from aps_top
    all_person_IDs = set(aps_top['Person ID'].unique())
    program_dict['all Person IDs'] = all_person_IDs

    return program_dict


def create_contingency_table(program_dict, program_a, program_b):
    '''
    Function-- create_contingency_table
        Create a 2x2 contingency table for enrollments in two programs.

    Parameters:
        program_dict (dict) : Dictionary of sets where 
            keys - program names
            values - sets of Person IDs
        program_a (str) : Name of Program A.
        program_b (str) : Name of Program B.

    Returns:
        contingency_table (np.array) : 2 x 2 contingency table,
            containing Person ID enrollments and overlaps
            between Program A and B, formatted as follows:
            _ _ _ _ _ _ _ _ _ _
            | A & B  | A only  |
            |- - - - - - - - - |
            | B only | Neither |
            | - - - - - - - - -|
    
    Note: 
        Leveraging operation efficiency of most set operators being O(1)
        to hopefully improve runtime.
    
    '''
    set_a = program_dict.get(program_a)
    set_b = program_dict.get(program_b)
    
    # use set operators to create sets for venn diagram
    both = set_a & set_b
    only_a = set_a - set_b
    only_b = set_b - set_a
    neither = set(program_dict['all Person IDs']) - set_a - set_b

    # return counts of each set in 2x2 numpy array
    contingency_table = np.array([
        [len(both), len(only_a)],
        [len(only_b), len(neither)]
        ])

    return contingency_table


def calculate_cramers_v(contingency_table):
    '''
    Function-- calculate_cramers_v
        Calculate Cramer's V statistic for 2x2 contingency table
        containing enrollment #'s between programs A and B.

    Parameters:
        contingency_table (np.array) : 2 x 2 contingency table,
            containing Person ID enrollments and overlaps
            between Program A and B, formatted as follows:
            _ _ _ _ _ _ _ _ _ _
            | A & B  | A only  |
            |- - - - - - - - - |
            | B only | Neither |
            | - - - - - - - - -|
        
    Returns:
        cramers_v (float) : Cramer's V coefficient, rounded to 4 decimals
    '''
    # use scipy.stat's chi-squared contingency function
    # Note: even though we only need the chi2 statistic to calculate Cramer's V
    # all return values shown below by tuple assignment (for reader)
    chi2, pvalue, dof, expected_freq = stats.chi2_contingency(
        contingency_table, correction=False
        )
    
    # Total sample size
    n = np.sum(contingency_table)  
    
    # phi-squared = chi-squared / sample size
    phi2 = chi2 / n
    
    # Number of rows (r) and columns (k)
    r, k = contingency_table.shape
    
    cramers_v = np.sqrt(phi2 / min(k-1, r-1))
    return cramers_v.round(4)


def generate_heatmap_df(aps_top, program_dict):
    '''
    Function-- generate_heatmap_df
        Generate a heatmap dataframe where each cell 
        is the Cramer's V coefficient between two programs.
        This function iterates through all combinations of top programs,
        while efficiently skipping any trivial or symmetric cases.

    Parameters:
        aps_top (pd.DataFrame) : Filtered afternoon program dataframe.
        program_dict (dict) : Dictionary of sets where 
            keys - program names
            values - sets of Person IDs
    Returns:
        heatmap_df (pd.DataFrame) : n x n matrix 
            where each cell is the Cramer's V coefficient between two programs.
    '''
    # get list of all programs from aps_top
    top_enrolled_progs = list(aps_top['Full name'].unique())
    
    # initialize blank heatmap, with program names across rows and columns
    heatmap_df = pd.DataFrame(
        index=top_enrolled_progs, 
        columns=top_enrolled_progs
        )

    # Fill the diagonal with 1s (ie, perfect self-correlation)
    np.fill_diagonal(heatmap_df.values, 1)

    # Iterate through each pair of programs only once
    # start at i = 0 up to i = 12
    for i in range(len(top_enrolled_progs)):
        # iterate j starting from j = i + 1 (since i = j is along diagonal)
        for j in range(i + 1, len(top_enrolled_progs)):
            program1 = top_enrolled_progs[i]
            program2 = top_enrolled_progs[j]
            cont_table = create_contingency_table(
                program_dict,
                program1,
                program2
                )
            cramers_v = calculate_cramers_v(cont_table)
            heatmap_df.at[program1, program2] = cramers_v
            
            # Fill symmetric value on opposite side of diagonal
            heatmap_df.at[program2, program1] = cramers_v 

    # Replace any NaN values with 0 (for pairs without direct comparison)
    heatmap_df = heatmap_df.fillna(0).astype(float).round(4)

    return heatmap_df

'''----------------------------- Plot Functions ----------------------------'''
# plot generation

def total_program_enrollment_bar(
    programs:list[str],
    years:list[str],
    demographics:str,
    groupmode:str,
    grades:str
    ) -> go.Figure:
    """
    Function-- total_program_enrollment_bar
        creates a histogram with the selected programs and their combined
        enrollment in the selected years, organizing by demographics as needed
    Parameters:
        programs (list[str]): selected program names
        years (list[int]): selected years range
        demographics (str): color filter for the histogram
    Returns: 
        go.Figure: a histogram with bars representing total enrollment
    """

    # filter original data to include the selected programs + years + grades
    filtered_df = filter_dataframe(df = filter_dataframe(
        df=filter_dataframe(
            df=DATA,
            column_name="Program (name)",
            filters=programs
            ),
        column_name="Acad Yr (start)",
        filters=[i for i in range(min(years), max(years)+1)]
        ), column_name="Grade at Time of Activity", filters=grade_level(grades))

    # generates histogram
    fig = px.histogram(
        filtered_df,
        x="Program (name)",
        color = demographics,
        barmode = groupmode
    )\
        .update_xaxes(tickangle = -45)
    return fig


def program_comparison_bar(
    programs:list[str],
    years:list[str],
    groupby:str,
    demographics:str,
    groupmode:str,
    grades:str
    ) -> go.Figure:
    """
    Function-- program_comparison_bar
        creates enrollment comparison charts
    Parameters:
        programs (list[str]): selected programs
        years (list[str]): selected years range
        demographics (str): color filter for the histograms
        groupmode (str): stacked or grouped bar charts
        groupby (str): demographic to organize charts by (default: by program)
    Returns:
        go.Figure: plotly figure split by the selected groupby mode
    """

    filtered_df = filter_dataframe(
        df = filter_dataframe(
            df=filter_dataframe(
                df=DATA,
                column_name="Program (name)",
                filters=programs
                ),
            column_name="Acad Yr (start)",
            filters=[i for i in range(min(years), max(years)+1)]
            ), 
        column_name="Grade at Time of Activity", 
        filters=grade_level(grades))\
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
        barmode=groupmode
    )\
        .update_traces(bingroup=None)\
        .update_layout(bargap=0.05, bargroupgap=0.1)\
        .update_xaxes(tickangle=-45, tickmode="linear", showticklabels=True)\
        .for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    return fig


def treemap(
    years:list[int], 
    program_codes:list[str],
    id_variables:list[str]
    ):
    """
    Function-- treemap
        turns a dataframe into a treemap with the 10 most popular programs
        based on the selected demographics and program codes
    Parameters:
        years (list[int]): selected years range
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
                            filters=[i for i in range(min(years),
                                                      max(years)+1)]),
        column_name="Code",
        filters=program_codes)
    pivot = pivot_dataframe(df=filtereddf, index=id_variables)
    melted = melt_pivottable(pivot, id_variables=id_variables,
                             var_name=column, value_name=value_name)\
                                .sort_values(by="Total", ascending=False)\
                                .groupby(id_variables)\
                                .head(10).reset_index(drop=True)

    fig = px.treemap(melted, path=(id_variables + [column]),
                     values = value_name)\
        .update_traces(textinfo="label+value")\
        .update_layout(margin = dict(t=15, l=15, r=15, b=15))

    return fig


def generate_dash_heatmap(
    years: list[int], 
    program_codes: list[str], 
    grades:str="hs"):
    """
    Function-- generate_dash_heatmap
        Converts a Cramer's V correlation matrix of the top 12 most popular
        after-school programs (within any given years) into a Dash heatmap.
    Parameters:
        years (list[int]): List of years to search and filter top programs.
    Returns:
        go.Figure: A heatmap of the Cramer's V correlation coefficient of
        the top 12 most popular programs within a range of years.
    """
    aps_top = filter_top_progs(
        DATA,
        years=years, 
        program_codes=program_codes,
        grades=grades, 
        n=12)
    
    program_dict = create_enrollment_dict(aps_top)
    heatmap_df = generate_heatmap_df(aps_top, program_dict)
    
    # Generate dash heatmap visual
    fig = px.imshow(heatmap_df,
                    labels=dict(color="Correlation"),
                    x=heatmap_df.columns,
                    y=heatmap_df.columns,
                    color_continuous_scale='matter',  # Change color palette
                    color_continuous_midpoint=0.15,
                    range_color=[0, 0.4]  # Set range of colors
                    )

    # Fills heatmap cells with correlation coefficient
    annotations = []
    for i, row in enumerate(heatmap_df.values):
        for j, value in enumerate(row):
            annotations.append(dict(
                x=j,
                y=i,
                text=str(round(value, 2)),
                # Round correlation coefficient to 2 decimal places
                showarrow=False,
                font=dict(color='white')
            ))
    fig.update_layout(annotations=annotations)

    # Make axis titles bold
    fig.update_layout(
        xaxis=dict(title=dict(font=dict(size=18))),
        yaxis=dict(title=dict(font=dict(size=18))))
    return fig
