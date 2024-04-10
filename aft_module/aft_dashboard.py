'''
AFT Data Visualization Tool
Driver
'''
'''-------------------------- Imports & Constants --------------------------'''
# pre-existing python libraries
import numpy as np
import dash
from dash import Dash, html, dcc, callback, Output, Input, State
from dash.exceptions import PreventUpdate

# our custom-made libraries
from aft_pkg.aft_data_org import (DATA, CODES, YEARS, PROGRAM_LIST, 
                                  DEMOGRAPHICS, COMPARISON_GROUPS)
from aft_pkg.aft_plot_functions import *

'''-------------------------------- Dashboard ------------------------------'''


app = Dash(__name__)

app.layout = html.Div(
    [
        html.H2(f"After School Program Enrollment", 
                style={"textAlign": "center", "fontWeight": "bold"}),
        html.Br(),
        
        # years dropdown shared by all plots
        html.Div("Select years:"),
        dcc.Dropdown(
            options=YEARS,
            value=YEARS,
            multi=True,
            id="years-select"),
        
        html.Br(),
        
        dcc.Tabs(
            [
                # total program enrollment
                dcc.Tab([
                    dcc.Graph(
                        id="total-program-enroll-graph"
                    ),
                    html.Div("Select programs:"),
                    dcc.Dropdown(
                        options=PROGRAM_LIST,
                        value=np.random.choice(PROGRAM_LIST, 5),
                        multi=True,
                        id="total-program-enroll-dropdown"),
                    html.Br(),
                    
                    html.Div("Select demographics to highlight:"),
                    dcc.RadioItems(
                        options=DEMOGRAPHICS,
                        value="Code",
                        inline=True,
                        id="total-program-enroll-demographics"),
                    html.Div("Bar grouping mode:"),
                    dcc.RadioItems(
                        options={"group":"grouped bars", "stack":"stacked bars"},
                        value="stack",
                        inline=True,
                        id="total-program-enroll-grouping"
                    )
                ], label="Total Program Enrollment"),
                
                # enrollment comparison charts
                # split enrollment into different charts for comparison
                dcc.Tab([
                    dcc.Graph(id="comparison-enroll-charts"),
                    html.Div("Select programs:"),
                    dcc.Dropdown(
                        options=PROGRAM_LIST,
                        value=np.random.choice(PROGRAM_LIST, 5),
                        multi=True,
                        id="comparison-enroll-programs"),
                    html.Br(),
                    
                    html.Div("Select chart to view:"),
                    dcc.RadioItems(
                        options=COMPARISON_GROUPS,
                        value="Program (name)",
                        inline=True,
                        id="comparison-enroll-format"),
                    html.Div("Select demographics to highlight:"),
                    dcc.RadioItems(
                        options=DEMOGRAPHICS,
                        value="Code",
                        inline=True,
                        id="comparison-enroll-demographics"),
                    html.Div("Bar grouping mode:"),
                    dcc.RadioItems(
                        options={"group":"grouped bars", "stack":"stacked bars"},
                        value="stack",
                        inline=True,
                        id="comparison-enroll-grouping"
                    )
                ], label="Enrollment Comparison Charts")
            ]
        )
    ],
    style={"margin":"1em 5em", "fontSize":18, "fontFamily":"Verdana"}
)
## Total Program Enrollment callback
@app.callback(
    Output("total-program-enroll-graph", "figure"),
    Input("total-program-enroll-dropdown", "value"), # programs
    Input("years-select", "value"), # years
    Input("total-program-enroll-demographics", "value"), # demographics
    Input("total-program-enroll-grouping", "value") # groupmode
)
def update_total_program_enrollment(programs, years, demographics, groupmode):
    return total_program_enrollment_bar(
        programs=programs, 
        years=years, 
        demographics=demographics, 
        groupmode=groupmode)

## Program Comparison callback
@app.callback(
    Output("comparison-enroll-charts", "figure"),
    Input("comparison-enroll-programs", "value"), # programs
    Input("years-select", "value"), # years
    Input("comparison-enroll-format", "value"), # groupby
    Input("comparison-enroll-demographics", "value"), # demographics
    Input("comparison-enroll-grouping", "value") # groupmode
)
def update_comparison_charts(programs, years, groupby, demographics, groupmode):
    return program_comparison_bar(
        programs=programs,
        years=years,
        groupby=groupby,
        demographics=demographics,
        groupmode=groupmode)


'''----------------------------------- Main --------------------------------'''

if __name__ == "__main__":
    app.run_server(host = "0.0.0.0", debug=True)