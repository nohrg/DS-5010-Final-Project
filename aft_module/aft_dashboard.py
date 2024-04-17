'''
AFT Data Visualization Tool
Driver
'''
'''-------------------------- Imports & Constants --------------------------'''

# pre-existing python libraries
from dash import Dash, html, dcc, callback, Output, Input

# our custom-made libraries
from aft_pkg.aft_data_org import (CODES, YEARS, PROGRAM_LIST, 
                                  DEMOGRAPHICS, COMPARISON_GROUPS, GRADES,
                                  TREEMAP_DEMOGS)
from aft_pkg.aft_plot_functions import *

'''-------------------------------- Dashboard ------------------------------'''

app = Dash(__name__)

app.layout = html.Div(
    [
        html.H2(f"Afternoon Program Enrollment Visualizations", 
                style={"textAlign": "center", "fontWeight": "bold"}),
        html.Br(),
        
        # years dropdown shared by all plots
        ### slider start and end point, affects all* charts
        html.Div("Select years:"),
        dcc.RangeSlider(
            min=min(YEARS),
            max=max(YEARS),
            step=1,
            value=[min(YEARS),max(YEARS)],
            marks={i: str(i) for i in range(min(YEARS), max(YEARS)+1)},
            id="years-slider"),
        html.Br(),
        
        # different visualization tabs
        dcc.Tabs(
            [
                # Total Program Enrollment
                ## basic histogram comparing overall enrollment
                dcc.Tab([
                    html.Div("Displays enrollment data for selected programs"),
                    dcc.Graph(
                        id="total-program-enroll-graph"
                    ),
                    
                    ## program selection, random by default
                    html.Div("Select programs:"),
                    dcc.Dropdown(
                        options=PROGRAM_LIST,
                        value=np.random.choice(PROGRAM_LIST, 5),
                        multi=True,
                        id="total-program-enroll-dropdown"),
                    html.Br(),
                    
                    ## affects color of histogram bars
                    html.Div("Select demographics to highlight:"),
                    dcc.RadioItems(
                        options=DEMOGRAPHICS,
                        value="Program (name)",
                        inline=True,
                        id="total-program-enroll-demographics"),
                    html.Br(),
                    
                    ## middle school, high school, or whole school
                    html.Div("Grades:"),
                    dcc.RadioItems(
                        options=GRADES,
                        value="all",
                        inline=True,
                        id="total-program-enroll-grades"
                    ), html.Br(),
                    
                    ## changes whether bars are grouped or stacked together
                    html.Div("Bar grouping mode:"),
                    dcc.RadioItems(
                        options={"group":"Grouped Bars", 
                                 "stack":"Stacked Bars"},
                        value="stack",
                        inline=True,
                        id="total-program-enroll-grouping"
                    )
                ], label="Total Program Enrollment"),
                
                # Enrollment Comparison
                ## splits enrollment into different histograms for comparison
                dcc.Tab([
                    html.Div("Compares enrollment in selected programs "+
                             " across demographics factors"),
                    dcc.Graph(id="comparison-enroll-charts", 
                              style= {'height': '900px'}),
                    
                    ## program selection, random by default
                    html.Div("Select programs:"),
                    dcc.Dropdown(
                        options=PROGRAM_LIST,
                        value=np.random.choice(PROGRAM_LIST, 5),
                        multi=True,
                        id="comparison-enroll-programs"),
                    html.Br(),
                    
                    ## the facet that the charts are split along
                    html.Div("Select chart to view:"),
                    dcc.RadioItems(
                        options=COMPARISON_GROUPS,
                        value="Program (name)",
                        inline=True,
                        id="comparison-enroll-format"),
                    html.Br(),
                    
                    ## affects histogram bar color
                    html.Div("Select demographics to highlight:"),
                    dcc.RadioItems(
                        options=DEMOGRAPHICS,
                        value="Program (name)",
                        inline=True,
                        id="comparison-enroll-demographics"),
                    html.Br(),
                    
                    ## middle school, high school, or whole school
                    html.Div("Grades:"),
                    dcc.RadioItems(
                        options=GRADES,
                        value="all",
                        inline=True,
                        id="comparison-enroll-grades"
                    ),
                    html.Br(),
                    
                    ## changes whether bars are grouped or stacked together
                    html.Div("Bar grouping mode:"),
                    dcc.RadioItems(
                        options={"group":"Grouped Bars",
                                 "stack":"Stacked Bars"},
                        value="stack",
                        inline=True,
                        id="comparison-enroll-grouping"
                    )
                ], label="Enrollment Comparison Over Time"),
                
                # Correlation Heatmap
                ## heatmap showing correlation of 12 most popular programs
                dcc.Tab([
                    html.Div("Displays correlation heatmap of the top 12 "
                             "most popular activities in the selected program"
                             " codes and years, as measured by their "
                             "Cramer's V coefficient."),

                    dcc.Graph(id="correlation-heatmap",
                              style= {'height': '600px', 'width': '800px'}),
                    html.Br(),
                    
                    ## includes only selected program codes
                    ## (i.e. sports or arts)
                    html.Div("Program codes:"),
                    dcc.Checklist(
                        options:=CODES, # walrus assignment for use in value
                        value=[option for option in options],
                        inline=True,
                        id="correlation-heatmap-program-codes"
                    ),
                    html.Br(),
                    
                    ## middle school, high school, or whole school
                    html.Div("Grades:"),
                    dcc.RadioItems(
                        options=GRADES,
                        value="hs",
                        inline=True,
                        id="correlation-heatmap-grades"
                    ), html.Br()

                ], label="Program Correlation"),

                # Program Popularity Treemap
                ## Displays program popularity across demographics
                dcc.Tab([
                    html.Div("Displays the 10 most popular programs among "+
                             "selected demographics"),
                    html.Div("Click into a square to expand it"),
                    dcc.Graph(id="top-ten-table"),
                    html.Br(),

                    ## includes only selected program codes
                    ## (i.e. sports or arts)
                    html.Div("Program codes:"),
                    dcc.Checklist(
                        options:=CODES, # walrus assignment for use in value
                        value=[option for option in options],
                        inline=True,
                        id="top-ten-program-codes"
                    ),
                    html.Br(),

                    ## demographics filters for backend pivot table
                    html.Div("Select demographics options"+
                             " (best results with 3 or fewer selected):"),
                    dcc.Checklist(
                        options = TREEMAP_DEMOGS,
                        value=["Race/ethnicity", "Gender code"],
                        id = "top-ten-id-variables"
                    )
                ], label="Program Popularity")
            ]
        )
    ],
    style={"margin":"1em 5em", "fontSize":18, "fontFamily":"Verdana"}
)

## Total Program Enrollment callback
@app.callback(
    Output("total-program-enroll-graph", "figure"),
    Input("total-program-enroll-dropdown", "value"), # programs
    Input("years-slider", "value"), # years
    Input("total-program-enroll-demographics", "value"), # demographics
    Input("total-program-enroll-grouping", "value"), # groupmode
    Input("total-program-enroll-grades", "value")
)
def update_total_program_enrollment(programs, years, demographics,
                                    groupmode, grades):
    '''total program enrollment chart'''
    return total_program_enrollment_bar(
        programs=programs,
        years=years,
        demographics=demographics,
        groupmode=groupmode,
        grades=grades)


## Program Comparison callback
@app.callback(
    Output("comparison-enroll-charts", "figure"),
    Input("comparison-enroll-programs", "value"), # programs
    Input("years-slider", "value"), # years
    Input("comparison-enroll-format", "value"), # groupby
    Input("comparison-enroll-demographics", "value"), # demographics
    Input("comparison-enroll-grouping", "value"), # groupmode
    Input("comparison-enroll-grades", "value")
)
def update_comparison_charts(programs, years, groupby,
                             demographics, groupmode, grades):
    '''program comparison charts'''
    return program_comparison_bar(
        programs=programs,
        years=years,
        groupby=groupby,
        demographics=demographics,
        groupmode=groupmode,
        grades=grades)


# Correlation Heatmap callback
@app.callback(
    Output('correlation-heatmap', 'figure'),
    Input("years-slider", "value"),
    Input("correlation-heatmap-program-codes", "value"),
    Input("correlation-heatmap-grades", "value"),
    [Input('correlation-heatmap', 'hoverData')]
)
def update_heatmap(years, program_codes, grades, hoverData):
    '''program correlation heatmap'''
    heatmap = generate_dash_heatmap(
        years=years,
        program_codes=program_codes,
        grades=grades)
    return heatmap


# checklist disabling callback (for popularity treemap)
'''@app.callback(
    Output("top-ten-id-variables", "options"),
    Input("top-ten-id-variables", "value")
)
def update_multi_options(value):
    #''''''The treemap popularity table only works when 2 demographics are
    selected. This callback prevents the user from selecting more than 2
    options at a time.''''''
    options = TREEMAP_DEMOGS
    if len(value) >= 2:
        options = [
            {
                "label": TREEMAP_DEMOGS[option],
                "value": option,
                "disabled": option not in value,
            }
            for option in options
        ]
    return options'''


# Program Popularity callback
@app.callback(
    Output("top-ten-table", "figure"),
    Input("years-slider", "value"),
    Input("top-ten-program-codes", "value"),
    Input("top-ten-id-variables", "value")
    )
def update_treemap(years, codes, id_demogs):
    '''program popularity treemap'''
    return treemap(years=years, program_codes=codes,
                   id_variables=id_demogs)


'''----------------------------------- Main --------------------------------'''

if __name__ == "__main__":
    
    app.run_server(debug=False)
    