'''
Quick & Dirty Dash Test
'''
'''-------------------------- Imports & Constants --------------------------'''
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


from os import chdir
chdir("/Users/noahraegrant/workspace/github.com/nohrg/DS5010/final project")
# my directory stuff gets weird, so I have to manually set it

from dash import Dash, html, dcc, callback, Output, Input

'''------------------------------ Data Clean -------------------------------'''
raw_data = pd.read_csv("aft_v1.csv") # check your file names
data = raw_data.iloc[: , 0:10] # OG sheet had a bunch of blank unused columns
data = data[(data["Code"] != "38623")]
data["Count"] = 1 # the quick & dirty solution for counting rows
## that line is not good code but frankly I really don't care enough for a test
data = data.sort_values("Acad Yr (start)")


sports = data[(data["Code"] == "S")] # Sports
strcon = data[(data["Code"] == "SC")] # Strength & Conditioning
arts = data[(data["Code"] == "A")] # Arts
commsrv = data[(data["Code"] == "C")] # Community Service
teammanage = data[(data["Code"] == "TM")] # Team Managers
other = data[(data["Code"] == "O")] # Other

away = data[(data["Code"] == "SA")] # Semester Abroad
leave = data[(data["Code"] == "L")] # On Leave?
exempt = data[(data["Code"] == "E")] # Jr/Sr exempt

CODES ={"S": sports, "SC": strcon, "A": arts, 
        "C": commsrv, "TM": teammanage, "O": other,
        "SA": away, "L": leave, "E": exempt}

'''------------------------------- Q&D Plot --------------------------------'''

def histogram(code:str):
    fig = px.histogram(CODES[code.upper()], y= "Count", x="Program (name)", 
                       color="Acad Yr (start)")
    fig.update_traces(dict(marker_line_width = 0))
    return fig

'''----------------------------- Example Dash ------------------------------'''
'''
# example from dash plotly site
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')
app = Dash(__name__)
app.layout = html.Div([
    html.H1(children='Title of Dash App', style={'textAlign':'center'}),
    dcc.Dropdown(df.country.unique(), 'Canada', id='dropdown-selection'),
    dcc.Graph(id='graph-content')
])

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    dff = df[df.country==value]
    return px.line(dff, x='year', y='pop')
#'''
'''--------------------------------- Dash ----------------------------------'''
#'''
testapp = Dash(__name__) # creating the dashboard app

testapp.layout = html.Div([
    html.H1(children="Program Enrollment by Category"), # title
    html.Hr(), # breakline
    dcc.RadioItems(options=['S', 'SC', 'A', 'C', 'TM', 'O'], value='S', 
                   id="radio-items"), # radio select buttons
    dcc.Graph(figure = {}, id='graph-content') # graph
])
@callback( # has the dashboard check and change based on selected radio button
    Output(component_id='graph-content', component_property='figure'),
    Input(component_id='radio-items', component_property='value')
)
def update_graph(value): # needs this function specifically named to update fig
    return histogram(value)#'''

'''--------------------------------- Main ----------------------------------'''

if __name__ == "__main__":
    testapp.run(debug=True)
'''Misc notes:
- I think there's a way to have a webbrowser in a tkinter window, so that
would be nicer for the final package than having to call an IP address
in a browser window.
- need to figure out multiple select items + how to use those to change stuff,
I don't think that'll be hard
- formatting with HTML/CSS my beloathed'''