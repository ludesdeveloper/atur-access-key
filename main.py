#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
from flask import Flask, jsonify, render_template, request
from datetime import date

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/accesskey', methods=['GET'])
def get_access_key():
    user_access_key = []
    iam = boto3.client('iam')
    paginator = iam.get_paginator('list_users')
    for response in paginator.paginate():
        for user in response['Users']:
            user_name = user['UserName']
            paginator_access_key = iam.get_paginator('list_access_keys')
            for access_key in paginator_access_key.paginate(UserName=user_name):
                if len(access_key['AccessKeyMetadata']) > 0:
                    for access_key_id in access_key['AccessKeyMetadata']:
                        access_key_age = access_key_id["CreateDate"]
                        age = date.today() - access_key_age.date()
                        access_key_id["Age"] = str(age.days)
                        user_access_key.append(access_key_id)
                else:
                    pass
                    # user_access_key.append({'UserName': user['UserName'], 'AccessKeyId': 'no-active-access-key',
                    #                       'Status': 'no-active-access-key', 'CreateDate': 'no-active-access-key'})
    return jsonify(user_access_key)


@app.route('/accesskey', methods=['POST'])
def delete_access_key():
    request_delete = request.json
    user_name = request_delete["userName"]
    access_key = request_delete["accessKey"]
    response = {
        "userName": user_name,
        "accessKey": access_key,
        "status": "delete"
    }
    iam = boto3.client('iam')
    iam.delete_access_key(
        AccessKeyId=access_key,
        UserName=user_name
    )
    return jsonify(response)


@app.route('/createaccesskey', methods=['POST'])
def create_access_key():
    request_create = request.json
    user_name = request_create["userName"]
    iam = boto3.client('iam')
    response = iam.create_access_key(
        UserName=user_name
    )
    return jsonify(response['AccessKey'])


if __name__ == "__main__":
    app.run(debug=True)
