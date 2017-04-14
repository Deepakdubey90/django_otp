from rest_framework import viewsets
from apps.users.response import JSONResponse
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
import json, datetime
from django.conf import settings
from rest_framework.exceptions import APIException
from django.conf import settings
import mimetypes
from rest_framework import exceptions
import random

## Models
from apps.users.models import (UserDataTable,UserConfirmationCode,TwilloResponseData)

## Twillo Messeging Integration
from twilio.rest import Client as TC


## randomly get the code 
def _get_pin(length=settings.PIN_LENGTH):
    """ Return a numeric PIN with length digits """
    return random.sample(range(10**(length-1), 10**length), 1)[0]



## Phone number length validator
def clean_client_phone(client_phone):
    str(client_phone)
    try:
        if long(client_phone) and type(client_phone)==int:
            min_length = 10
            max_length = 13
            ph_length = str(client_phone)
            if len(ph_length) < min_length or len(ph_length) > max_length:
                raise ValidationError('Phone number length not valid')
    except (ValueError, TypeError):
        return False
    return True

class ValidataParameter:

    def user_signup(data):
        required_fields = ["fullname","phone_no","email","password"]
        for field in required_fields:
            if field not in data.keys():
                raise Exception({'status':"error", "field_name":field, "message":"{0} field required" .format(field) })
            elif not data.get(field):
                raise Exception({'status':"error", "field_name":field, "message":"{0} field not empty" .format(field) })
        return data
    def verify_token(data):
        required_fields = ['msid','c_token']
        for field in required_fields:
            if field not in data.keys():
                raise Exception({'status':"error", "field_name":field, "message":"{0} field required" .format(field) })
            elif not data.get(field):
                raise Exception({'status':"error", "field_name":field, "message":"{0} field not empty" .format(field) })
        return data
    def resend_token(data):
        required_fields = ["phone_no"]
        for field in required_fields:
            if field not in data.keys():
                raise Exception({'status':"error", "field_name":field, "message":"{0} field required" .format(field) })
            elif not data.get(field):
                raise Exception({'status':"error", "field_name":field, "message":"{0} field not empty" .format(field) })
        return data


def send_message(to_phone,msg):
    client = TC(settings.TWILLO_ACCOUNT_ID, settings.TWILLO_TOKEN)
    from_phone = settings.TWILLO_PHONE_NUMBER,
    message = client.messages.create(to=to_phone,from_= from_phone,body=msg)
    return message




class UserSignupView(APIView):
    def post(self,request, format=None):
        data =  request.data
        cleaned_data = ValidataParameter.user_signup(data)
        if UserDataTable.objects.filter(phone_no=cleaned_data['phone_no']):
            print ("Scxzczx")
            user = UserDataTable.objects.get(phone_no=cleaned_data['phone_no'])
            if not user.is_active:
                return JSONResponse({'status':"200","message":"Registerd User but not verified, please confirm the your phone"})
            else:
                return JSONResponse({'status':"200","message":"The Mobile number already registerd, please try with another"})
        else:
            if UserDataTable.objects.filter(username=cleaned_data['email']) and \
                UserDataTable.objects.filter(email=cleaned_data['email']):
                return JSONResponse({'status':"200","message":"User is already exist"})
            else:
                #### Confirmation code generating ####
                conf_code = _get_pin()
                ### Message Sending ###
                message = str(conf_code) + settings.MESSAGE
                message = send_message(cleaned_data['phone_no'],message)
                print (message)
                if message.__dict__.get('error_code') == None:
                    if message.__dict__['_solution']:
                        """Saving User data but the user is Inactive stage
                        Once the User confirm the token then the user will be 
                        active statge """
                        user_data = UserDataTable.objects.create(
                            full_name=cleaned_data['fullname'],
                            phone_no=cleaned_data['phone_no'],
                            active_date=datetime.datetime.utcnow(),
                            is_active=False
                            )
                        user_data.username = cleaned_data['email']
                        user_data.email = cleaned_data['email']
                        user_data.set_password(cleaned_data['password'])
                        user_data.save()
                        user_conf = UserConfirmationCode()
                        user_conf.user = user_data
                        user_conf.confirmation_code = conf_code
                        user_conf.date_created = datetime.datetime.utcnow()
                        user_conf.message_sid = message.__dict__['_solution']['sid']
                        user_conf.save()
                        msid = user_conf.message_sid
                        from_phone = message.__dict__['_properties']['from_']
                        to_phone = message.__dict__['_properties']['to']
                        tw_data = TwilloResponseData.objects.create(from_phone_no=from_phone,to_phone_no=to_phone,\
                            message_sid= msid)
                        return JSONResponse({'status':"200","msid":msid,"message":"Success"})
                else:
                    status_code = message.__dict__.get('error_code')
                    message = message.__dict__.get('error_message')
                    return JSONResponse({'status':status_code,"message":message})



class VerifyToken(APIView):
    def post(self, request,format=None):
        data = request.data
        cleaned_data = ValidataParameter.verify_token(data)
        user_token = UserConfirmationCode.objects.get(message_sid=cleaned_data['msid'])
        
        """ If need to check the code is expired plese do check the `verfication_code_expired`  
            support function"""

        # if user_token.verfication_code_expired():
            # pass
        # else:
        #     return JSONResponse({'status':400,"message":"Token got expired"})
        if user_token.is_used:
            return JSONResponse({'status':200,"message":"The confirmation code already used"})        
        if user_token.confirmation_code == cleaned_data['c_token']:
            user = UserDataTable.objects.get(id=user_token.user.id)
            mobile_no = user.phone_no
            user.is_active = True
            user.save()
            user_token.is_used = True
            user_token.save()
            return JSONResponse({'status':200,"message":str(mobile_no)+" Successfully verified"})
        else:
            return JSONResponse({'status':200,"message":"Please Enter Valid Token"})

class ResendCode(APIView):
    def post(self,request,format=None):
        data = request.data
        cleaned_data = ValidataParameter.resend_token(data)
        phone_no = data.get('phone_no')
        if not UserDataTable.objects.filter(phone_no=phone_no):
            return JSONResponse({'status':200,"message":"User doesn't exist plese signup"})
        conf_code = _get_pin()
        ### Message Sending ###
        message = str(conf_code) + settings.MESSAGE
        message = send_message(cleaned_data['phone_no'],message)
        user_data = UserDataTable.objects.get(phone_no=cleaned_data['phone_no'])
        user_conf = UserConfirmationCode()
        user_conf.user = user_data
        user_conf.confirmation_code = conf_code
        user_conf.date_created = datetime.datetime.utcnow()
        user_conf.message_sid = message.__dict__['_solution']['sid']
        user_conf.save()
        msid = user_conf.message_sid
        from_phone = message.__dict__['_properties']['from_']
        to_phone = message.__dict__['_properties']['to']
        tw_data = TwilloResponseData.objects.create(from_phone_no=from_phone,to_phone_no=to_phone,\
            message_sid= msid)
        return JSONResponse({'status':"200","msid":msid,"message":"Success"})



