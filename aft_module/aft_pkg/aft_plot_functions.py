'''
AFT Data Visualization Tool
Plot Functions
'''
'''-------------------------- Imports & Constants --------------------------'''

# pre-existing python libraries
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency
import itertools
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


def concatenate_program_details(row):
    '''
    Function to concatenate important program details into a single string
    This function is used to add a 'Full Name' column to the aps data frame.

    Args:
        row (pd.Series) : A Pandas Series corresponding to a single row of a DataFrame.
            It should contain the columns 'Program (Gender)', 'Program (Level)',
            and 'Program (name)', from which non-NaN values will be concatenated.

    Returns:
        str : A string formed by concatenating the non-NaN values of 'Program (Gender)',
            'Program (Level)', and 'Program (name)' columns, separated by spaces.
            Returns an empty string if all specified columns contain NaN values.
    '''
    # List to hold the non-NaN values
    details = []

    for column in ['Program (Gender)', 'Program (Level)', 'Program (name)']:
        # Append the value if it is not NaN
        if pd.notna(row[column]):
            details.append(row[column])
    # Join the details with a space and return
    return ' '.join(details)


def filter_top_progs(df, start_yr=2010, end_yr=2022, start_gr=9, end_gr=12,
                     n=15):
    '''
    Args:
        df (pd.Dataframe) : afternoon program dataframe to be filtered
        start_yr (int) : begin filtering df starting in this year (inclusive).
        Default is 2010
        end_yr (int) : stop filtering df in this year (inclusive). Default
        is 2022
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
    aps_top = df[(df['Acad Yr (start)'] >= start_yr)
                 & (df['Acad Yr (start)'] <= end_yr)
                 & (df['Grade at Time of Activity'] >= start_gr)
                 & (df['Grade at Time of Activity'] <= end_gr)]

    # Create an array of the top enrolled programs
    top_enrolled_progs = aps_top['Full name'].value_counts().head(n).index

    # Filter the DataFrame to only keep top_enrolled_programs
    aps_top = aps_top[aps_top['Full name'].isin(top_enrolled_progs)]

    return aps_top

# helper function to help convert aps_top df into an enrollment matrix

def mark_enrollments(aps_top):
    '''
    Data wrangling function that generates an enrollments matrix.
    Creates a df so that each row in a unique Person ID
    and the columns are the top_enrolled_progs

    1 = enrolled, 0 = not enrolled
    '''
    # create array of all unique students from aps_top
    person_ID_array = aps_top['Person ID'].unique()

    # initialize a Data Frame with all the Person ID's as first column
    matrix = pd.DataFrame(person_ID_array, columns=["Person ID"])

    # fill rest of matrix with 0's and column_titles
    column_titles = aps_top['Full name'].unique()
    for column in column_titles:
        matrix[column] = 0

    for _, row in DATA.iterrows():
        person_id = row['Person ID']
        program = row['Full name']

        # Check if the program exists in the matrix columns to avoid KeyError
        if program in matrix.columns:
            # Find the index in matrix where Person_ID matches and set the
            # program column to 1
            matrix.loc[matrix['Person ID'] == person_id, program] = 1

    return matrix


# helper functions to run Cramer's V test and create a correlation matrix
def cramers_v(x, y):
    '''
    Calculate Cramer's V statistic for any two pairwise columns of a DataFrame.
    '''
    confusion_matrix = pd.crosstab(x, y)
    chi2 = chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    phi2 = chi2 / n
    r, k = confusion_matrix.shape
    phi2_corr = max(0, phi2 - ((k - 1) * (r - 1)) / (n - 1))
    r_corr = r - ((r - 1) ** 2) / (n - 1)
    k_corr = k - ((k - 1) ** 2) / (n - 1)

    return (phi2_corr / min((k_corr - 1), (r_corr - 1))) ** 0.5


def generate_cramers_results(matrix):
    '''
    Given an enrollment matrix, this function will calculate all pairwise
    Cramer's V test for any two columns of the input DataFrame.

    Args:
        matrix (pd.Dataframe) - enrollment matrix each row is a unique person
        ID, columns are the different top programs to compare. and '1's to
        mark all of their enrollments while at the school
    Returns:
        cramers_v_results (dict) : dictionary of all pairwise programs and
        their Cramer's V coefficients
            keys (tuple) - (program1 , program 2)
            value (float) - Cramer's V coefficient (0 = no association,
            1 = pure association)
    '''
    # Drop the 'Person ID' column to focus on program columns only
    matrix = matrix.drop("Person ID", axis=1)

    # Generate all unique pairs of programs
    program_columns = matrix.columns
    pairs = list(itertools.combinations(program_columns, 2))

    # Calculate Cramer's V for each pair and store the results
    # could store results in a dictionary
    cramers_v_results = {}
    for program1, program2 in pairs:
        cv = cramers_v(matrix[program1], matrix[program2])
        cramers_v_results[(program1, program2)] = cv

    return cramers_v_results


def generate_heatmap_df(aps_top, cramers_v_results):
    '''
    Args:
        aps_top (pd.Dataframe) : filtered afternoon program dataframe (return
        from filter_top_progs function)
        cramers_v_results (dict) : dictionary of all pairwise cramer's V tests
        (return from generate_cramers_v function)

    Returns:
        heatmap_df (pd.Dataframe) : n x n matrix where each cell is the
         Cramer's V coeffiecient between two progs
    '''
    # extract all program names (to populate row and column variables)
    top_enrolled_progs = aps_top['Full name'].unique()

    # Initialize the DataFrame
    heatmap_df = pd.DataFrame(index=top_enrolled_progs, columns=top_enrolled_progs)

    # Fill the diagonal with 1s for perfect self-correlation
    np.fill_diagonal(heatmap_df.values, 1)

    # Populate the DataFrame with Cramer's V results
    for (program1, program2), cv_value in cramers_v_results.items():
        heatmap_df.at[program1, program2] = cv_value
        heatmap_df.at[program2, program1] = cv_value  # Fill symmetric value

    # Replace any NaN values with 0 (for pairs without direct comparison,
    # if any)
    heatmap_df = heatmap_df.fillna(0)

    # Ensure the data is of float type for heatmap compatibility
    heatmap_df = heatmap_df.astype(float).round(4)

    return heatmap_df

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


def generate_dash_heatmap():
    aps_top = filter_top_progs(DATA, n=12)
    matrix = mark_enrollments(aps_top)
    cramers_v_results = generate_cramers_results(matrix)
    heatmap_df = generate_heatmap_df(aps_top, cramers_v_results)
    fig = px.imshow(heatmap_df,
                    labels=dict(color="Correlation"),
                    x=heatmap_df.columns,
                    y=heatmap_df.columns,
                    color_continuous_scale='matter',  # Change color palette
                    color_continuous_midpoint=0.15,
                    range_color=[0, 0.3]  # Set range of colors
                    )

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
