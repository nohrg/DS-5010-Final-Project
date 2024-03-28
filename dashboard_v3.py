'''
Dash Filtering Tests
'''
'''-------------------------- Imports & Constants --------------------------'''
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

pd.options.plotting.backend = "plotly"


from os import chdir
chdir("/Users/noahraegrant/workspace/github.com/nohrg/DS5010/final project")
# my directory stuff gets weird, so I have to manually set it

import dash
from dash import Dash, html, dcc, callback, Output, Input, State
from dash.exceptions import PreventUpdate
'''------------------------------ Data Clean -------------------------------'''
DATA = pd.read_csv("aft_v3.csv") # check your file names

program_list = list(DATA.sort_values("Code")["Program (name)"].unique())
codes = list(DATA.sort_values("Code")["Code"].unique())
# 'A', 'C', 'E', 'IP', 'L', 'O', 'S', 'SA', 'SC', 'TM'
code_labels = ['Arts (A)', 'Community Service (C)', 'Exempt (E)', 
               'Independent Project (IP)', 'Leave (L)', 'Other (O)',
               'Sports (S)',  'Semester Abroad (SA)', 
               'Strength & Conditioning (SC)', 'Team Manager (TM)']
code_dict = {codes[i]: code_labels[i] for i in range(len(code_labels))}
years = list(DATA.sort_values("Acad Yr (start)")["Acad Yr (start)"].unique())

DEMOGRAPHICS={"Gender code": "Gender", 
              "Race/ethnicity":"Race/Ethnicity", 
              "FA": "Financial Aid Status", 
              "Grade at Time of Activity":"Grade", 
              "Program (Level)":"Program Level",
              "Code": "None"}

app = Dash(__name__)

app.layout = html.Div(
    [
        html.H2(f"After School Program Enrollment", 
                style={"textAlign": "center"}),
        # program code selection
        html.Div("Select the program code(s):"),
        dcc.Checklist(
            id = "program-codes",
            options = code_dict,
            value = codes,
            inline = True
        ),
        html.Br(),
        # program selection
        html.Div("Choose Programs:"),
        dcc.Dropdown(
            id = "program-dropdown",
            value = np.random.choice(program_list, 5),
            options = program_list,
            multi=True
        ),
        ### note to self: want to find ways to hide unselected prog code items
        html.Br(),
        # year selection
        html.Div("Choose Years:"),
        dcc.Dropdown(
            id="program-years",
            options = years,
            value = years,
            multi=True
        ),
        # select all for years, need to get working (currently borked)
        html.Button("Select All",
            id="select-all-years",
            n_clicks=0),
        html.Br(),
        # demographics filter selection
        ### may turn into object and toss into the relevant tabs
        ### test how that works
        html.Div("Select Demographics Filter:"),
        dcc.RadioItems(id="demographics-filter",
                       options = DEMOGRAPHICS, 
                       value = "Code", 
                       inline=True),
        html.Br(),
        # plot tabs
        dcc.Tabs(
            [
                dcc.Tab([
                    dcc.Graph(
                        id="total-bar-graph")], 
                    label="Total Enrollment"),
                dcc.Tab([
                    html.Div("Grouping Mode:"),
                    dcc.RadioItems(
                        id="comparison-radio",
                        options = ["group", "stack"],
                        value = "stack",
                        inline = True
                        ),
                    html.Div("Group by:"),
                    dcc.RadioItems(
                        id="comparison-group",
                        options = {
                            "Program (name)": "Program",
                            "Grade at Time of Activity":"Grade",
                            "FA": "Financial Aid Status",
                            "Gender code": "Gender", 
                            "Race/ethnicity":"Race/Ethnicity"
                            },
                        value = "Program (name)",
                        inline = True
                        ),
                    dcc.Graph(id='comparison-bar-graph')
                ], label="Enrollment Comparison Charts")
            ]
        )
    ],
    style={"margin":"1em 5em", "fontSize":18}
)
### Select All for Years
### currently broken
'''@app.callback(
    Output("program-years", "value"),
    Input("select-all-years", "n_clicks"),
    [State("program-years", "options")]
)
def update_year_dropdown(n_clicks, feature_options):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate()
    else:
        trigged_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if trigged_id == "select_all":
            if n_clicks == 0:
                raise PreventUpdate()
            if n_clicks % 2 == 0:
                return []
            else:
                return [i["value"] for i in feature_options]'''
'''@app.callback(
    Output("program-dropdown","options"),
    Input("program-codes", "value"),
    State("program-dropdown", "value")
) 
def hide_dropdown_options(program_codes):
    df = DATA[DATA["Code"]].isin(program_codes)
    return list(df["Program (name)"].unique())'''
### Histogram with total counts for given years, groupable by demo
@app.callback(
    Output("total-bar-graph", "figure"),
    Input("program-codes", "value"),
    Input("program-dropdown", "value"),
    Input("program-years", "value"),
    Input("demographics-filter", "value")
)
def update_bar_graph(program_codes, programs, years, demographics):
    filtered_df = DATA[DATA["Code"].isin(program_codes)]
    filtered_df = filtered_df[filtered_df["Program (name)"].isin(programs)]
    filtered_df = filtered_df[filtered_df["Acad Yr (start)"].isin(years)]
    
    fig = px.histogram(
        filtered_df,
        x="Program (name)", color=demographics, barmode='group'
    )\
        .update_xaxes(tickangle = -45)
    return fig
### Histogram comparing years, groups by years
@app.callback(
    Output("comparison-bar-graph", "figure"),
    Input("program-codes", "value"),
    Input("program-dropdown", "value"),
    Input("program-years", "value"),
    Input("demographics-filter", "value"),
    Input("comparison-radio", "value"),
    Input("comparison-group", "value")
)
def update_comparison_bar_chart(program_codes, programs, years, 
                                demographics, groupmode, groupby):
    filtered_df = DATA[DATA["Code"].isin(program_codes)]
    filtered_df = filtered_df[filtered_df["Program (name)"].isin(programs)]
    filtered_df = filtered_df[filtered_df["Acad Yr (start)"].isin(years)]
    filtered_df = filtered_df.sort_values(groupby)
    
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
        height = 1000
    )\
        .update_traces(bingroup=None)\
        .update_layout(bargap=0.05, bargroupgap=0.1)\
        .update_xaxes(tickangle=-45, nticks=25, showticklabels=True)\
        .for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)
    
## notes for self: code/year select all, tabs as class (or, rather, child class)
## I think I could do a lot with inheritance and importing that as a module into driver
## "export as PDF" or png button, exports the dash + summary stats
## summary stats tab? summary stats below the plots?