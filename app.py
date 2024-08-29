import dash
import pandas as pd
import plotly.express as px 
from dash import Dash, html, dcc, Input, Output
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import dash_leaflet as dl


# read data
SkinCare_df = pd.read_excel('SkinCareProduct.xlsx')
Food_df = pd.read_excel('QBUS5010.xlsx')

# data preprocessing:
selected_features = SkinCare_df.columns
SkinCareProduct_df = SkinCare_df[selected_features]
Food_df.columns = ['food', 'Vitamin C','Vitamin A', 'Vitamin E','Carotene']
min_value = Food_df.min()
Food_df = Food_df.fillna(min_value)
Food_df['Vitamin A'] = Food_df['Vitamin A']/1000
Food_df['Carotene'] = Food_df['Carotene']/1000
skin_nutrition_dict = {'Brightening':['Vitamin C'], 'Acne': ['Carotene', 'Vitamin A'], 'Anti-Aging' :['Vitamin E', 'Vitamin C']}

# app initialisation:
SkinCare_df_age_CS = SkinCare_df.loc[SkinCare_df['Skin_Issue']=='Anti-Aging',:]
SkinCare_df_age_CS_sorted = SkinCare_df_age_CS.sort_values(by=['Review_Score'], ascending = False)
SkinCare_df_age_CS_Top5= SkinCare_df_age_CS_sorted.head()

# create dash object
app = dash.Dash(external_stylesheets = [dbc.themes.MINTY])

server = app.server

# define Input options:
skin_issues_list = sorted(SkinCareProduct_df['Skin_Issue'].unique())
product_type_list = sorted(SkinCareProduct_df['Type'].unique())

# Define app components:
skin_issue = dcc.Dropdown(options = skin_issues_list,  value = 'Anti-Aging' , id = 'input_skin_issue', persistence= True)
product_type = dcc.Dropdown(options = product_type_list, value = product_type_list, 
                            id = 'input_product_type', multi = True, persistence = True)

df_storage_SkinCare = dcc.Store(id = 'df_storage_skin_care', storage_type='memory')
df_storage_Food = dcc.Store(id = 'df_storage_food', storage_type='memory')

#Section C and D title
# title_card = dbc.Card(
#     dbc.CardBody([
#         html.H4("Hard to make decisions?"),
#         #html.H6("Hard to make decisions?", className="display-5", style={"font-size": "16px"}),
#         html.P("Use the charts below to make an informed choice!", className="lead", style={"font-size": "12px"})
#     ]),
#     className="mb-4",
#     style={"max-width": "450px"} ,

# )


list_item_title_left = dbc.ListGroupItem(html.Div([
    html.Br(),
    html.H4("Hard to make decisions?"),
    html.P("Use the charts below to make an informed choice!", className="lead", style={"font-size": "12px"}),
    html.Br()]), id = 'list_item_title_left')
list_group_title_left = dbc.ListGroup(list_item_title_left, class_name='list-group-item-info mb-4', id = 'list_group_title_left')

list_item_title_right = dbc.ListGroupItem(html.Div([
    html.Br(),
    html.H4("Recommanded Foods: "),
    html.P("Do you know balanced diet also plays an crucial role in prompting healthy skin? ", className="lead", style={"font-size": "12px"}),
    ]), id = 'list_item_title_right')
list_group_title_right = dbc.ListGroup(list_item_title_right, class_name='list-group-item-info mb-4', id = 'list_group_title_right')


# map:
map_function = dl.Map([
    dl.TileLayer(), 
    dl.Marker(id = 'Mecca_marker', position = [-33.8707636948296, 151.20703194187925], children = [dl.Popup(children = html.Div([
                                                                                        
                                                                                            html.B("This is Mecca George Street!", id = 'Mecca_0'),
                                                                                            html.Br(),
                                                                                            html.Br(),
                                                                                            html.B('Opening Hours:'),
                                                                                            html.P('10 am - 6 pm (Mon. Tues. Wed. Fri. Sat.)', id = 'Mecca_OH_1'),
                                                                                            html.P('10 am - 9 pm (Thurs.)', id = 'Mecca_OH_2'),
                                                                                            html.P('10 am - 5 pm (Sun.)', id = 'Mecca_OH_3'),
                                                                                        ]),
                                                                                       )]
              ),# Mecca sydney flagship store   
                                                                                         
                                                                                                                                                                             
                                                                                  
    dl.Marker(id = 'Sephora_marker', position = [-33.865902656473736, 151.20779418422347], children = [dl.Popup(children = html.Div([
                                                                                        
                                                                                            html.B("This is Sephora @ Pitt Street!", id = 'Sephora_0'),
                                                                                            html.Br(),
                                                                                            html.Br(),
                                                                                            html.B('Opening Hours:'),
                                                                                            html.P('9:30 am - 7 pm (Mon. Tues. Wed. Fri.)', id = 'Sephora_OH_1'),
                                                                                            html.P('9:30 am - 9 pm (Thurs.)', id = 'Sephora_OH_2'),
                                                                                            html.P('9 am - 7 pm (Sat.)', id = 'Sephora_OH_3'),
                                                                                            html.P('10 am - 6 pm (Sun.)', id = 'Sephora_OH_4'),
                                                                                        ]),
                                                                                       )],
              ),# Sephora @ Pitt Street
    dl.FullScreenControl(),
    dl.LocateControl(id = 'User_loc', locateOptions = {'enableHighAccuracy': True}),
    ], center = [-33.87,151.207], zoom = 14, style = {'height': '50vh'})

map_card = dbc.Card([dbc.CardBody([map_function])], id = 'map_card')

# map list items
list_item_map_title = dbc.ListGroupItem(html.Div([
    html.H4('Want to Find a Local Store?'),
    html.P('click marker for more store information', className="lead", style={"font-size": "12px"}),
    ]), id = 'list_item_map_title')
list_item_map = dbc.ListGroupItem(map_card , id = 'list_item_map')
list_group_map = dbc.ListGroup([list_item_map_title, list_item_map], class_name='list-group-item-info mb-4', id = 'list_group_map')

def create_top_product_card(idx, df_):
    
    """
    Input: rank of the prodcut (1-5), skincare_dataframe
    Returns:
        dbc.Card component for single product
    """
    df = df_.reset_index(drop = True)
    
    product_name = df.Product[idx]

    # img_src
    if product_name ==  'Ascorbyl Tetraisopalmitate Solution 20% in Vitamin F':
        image_src = 'https://theordinary.com/dw/image/v2/BFKJ_PRD/on/demandware.static/-/Sites-deciem-master/default/dw64246855/Images/products/The%20Ordinary/rdn-ascorbyl-tetraisopalmitate-solution-20pct-in-vitamin-f-30ml.png?sw=1200&sh=1200&sm=fit'

    elif product_name == 'Dior snow Essence Of Light Lock & Reflect Crème':
        image_src = 'https://image-optimizer-reg.production.sephora-asia.net/images/product_images/closeup_1_Product_3348901580861-Dior-Diorsnow-Essence-Of-Light-Lock-Reflect-Creme-50ml_254199199c1f11ef9c21a69f1c003f323f2cccf8_1646117461.png'

    elif product_name == 'Lancôme Clarifique Clarifying Serum 30ml':
        image_src = 'https://www.lancome.com.au/dw/image/v2/BFZM_PRD/on/demandware.static/-/Sites-lancome-ng-master-catalog/default/dw9c9d968c/images/R_SK_L3_serums/00717-LAC/00717-LAC-4935421786508-30ml-IMAGE1.jpg?sw=750&sh=750&sm=cut&sfrm=jpg&q=70'

    else: 
        image_src = '/assets/{}.png'.format(df.Product[idx])

    product_price = df['Official_Price (AUD)'][idx]
    functionalities = df.Functionality[idx]
    product_link = df.Link[idx]

    # create card components:
    Product_name = html.H6(product_name, className = 'card_title', id = 'Top{}_product_name'.format(idx+1))
    Card_image = dbc.CardImg(id = 'top{}_image'.format(idx+1),
                                src = image_src,
                                className = 'img-fluid rounded-center center',
                                )
    Product_functionality = html.Small(functionalities, className = 'card-text .small',  id = 'Top{}_functionality'.format(idx+1))
    Product_price = html.H5('${:.2f}'.format(product_price),className = 'card-text text-center', id ='Top{}_price'.format(idx +1))
    Price_note = html.P('Official Price in AUD',className = 'card-text text-center small text-muted', id ='Top{}_price_note'.format(idx +1))
    Product_button = dbc.Button('Purchase Online', className='me-1',color = 'info', outline = True, id = 'Top{}_link'.format(idx+1), href = product_link)

    # construct card
    card = dbc.Card([   
        dbc.Row([
                dbc.Col([
                    Card_image,
                    html.Br(),
                    html.Br(),
                    Product_price,
                    Price_note,
                    
                ], className = 'col-md-4', align = 'center',),
                
                dbc.Col(
                    dbc.CardBody([
                            Product_name,
                            Product_functionality,
                            html.Br(),
                            html.Br(),
                            Product_button,
                    ]),
                className = 'col-md-8 '
                )
        ], justify = 'center',)
    ])
    
    # ref: https://dash-bootstrap-components.opensource.faculty.ai/docs/components/card/
    
    return card

# list product：

# define ListGroupItems:
list_group_item_0 = dbc.ListGroupItem(html.Div([html.H4('Top 5 products: '),
                                                html.Small('(ranked by review scores)', className="lead", style={"font-size": "12px"})]), id = 'product_heading')
list_group_item_1 = dbc.ListGroupItem(create_top_product_card(0, SkinCare_df_age_CS_Top5), id = 'list_product_1')
list_group_item_2 = dbc.ListGroupItem(create_top_product_card(1, SkinCare_df_age_CS_Top5), id = 'list_product_2')
list_group_item_3 = dbc.ListGroupItem(create_top_product_card(2, SkinCare_df_age_CS_Top5), id = 'list_product_3')
list_group_item_4 = dbc.ListGroupItem(create_top_product_card(3, SkinCare_df_age_CS_Top5), id = 'list_product_4')
list_group_item_5 = dbc.ListGroupItem(create_top_product_card(4, SkinCare_df_age_CS_Top5), id = 'list_product_5')


# define list group
list_top5_products= html.Div(
    [
        # html.H4('Top 5 products: '),
        dbc.ListGroup(
        [
            list_group_item_0,
            list_group_item_1,
            list_group_item_2,
            list_group_item_3,
            list_group_item_4,
            list_group_item_5,
        ],
        id = 'top_products_list', class_name='list-group-item-info mb-4'
        )
    ]
)



# app layout ------------------------------------------------------------------------------------------
app.layout = dbc.Container(
    html.Div([
        dbc.Row(
            [
                # first row, first col
                dbc.Col([
                    html.Br(),
                    list_group_title_left], md=4),

                # first row, sec column -- User input
                dbc.Col([
                    html.Br(),
                    html.Div([
                        "Solve Your Skin Issue? ", skin_issue,]),
                    html.Div([
                        "Select a Product Type", product_type,]),
                    html.Br(),
                    df_storage_SkinCare,
                    df_storage_Food,
                ], md=4),

                # first row, third col
                dbc.Col([
                    html.Br(),
                    list_group_title_right] , md=4),   
            ], align='start'
        ),
        
        dbc.Row([
            # second row, first col -- Scatter plot and Span Chart
            dbc.Col([
                # title_card,
                dbc.ListGroup(id = 'plot_list'),
                # html.H4('Check Store Location'),
                list_group_map,
                ], md=4),
                
                # dbc.Col(dbc.Card(id='scatter_plot_card', className="mb-4")),
                # dbc.Col(dbc.Card(id='line_plot_card', className="mb-4"))]),

            # second row, second col --- Ranking Top 5 Products
            dbc.Col([
                    list_top5_products, 
                    html.Br(),
                    html.Br(),], md=4),

            # second row, third col
            dbc.Col(dbc.ListGroup(id = 'list_group_food'), md=4), 
        ]),
        
    ])
)


#Callbacks---------------------------------------------------------------------------------------------

# update df_subset -- store
@app.callback(
    Output(df_storage_SkinCare, component_property='data'),
    Input(skin_issue, component_property='value'),
    Input(product_type, component_property='value')
)

def df_update(skin_issue, product_type):
    if skin_issue and product_type:
        SCP_df = SkinCareProduct_df.loc[(SkinCareProduct_df['Skin_Issue'] == skin_issue) & (SkinCareProduct_df['Type'].isin(product_type)), :]

        #ref:  https://community.plotly.com/t/storing-a-dataframe-in-dcc-store/56230
        return {'data-frame': SCP_df.to_dict('records')}
    
    raise PreventUpdate

@app.callback(
    Output(df_storage_Food, component_property='data'),
    Input(skin_issue, component_property='value'),
)

def df_update(skin_issue):
    if skin_issue:
        skin_nutrition_dict = {'Brightening':['Vitamin C'], 'Acne': ['Carotene', 'Vitamin A'], 'Anti-Aging' :['Vitamin E', 'Vitamin C']}
 
        selected_nutrition = ['food'] + skin_nutrition_dict[skin_issue]
        food_df = Food_df[selected_nutrition]
        
        # print(food_df)
        
        #ref:  https://community.plotly.com/t/storing-a-dataframe-in-dcc-store/56230
        return {'data-frame': food_df.to_dict('records')}
    
    raise PreventUpdate


# section B: Rank Top 5 products:
@app.callback(
    Output(list_group_item_1, component_property='children'),
    Output(list_group_item_2, component_property='children'),
    Output(list_group_item_3, component_property='children'),
    Output(list_group_item_4, component_property='children'),
    Output(list_group_item_5, component_property='children'),
    Input(df_storage_SkinCare, component_property='data')
)

def Top_5_products(df_skincare_):
    df_skincare = pd.DataFrame(df_skincare_['data-frame'])
    df_skincare_sorted = df_skincare.sort_values(by = ['Review_Score'], ascending = False)
    df_skincare_top5 = df_skincare_sorted.head()
    
    
    card_1 = create_top_product_card(0, df_skincare_top5)
    card_2 = create_top_product_card(1, df_skincare_top5)
    card_3 = create_top_product_card(2, df_skincare_top5)
    card_4 = create_top_product_card(3, df_skincare_top5)
    card_5 = create_top_product_card(4, df_skincare_top5)
    
    return card_1, card_2, card_3, card_4, card_5



# section C and D: Plots-------------------------------------------------------------------
@app.callback(
    Output('plot_list', 'children'),
    Input(df_storage_SkinCare, component_property='data'),
    Input('input_product_type', 'value'), 
    Input('input_skin_issue', 'value')    
)


def plots_output(df_skincare_, product_type, skin_issue):  
    df_skincare = pd.DataFrame(df_skincare_['data-frame'])
    df_skincare_sorted = df_skincare.sort_values(by = ['Review_Score'], ascending = False)
    df_skincare_top5 = df_skincare_sorted.head()
    
    if not isinstance(product_type, list):
        product_type = [product_type] 
        
    SCP_df = SkinCareProduct_df.loc[(SkinCareProduct_df['Skin_Issue'] == skin_issue)
                                & (SkinCareProduct_df['Type'].isin(product_type)), :]
    SCP_df_sorted = SCP_df.sort_values(by=['Review_Score'], ascending=False)
    SCP_df_Top5 = SCP_df_sorted.head() 
    

    # Scatter plot
    scatter_fig = px.scatter(SCP_df_Top5, x='Review_Score', y='Review_Number', hover_name='Product', template="simple_white")
    scatter_fig.update_traces(marker=dict(size=12),
                  selector=dict(mode='markers'))

    # https://plotly.com/python/marker-style/
    scatter_fig.update_layout(
        autosize=True,
        width=None,
        height=450,
        margin=dict(
        l=20,
        r=50,
        b=50,
        t=100,
        pad=4
    ),)

    # Scatter Plot Card
    scatter_card = dbc.Card(
        dbc.CardBody(
            [
                html.H4("Scatter Plot for Reviews", className="card-title"),
                html.Br(),
                dcc.Graph(figure=scatter_fig, id='scatter_plot')
            ]
        ), className="mt-4"
    )
    
    # Line Plot for different Seasons
    line_chart = go.Figure()

    Seasons = ['Season_1', 'Season_2', 'Season_3', 'Season_4']
    for product in SCP_df_Top5['Product']:
        product_prices = SCP_df_Top5[SCP_df_Top5['Product'] == product]
        line_chart.add_trace(
            go.Scatter(x=Seasons, y=product_prices[Seasons].iloc[0].values, name=product)
        )

    line_chart.update_layout(
        title={
        'text': "Average Price Changes Across Seasons ",
        'y':1.0,  
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
        yaxis_title='Price (AUD)',
        xaxis_title='Seasons',
        xaxis=dict(tickangle=90),
        autosize=True,
        width=None,
        height=500,
        margin=dict(
            l=20,
            r=50,
            b=50,
            t=100,
            pad=4
            ),
        legend_orientation="h",  
        legend=dict(x=0.5, y=1.05, xanchor='center', yanchor='bottom',
        font=dict(size=10) )  
        )

    
    # Line Plot Card
    line_card = dbc.Card(
        dbc.CardBody(
            [
                html.H4("Line Plot for Prices", className="card-title"),
                html.Br(),
                dcc.Graph(figure=line_chart, id='line_plot')
            ]
        )
    )

    # listgroup ----
    
    plot_list_group = html.Div([
        
        
        dbc.ListGroup(
            [
                dbc.ListGroupItem(scatter_card, id = 'list_scatter'),
                dbc.ListGroupItem(line_card, id = 'list_line'),
            ], id = 'plot_list', class_name = 'list-group-item-info mb-4'
        )
    ])
        
    

    return  plot_list_group  #scatter_card, line_card

    
# Section E &F----------------------------------------------------------------
@app.callback(
    Output('list_group_food', 'children'),
    [Input(df_storage_Food, component_property='data'),
     Input('input_skin_issue', 'value')]
)

def recommend_foods(food_data, selected_skin_issue):
    if not food_data or not selected_skin_issue:
        raise PreventUpdate

    # Convert the stored data to dataframe
    temp_food_df = pd.DataFrame(food_data['data-frame'])
    all_vitamins = [col for col in Food_df.columns if col != 'food']

    # Find the top 5 foods for the selected skin issue's vitamins
    recommended_foods = set()
    vitamins_for_skin_issue = skin_nutrition_dict[selected_skin_issue]
    for vitamin in vitamins_for_skin_issue:
        top_5_foods_for_vitamin = temp_food_df.nlargest(5, vitamin)
        recommended_foods.update(top_5_foods_for_vitamin['food'].tolist())

    # Extract these foods from the original Food_df
    recommended_foods_df = Food_df[Food_df['food'].isin(recommended_foods)]

    # Calculate the vitamin percentage for each food
    recommended_foods_df[all_vitamins] = recommended_foods_df[all_vitamins].div(recommended_foods_df[all_vitamins].sum(axis=1), axis=0) * 100

    # Displaying the recommended food names and images
    food_title = f"Top recommended food in {', '.join(vitamins_for_skin_issue)}"

    food_display = []
    food_display.append(html.H4(food_title, className="card-title"))#mt-3 mb-4 
    for food in recommended_foods:
        food_display.append(html.Div([
            html.Img(src=f'assets/{food}.png', style={'width':'100px', 'height':'100px'}),
            html.P(food)
        ], style={'display': 'inline-block', 'margin':'10px'}))
    
    # Create the stacked bar chart
    traces = []
    for vitamin in all_vitamins:
        traces.append(go.Bar(
            x=recommended_foods_df['food'],
            y=recommended_foods_df[vitamin],
            name=vitamin
        ))

    layout = go.Layout(
        barmode='stack',
        title='Vitamin Distribution in Recommended Foods',
        xaxis_title='Food',
        yaxis_title='Percentage'
    )
    fig = go.Figure(data=traces, layout=layout)
    fig.update_layout(
        title_font_size = 15,
        xaxis=dict(tickangle=90),
        autosize=True,
        # width=363,
        # height=550,
        margin=dict(
        l=1,
        r=1,
        b=50,
        t=100,
        pad=4
    ),)

    # recommended_foods_list = [html.H5("Recommended Foods", className="card-title")] + food_display + [dcc.Graph(figure=fig)]

    # return dbc.Card(
    #     dbc.CardBody(recommended_foods_list),
    #     className="mt-4"
    #     )
    
    # create cards
    food_nurient_card = dbc.Card(
        dbc.CardBody(food_display),
        className="mt-4", id = 'food_nurient_card'
        )
    
    food_plot_card = dbc.Card(
        dbc.CardBody(
            [dcc.Graph(
                figure=fig, config = {'responsive': True}
                )
            ]),
        className="mt-4", id = 'food_plot_card'
        )
    
    # create list_group_items
    list_group_item_food_nurient = dbc.ListGroupItem(food_nurient_card, id = 'list_group_item_food_nurient')

    list_group_item_food_plot = dbc.ListGroupItem(food_plot_card, id = 'list_group_item_food_plot')
    
    
    list_group_food = dbc.ListGroup(
        [
            list_group_item_food_nurient,
            list_group_item_food_plot
        ], id = 'list_group_food', class_name = 'list-group-item-info mb-4' )

    
    return list_group_food


if __name__ == '__main__':
    app.run_server(debug = True)
