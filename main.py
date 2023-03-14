from flask import Flask, request, make_response
import json
import os
from flask_cors import cross_origin
import mysql.connector
from logger import logger

app = Flask(__name__)


# geting and sending response to dialogflow
@app.route('/webhook', methods=['POST'])
@cross_origin()
def webhook():
    req = request.get_json(silent=True, force=True)

    # print("Request:")
    # print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


# processing the request from dialogflow
def processRequest(req):
    log = logger.Log()

    sessionID = req.get('responseId')

    result = req.get("queryResult")
    user_says = result.get("queryText")
    log.write_log(sessionID, "User Says: " + user_says)
    parameters = result.get("parameters")
    cust_name = parameters.get("cust_name")
    # print(cust_name)
    cust_contact = parameters.get("cust_contact")
    cust_email = parameters.get("cust_email")
    intent = result.get("intent").get('displayName')
    if (intent == 'Welcome Intent - yes'):

        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="adarsh",
            database="chatbot"
        )

        # Insert the details into the MySQL database
        cursor = db.cursor()
        sql = "INSERT INTO details (name, phone, email) VALUES (%s, %s, %s)"
        val = (cust_name, cust_contact, cust_email)
        cursor.execute(sql, val)
        db.commit()

        fulfillmentText = "Thank you , what would you like to know about 1. About us 2. All categories 3. Delivery options 4. Refund policy?"
        log.write_log(sessionID, "Bot Says: " + fulfillmentText)
        return {
            "fulfillmentText": fulfillmentText
        }
    else:
        log.write_log(sessionID, "Bot Says: " + result.fulfillmentText)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')