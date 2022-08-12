#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import dash
from dash import html
from dash import dcc
import plotly.express as px
from dash.dependencies import Input, Output, State
from dash import dash_table
import numpy as np
import plotly.graph_objects as go


# In[2]:


df = pd.read_csv("train.csv")
df.head()


# In[3]:


#data cleaning missing values - get count of null values.
df.isnull().sum()


# In[4]:


colors = {
    'background': '#575757',
    'text': '#ffffff'
}
font_size=15

# color dictonary


# In[5]:


# Data Trasfomation - remove cc and bhp

df['Engine'] = df['Engine'].map(lambda x:str(x)[:-2])
df['Power'] = df['Power'].map(lambda x:str(x)[:-3])
df.head()


# In[6]:


#Dealing with missing value
df=df.drop(columns=['New_Price'],axis=1)
df[['Seats']]=df[['Seats']].fillna(5)  # get median of seats -  fillna for fill mising value bcz there are missing values
df.Engine=pd.to_numeric(df.Engine, errors='coerce') # convert text to numeric
df.Power=pd.to_numeric(df.Power, errors='coerce')
engin_cc_mean=df.Engine.mean()  # find mean valus
power_mean=df.Power.mean()
df[['Engine']]=df[['Engine']].fillna(engin_cc_mean)  # fill with mean value
df[['Power']]=df[['Power']].fillna(engin_cc_mean)
df.isnull().sum() # what are other null values


# remove new price


# In[7]:


df.info()


# In[8]:


def owner_mean_prices(df):  # function to get owner mean value------ to get null
    owner_mean_price=df[['Owner_Type',"Price"]].groupby('Owner_Type')[
    'Price'].agg([min,max,np.mean]).sort_values(by='mean',ascending=False).reset_index(
    ).rename(columns={'mean':'Mean_Price','min':"Min_Price",'max':'Max_Price'})

    return owner_mean_price
owner_mean_price=owner_mean_prices(df)


# In[9]:


search_box=df[['Name','Year','Owner_Type','Price']].groupby(['Name','Year','Owner_Type'])['Price'].agg([max,min,np.mean]).reset_index()

search_box


# In[10]:


def type_sep(typ,data):
    if typ=='ALL' :
        type_data=data
    elif typ=='OPT1':
        type_data=data[data['Transmission']=='Manual']
    else:
        type_data=data[data['Transmission']=='Automatic']
    return type_data

# fuction to seperate tramsmission value 
# when entr value @call back go


# In[11]:



#seperate fuel type
def Fuel_Type_sep (Fuel_Type,data):
    if Fuel_Type=='CNG':
        fuel_filterd_data=data[data['Fuel_Type']=='CNG']
    elif Fuel_Type=='Diesel':
        fuel_filterd_data=data[data['Fuel_Type']=='Diesel']
    elif Fuel_Type=='ALL':
        fuel_filterd_data=data
    elif Fuel_Type=='Petrol':
        fuel_filterd_data=data[data['Fuel_Type']=='Petrol']
    elif Fuel_Type=='LPG':
        fuel_filterd_data=data[data['Fuel_Type']=='LPG']
    else:
        fuel_filterd_data=data[data['Fuel_Type']=='Electric']
    return fuel_filterd_data


# In[12]:


# box 2   - histo-1 with location  graphs are created
def graph_creater(data):
    fig=[  px.box(data,x='Owner_Type',y='Price',title='Owner Type vs. Price',color='Transmission'),
           px.box(data,x='Seats',y='Price',title='Seats vs. Price',color='Transmission'),
           px.histogram(data,x='Location',color='Transmission',title='Vehicle Count in Each City')]
    for i in fig:
        i.update_layout(plot_bgcolor=colors['background'],
                      paper_bgcolor=colors['background'],
                      font_color=colors['text'],width = 550,
        height = 400,
                       )
        
    return fig


# In[13]:


# pie chart create
def Trasmition_pie_fig(data):
    Transmission_type_data=data.groupby('Transmission').count().reset_index()[['Transmission','Price']]
    Transmission_type_data=Transmission_type_data.rename({'Price':"Count"},axis=1)
    fig=px.pie(Transmission_type_data,values="Count",names='Transmission',title="Trasmission Types",
               color_discrete_sequence=px.colors.sequential.RdBu,hole=.3)
    fig.update_layout(plot_bgcolor=colors['background'],
                      paper_bgcolor=colors['background'],width = 400,
        height = 400,
                      font_color=colors['text'],
                    )
    
    return fig


# In[14]:


#dictribution, scateer 
def fig_creater(data,col_name1,col_name2):
    
    fig=[px.histogram(data,x=col_name1,title=("Distribution of "+col_name1)),
         px.histogram(data,x='Owner_Type',title="Count of the Owners" ),
        px.scatter(df,x=col_name2,y='Price',title=('Price vs '+col_name2))]
    for i in fig:
        i.update_layout(plot_bgcolor=colors['background'],
                      paper_bgcolor=colors['background'],
                      font_color=colors['text'], width = 450,
        height = 400,template='seaborn'

                      )
    return fig


# In[15]:


def year_fillter(data,year):
    if year=="ALL":
        year_filterd_data=df
    else:
        year_filterd_data=df[df['Year']==int(year)]
    return year_filterd_data


# In[16]:


app=dash.Dash(__name__)


# In[17]:


# dictonaries and append
year_list=sorted(list(df.Year.unique()))
year=[{'label': i, 'value': i} for i in year_list] # 
year.append({'label':'ALL','value': 'ALL'})
row=df.Fuel_Type.unique()
fuel_type=[{'label': i, 'value': i} for i in row]
fuel_type.append({'label':'ALL','value': 'ALL'})
owner_type=list(df.Owner_Type.unique())
heat_map_data=df.corr()
columns_names=[{'label':'Kilometers_Driven','value':'Kilometers_Driven'},
                {'label':'Engine','value':'Engine'},
                {'label':'Power','value':'Power'},
                {'label':'Price','value':'Price'},
               {'label':'Year','value':'Year'}]

heat_map_data
year
# give values to frop down


# In[18]:


app.layout=html.Div(children=[html.H1('USED CAR MARKET DASHBOARD',style={'textAlign':'center',
                                        'color':colors['text'],'font-size':30}),
                               
                                html.Div([
                                    
                                     
                                      
                                   html.Div([
                                       
                                        html.Div(
                                            [
                                            html.H2('Choose Year:', style={'margin-right': '2em','color':colors['text'],'font-size': '14px'})
                                            ]
                                        ),
                                        dcc.Dropdown(id='input-year', 
                                                    
                                                     options=year,
                                                     value="ALL",

                                                     placeholder="Select a year",
                                                     style={'width':'300px', 'font-size': '14px', 'text-align-last' : 'center'}),
                                            
                                           html.Div(
                                            [
                                            html.H2('Fuel Type:', style={'margin-right': '2em','margin-left': '3em','color':colors['text'],'font-size': '14px'})
                                            ]
                                        ),
                                        dcc.Dropdown(id='input_Fuel_Type', 
                                                    
                                                     options=fuel_type,
                                                     value="ALL",

                                                     placeholder="Select a year",
                                                     style={'width':'300px', 'padding':'2px', 'font-size': '14px', 'text-align-last' : 'center'}),
                                       html.Div(
                                            [
                                           
                                                html.H2('Trasmission Type:', style={'margin-right': '2em','margin-left': '3em','color':colors['text'],'font-size': '14px'}),
                                            ]
                                        ),dcc.Dropdown(
                                    id='input_vehical_type',
                                    options=[
                                        {'label': 'Manual', 'value': 'OPT1'},
                                        {'label': 'Automatic', 'value': 'OPT2'},
                                        {'label': 'ALL', 'value': 'ALL'}
                                    ],value="ALL",
                                    
                                   placeholder="Select The Type",
                                    style={'width':'300px', 'padding':'2px', 'font-size': '14px', 'text-align-last' : 'center'})
                                   ], style={'display': 'flex'}),  
                                   ]),
                          
                        
                               html.Div([
                                   
                                  html.Div([], id='plot1',), 
                                             
                                   
                                         
                                   html.Div([], id='plot2',),
                                   html.Div([], id='plot3',),
                                   
#                                    
                               ],style={'display': 'flex',}),
                              
                               
                               
                                                        
                              
                              
                              
                               html.Div([
                                
                                   
#                                html.Div([
#                               dash_table.DataTable(
#                                     id='table',
#                                     columns=[{"name": i, "id": i} for i in owner_mean_price.columns],
#                                     data=owner_mean_price.to_dict('records'),
#                                style_data={'color': 'black','backgroundColor': 'white'},
                                  
#                                style_data_conditional=[{'if': {'row_index': 'odd'},'backgroundColor': 'rgb(220, 220, 220)',}],
#                                 style_header={'backgroundColor': 'rgb(210, 210, 210)','color': 'black','fontWeight': 'bold'
#     })
#                                         ],style={'width':'800px'},)
                              ]),
                              html.Div([
                                  html.Div([dcc.RadioItems(
                                id='column_name_change',
                                options=[{'label':'Kilometers_Driven','value':'Kilometers_Driven'},
                {'label':'Engine','value':'Engine'},
                {'label':'Power','value':'Power'},
                {'label':'Price','value':'Price'},
               {'label':'Year','value':'Year'}],
                                    value='Year',style={'width':'400px', 'padding':'3px','color':colors['text']},
                                   labelStyle={'display': 'inline-block'}
                                    ),
                              
                                  
                                       html.Div([], id='fig1'),
                                  ])
                                  ,
                                      html.Div([], id='fig2'),
                                      html.Div([],id='plot4')
                                  

   

    
                ],style={'display': 'flex',}),
                              
                             html.Div([
                                  html.Div([
                                dcc.Checklist(
                                id='heat_slt_col',
                                options=[{'label': x, 'value': x} 
                                     for x in heat_map_data.columns],
                                    value=heat_map_data.columns.tolist(),
                                    style={'width':'500px', 'padding':'3px','color':colors['text']}
                                    ),
                                dcc.Graph(id="Heat_map")]),
                                html.Div([
                                            html.H2('VehicleType:', style={'margin-right': '2em',
                                                                           'color':colors['text'],'font-size': '14px'}),
                                         
                                    dcc.Dropdown(id='choice2',
                                         options=[{'label':x, 'value':x}
                                                  for x in sorted(df.Name.unique())],
                                         value='Maruti Wagon R LXI CNG',
                                            style={'width':'300px', 'padding':'3px'}
                                         ),
                        #Initialing the graph from dash core components
                                          dcc.Graph(id="graph2")]),
                                 html.Div([dcc.RadioItems(
                                id='column_name_change2',
                                options=[{'label':'Kilometers_Driven','value':'Kilometers_Driven'},
                {'label':'Engine','value':'Engine'},
                {'label':'Power','value':'Power'},
    
                               ],
                                    value='Kilometers_Driven',style={'width':'500px', 'padding':'4px','color':colors['text']},
                                   labelStyle={'display': 'inline-block'}
                                    ),
                              
                                  
                                       html.Div([], id='fig3'),
                                  ],style={'margin-left': '6em'})
                        ],style={'display': 'flex',}),   
                                ],style={'background-color':colors['background']})
                            
                            
                                
                           
                               
                              
                 


# In[19]:


@app.callback( [Output(component_id='plot1', component_property='children'),
                Output(component_id='plot2', component_property='children'),
                Output(component_id='plot3', component_property='children'),
                Output(component_id='plot4', component_property='children')
               
               ],
               [Input(component_id='input-year', component_property='value'),
               Input(component_id='input_vehical_type', component_property='value'),
               Input(component_id='input_Fuel_Type', component_property='value')],
              [State("plot1", 'children'),State("plot2", 'children'),State("plot3", 'children'),
               State("plot4", 'children')
               ])
def graph_render(year,vehical_type,Fuel_Type,c1,c2,c3,c4):
    
    year_filterd_data=year_fillter(df,year)
   
    fuel_and_year_filterd_data=Fuel_Type_sep(Fuel_Type,year_filterd_data)
    
    tras_fuel_year_sep_data=type_sep(vehical_type,fuel_and_year_filterd_data)
    
    
    pie_fig=Trasmition_pie_fig(fuel_and_year_filterd_data)
    
    box_fig_owner,box_fig_seats,stck_fig=graph_creater(tras_fuel_year_sep_data)
    
    return [dcc.Graph(figure=pie_fig),
            dcc.Graph(figure=box_fig_owner),
           dcc.Graph(figure=box_fig_seats),
           dcc.Graph(figure=stck_fig)]


# In[20]:


@app.callback(
    Output("Heat_map", "figure"), 
    [Input("heat_slt_col", "value")])
def filter_heatmap(cols):
    fig = px.imshow(heat_map_data[cols] , title = "Heat Map")
    fig.update_layout(plot_bgcolor=colors['background'],
                      paper_bgcolor=colors['background'],width = 400,
                      font_color=colors['text'],
                     )
    return fig


# In[21]:


@app.callback( [Output(component_id='fig1', component_property='children'),
                Output(component_id='fig2', component_property='children'),
                Output(component_id='fig3', component_property='children')
               ],
               [Input(component_id='input_Fuel_Type', component_property='value'),
               Input(component_id='column_name_change', component_property='value'),
               Input(component_id='column_name_change2', component_property='value')],
              [State("fig1", 'children'),State("fig2", 'children'),State("fig3", 'children')])

def get_graph(Fuel_Type,col_name1,col_name2,c1,c2,c3):
    
    filt_data=Fuel_Type_sep(Fuel_Type,df)
  
    fig1,fig2,fig3=fig_creater(filt_data,col_name1,col_name2)
    
    
    
    
    
    
    return [dcc.Graph(figure=fig1),
            dcc.Graph(figure=fig2),
            dcc.Graph(figure=fig3)
            ]


# In[22]:


@app.callback(
    Output("graph2","figure"),
    [Input("choice2","value")]
   
)
def update_figure(VehicleType):
    dff = df[df.Name==VehicleType]
    fig=px.pie(dff, names='Location',title='Sold or Available Locations of Cars')
    fig.update_layout(plot_bgcolor=colors['background'],
                      paper_bgcolor=colors['background'],width = 400,
        height = 400,
                      font_color=colors['text'],
                    )
    return fig


# In[ ]:


if __name__=='__main__':
    app.run_server()


# In[ ]:





# In[ ]:




