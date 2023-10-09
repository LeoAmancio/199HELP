import json
import os
from flask import Flask, jsonify, make_response,request, render_template
from flask_cors import CORS
from twilio.rest import Client

from gdacs.api import GDACSAPIReader

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api', methods=['GET', 'POST'])
def datas():
    data = request.form.to_dict(flat=False)

    country = ""
    state = ""
    city = ""
    phone = ""
    try:
        json_string = list(data.keys())[0]
        parsed_data = json.loads(json_string)

        if 'country' in parsed_data:
            country = parsed_data['country']

        if 'state' in parsed_data:
            state = parsed_data['state']

        if 'city' in parsed_data:
            city = parsed_data['city']

        if 'phone' in parsed_data:
            phone = parsed_data['phone']

        if 'location' in parsed_data:
            location = parsed_data['location']
    except Exception as e:
        print(e)
        print('no data')



    client = GDACSAPIReader()

    fl_events = client.latest_events(limit=1000)

    features= fl_events.features

    feature = None

    print(feature)

    if location != None:

        for feat in features:

            split = location.split(",")
            lat_location = split[0]
            long_location = split[1]

            cordenadas = feat["geometry"]["coordinates"]
            latitude = cordenadas[0]
            longitude = cordenadas[1]

            if latitude == lat_location and longitude == long_location:
                feature = feat
                break

    if feature is None:
        feature = features[0]

    episodealertlevel = feature["properties"]["episodealertlevel"]

    country = feature["properties"]["country"]
    fromdate = feature["properties"]["fromdate"]
    todate = feature["properties"]["todate"]

    cordenadas = feature["geometry"]["coordinates"]

    latitude = cordenadas[0]

    longitude = cordenadas[1]

    descricao = feature["properties"]["description"]

    event_type = feature["properties"]["eventtype"]

    if episodealertlevel == 'Orange' or episodealertlevel == 'Red' :
        account_sid = 'AC072b20a8e6c7b07248229937e93ab430'
        auth_token = 'e0fa5df703dbf432f51212142ceb24cf'
        client = Client(account_sid, auth_token )

    if event_type == "EQ":
             sms_message = "earthquake alert: Stay Where You Are:, Protect your neck, avoid Hazardous Areas"
    elif event_type == "FL":
            sms_message = "Floods alert: Turn off electricity and gas, Seek Higher Ground"


    autority_phone = '123456789'

    # message = client.messages.create(
    #     from_='+12055122227',
    #     body=sms_message,
    #     to=autority_phone
    # )

    response = make_response(jsonify({
        'episodealertlevel': episodealertlevel,
        'cordenadas': cordenadas,
        'latitude': latitude,
        'longitude': longitude,
        'descricao': descricao,
        'country': country,
        'fromdate': fromdate,
        'todate': todate
    }))
    return response

app.run()