import datetime
from pydoc import classname
from dash import Dash, callback_context
#import dash_core_components as dcc
#import dash_html_components as html
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import flask
import base64
from PIL import Image
from io import BytesIO
import hashlib

# import plotly.express as px
clicked = 0
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = flask.Flask(__name__)
app = Dash(__name__, external_stylesheets=external_stylesheets, server=server)

imgs = []

def binary_to_img(binary_string):
    """
    Decoder string base64 to Image and get hash
    :param base64_string:
    :return:
    """
    img = Image.open(BytesIO(binary_string))
    # arr = np.asarray(img)
    img_hash = hashlib.sha256(img.tobytes())
    return img, img_hash.hexdigest()

def img_to_binary(img: Image):
    """
    Encoder image to string base64 and get hash
    :param image:
    :return:
    """
    output = BytesIO()
    img.save(output, format='JPEG')
    hex_data = output.getvalue()
    return hex_data

app.layout = html.Div([
    dcc.Upload(
        id='upload-image',
        children=html.Div([
            'Перенесите сюда или ',
            html.A('выберите файлы')
        ]),
        style={
            'width': '99%',
            'height': '100px',
            'lineHeight': '100px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px',
            'align-content': 'center',
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-image-upload'),
    # html.Button('Найти', id='button-1', style={'align-content': 'center'}, n_clicks=0),
    # html.Div('ghb', id='my-output', style={'visibility': 'hidden'})
    html.Div(id='old-images-cards'),
])


def func(contents):
    # image, _ = binary_to_img(contents)
    # print(image)
    # b64_string, _ = img_to_binary(image)
    num_warls = 5
    return contents, num_warls


def parse_contents(contents, filename):
    
    updated_contents, num_warls = func(contents)

    return html.Div([
        html.Div(className='row', children=[
            html.H5(f'Название файла: {filename}', style={'textAlign': 'center'}, className='column'), 
            html.H5(f'Моржей обнаружено: {num_warls}', style={'textAlign': 'center'}, className='column')
            ]),
        # html.H6(datetime.datetime.fromtimestamp(date)),

        # HTML images accept base64 encoded strings in the same format
        # that is supplied by the upload
        html.Div(className='row', children=[html.Img(src=contents, className='column'), html.Img(src=updated_contents, className='column')]),
        # dcc.Graph(id="image", figure=img_to_figure(contents)),
        html.Hr(),
        #html.Div('Raw Content'),
        # html.Pre(contents[0:200] + '...', style={
        #     'whiteSpace': 'pre-wrap',
        #     'wordBreak': 'break-all'
        # })
    ])
    

def old_images(contents, filename):
    imgs.append((contents, filename))

    cards = []
    for c, f in imgs:
        cards.append(dbc.Col(
            html.Button(id='submit-b', n_clicks=0, className='imgbtn',
                children=[html.Div(dbc.CardImg(src=c, class_name='sqimg',)), f,], 
                        ), style={"margin-right": "10px", "margin-left": "10px"}))
    cards = dbc.Row(cards)

    return cards


@app.callback(
    Output('output-image-upload', 'children'), 
    Output('old-images-cards', 'children'),
    Input('upload-image', 'contents'),
    State('upload-image', 'filename'))

def update_output(list_of_contents, list_of_names):
    if list_of_contents is not None:
        card = old_images(list_of_contents[0], list_of_names[0])

        children = parse_contents(list_of_contents[0], list_of_names[0])

        return children, card
    return None, None


# @app.callback(Output('output-image-upload', 'children'),
#               Input('button-1', 'n_clicks'),
#               Output('output-image-upload', 'children'))              
# def on_click(n_clicks, children):
#     print(n_clicks)
#     if children is not None:
#         new_children = [children[0], children[0]]
#         return new_children


# @app.callback(Output('output-image-upload', 'children'),
#               Input('button-1', 'n_clicks'),
#               State('upload-image', 'filename'))              
# def on_click(list_of_contents, list_of_names):
#     if list_of_contents is not None:
#         children = [
#             parse_contents(c, n, 'visible') for c, n in
#             zip(list_of_contents, list_of_names)]
#         return children 


@server.route('/test', methods=['POST'])
def req():
    print('Request triggered!')  # For debugging purposes, prints to console

    return flask.redirect(flask.request.url)  # Should redirect to current page/ refresh page


if __name__ == '__main__':
    app.run_server(debug=True)