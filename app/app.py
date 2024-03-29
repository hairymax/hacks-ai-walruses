from dash import Dash, callback_context, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import base64
from PIL import Image
from io import BytesIO
import hashlib
from nn import WarlModel
from dash.exceptions import PreventUpdate
import os

img_path = './images/'
os.makedirs(img_path, exist_ok=True)

# Переменные nnDetection
checkpoint = '/home/hm/ml/hack-ai-walruses/app/checkpoints/cascade_mask_rcnn_x101_32x4d_fpn_1x_epoch_36.pth'
#config = '/home/hm/tmp/mmdetection/configs/mask_rcnn/mask_rcnn_x101_64x4d_fpn_1x_coco.py'
config = '/home/hm/tmp/mmdetection/configs/cascade_rcnn/cascade_mask_rcnn_x101_32x4d_fpn_1x_coco.py'
model = WarlModel(checkpoint=checkpoint, config=config)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets,
           prevent_initial_callbacks=True)

imgs = [(None, None, None, None), (None, None, None, None), (None, None, None, None), (None, None, None, None), (None, None, None, None)]

current_img = (None, None, None, None)



def old_images():
    global current_img, imgs
    imgs.insert(0, current_img)

    if len(imgs) > 5:
        imgs.pop(-1)

    vis = 'visible'
    cards = []

    for i in range(len(imgs)):
        c = imgs[i][0]
        f = imgs[i][1]
        if f is None:
            vis = 'hidden'
        cards.append(dbc.Col(
            html.Button(id=str(i)+'-button', className='imgbtn',
                        children=[html.Div(dbc.CardImg(
                            src=c, className='sqimg',)), f, ],
                        ), style={"margin-right": "10px", "margin-left": "10px", 'visibility': vis}))
        vis = 'visible'

    cards = html.Div([html.Hr(), dbc.Row(cards)])

    return cards


def old_images_same():
    global imgs
    vis = 'visible'
    cards = []
    for i in range(len(imgs)):
        c = imgs[i][0]
        f = imgs[i][1]
        if f is None:
            vis = 'hidden'
        cards.append(dbc.Col(
            html.Button(id=str(i)+'-button', className='imgbtn',
                        children=[html.Div(dbc.CardImg(
                            src=c, className='sqimg',)), f, ],
                        ), style={"margin-right": "10px", "margin-left": "10px", 'visibility': vis}))
        vis = 'visible'
    cards = html.Div([html.Hr(), dbc.Row(cards)])
    return cards


def b64_to_img(base64_string):
    """
    Decoder string base64 to Image and get hash
    :param base64_string:
    :return:
    """
    img = Image.open(BytesIO(base64.b64decode(base64_string)))
    img_hash = hashlib.sha256(img.tobytes())
    return img, img_hash.hexdigest()


def img_to_b64(img: Image):
    """
    Encoder image to string base64 and get hash
    :param image:
    :return:
    """
    buff = BytesIO()
    img.save(buff, format="JPEG")
    base64_string = base64.b64encode(buff.getvalue())
    img_hash = hashlib.sha256(buff.getvalue())
    return base64_string, img_hash.hexdigest()


app.layout = html.Div([
    html.H1("PytBool's моржDetection", style={'textAlign': 'center'}),
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
    dcc.Loading(
            id="loading-1",
            type="default",
            children=html.Div(id="loading-output-1"),
            fullscreen=True
        ),
    html.Div(id='output-image-upload'),
    html.Div(id='old-images-cards', children=old_images_same()),
])


def func(contents, filename):
    header, contents = contents.split(',', maxsplit=1)
    image, _ = b64_to_img(contents)
    image.save(img_path+filename,
               "JPEG", quality=100, subsampling=0)

    new_path, num_warls = model(img_path+filename)

    if new_path is not None:
        new_image = Image.open(new_path)

        b64_string, _ = img_to_b64(new_image)
        b64_string = str(header) + ',' + str(b64_string)[2:-1]

        return b64_string, num_warls
    else:
        return None, None


def parse_contents():
    global current_img

    contents, filename, _, _ = current_img
    if contents is not None:
        if current_img[2] is None and current_img[3] is None:
            updated_contents, num_warls = func(contents, filename)
            current_img = (current_img[0], current_img[1], updated_contents, num_warls)
        else:
            _, _, updated_contents, num_warls = current_img
        
        return html.Div([
            html.Div(className='row', children=[
                html.H3(f'{filename}', style={
                        'textAlign': 'center'}, className='column'),
                html.H3(f'Моржей обнаружено: {num_warls}', style={
                        'textAlign': 'center'}, className='column')
            ]),

            html.Div(className='row', children=[html.Img(src=contents, className='column'), html.Img(
                src=updated_contents, className='column')]),
            html.Div(className='row', children=[html.H6('Обозначения:', style={'padding-right':'30px'}), 
                      html.H6('Красный цвет - взрослые особи,', style={'padding-right':'30px','color':'red'}),
                      html.H6('Зелёный цвет - детёныши', style={'color':'green'})], style={'align-content': 'center'})
        ], style={'min-height': '450px'})
    else: return None


@app.callback(
    Output('output-image-upload', 'children'),
    Output('old-images-cards', 'children'),
    Output('loading-output-1', 'children'),
    Input('upload-image', 'contents'),
    Input('0-button', 'n_clicks'),
    Input('1-button', 'n_clicks'),
    Input('2-button', 'n_clicks'),
    Input('3-button', 'n_clicks'),
    Input('4-button', 'n_clicks'),
    State('upload-image', 'filename'),)
def update_output(list_of_contents, btn0, btn1, btn2, btn3, btn4, list_of_names):
    global current_img, imgs

    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if changed_id is not None and 'button' in changed_id:
        index = int(changed_id[0])
        current_img = (imgs[index][0], imgs[index][1], imgs[index][2], imgs[index][3])
        return parse_contents(), old_images_same(), btn0

    if list_of_contents is not None and 'upload-image' in changed_id:
        current_img = (list_of_contents[0], list_of_names[0], None, None)
        children = parse_contents(), btn0

        card = old_images()
        return children, card, btn0

    return parse_contents(), old_images_same(), btn0

if __name__ == '__main__':
    app.run_server(debug=False)