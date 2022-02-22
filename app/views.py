import ctypes
from logging.handlers import BaseRotatingHandler
from smtplib import SMTPDataError
from unittest import result
from . import app
from flask import request, json, jsonify
from ctypes import *
import urllib, http.client, os

libreria_c ="/app/libreria_c.so"
parse_server_url = os.environ['PARSE_SERVER_URL']
paser_server_aplication_id = os.environ['PARSE_SERVER_APLICATION_ID']
paser_server_master_key = os.environ['PARSE_SERVER_MASTER_KEY']

fun_libreria_c = CDLL(libreria_c)

fun_libreria_c.descifrado.restype=c_char_p

fun_libreria_c.freeme.argtypes=c_void_p,
fun_libreria_c.freeme.restype=None

def updatedata(objectId,data):
    sendata = str("longitud = " + str(data[0]) + " latitud = " + str(data[1]) + " altitud = " + str(data[2]) + " bearing = " + str(data[3]) + " speed = " + str(data[4]))
    print("sendata = " + sendata)
    connection = http.client.HTTPSConnection(parse_server_url, 443)
    connection.connect()
    connection.request('POST', '/parse/classes/Ubicacion', json.dumps({
       "Longitud": data[0],
       "Latitude": data[1],
       "Altitude": data[2],
       "Bearing": data[3],
        "Speed": data[4],
     }), {
        "X-Parse-Application-Id": paser_server_aplication_id,
        "X-Parse-Master-Key": paser_server_master_key,
        "Content-Type": "application/json"
     })
    results2 = json.loads(connection.getresponse().read())
    print("result2 =" +str(results2) )
    print("objetId"+ str(results2["objectId"]))
    connection.request('PUT', '/parse/classes/Rastreo/' + str(objectId),
    json.dumps({
      "UbicacionUsuario": {
        "__type": "Pointer",
        "className": "Ubicacion",
        "objectId": results2["objectId"]
      }, 
      "decript":str(sendata)
      }),{
          "X-Parse-Application-Id": paser_server_aplication_id,
          "X-Parse-Master-Key": paser_server_master_key,
          "Content-Type": "application/json"
      })
    result =json.loads(connection.getresponse().read().decode())  
    print("result = " + str(result))
    
    return 0

def string_hex_to_binary_string(s):
    base=["0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F"]
    hexa=["0000","0001","0010","0011","0100","0101","0110","0111","1000","1001","1010","1011","1100","1101","1110","1111"]
    start=s.upper()
    data=""
    for i in range(0,20):
        for j in range(0,len(base)):
            if(start[i]==base[j]):
                data=str(data)+str(hexa[j])
    return data

def decodemsg(msg):
   #
   #    signo longitud -         longitud       - signolatitud -          latitud         -     altitud      -    bearing    -  speed   - notuse
   #    |       0      - 0000000|00000000|00000 -       0      - 00|00000000|00000000|000 - 00000|00000000|0 - 0000000|00000 - 000|0000 - XXXX|
   #bytes              0              1                  2              3         4         5           6         7            8         9
   #    |       0      - 1234567|89012345|67890 -       1      - 23|45678901|23456789|012 - 34567|89012345|6 - 7890123|45678 - 901|2345 - XXXX|
   #    |       0                  1          2                           3           4             5             6             7
    binary_string=string_hex_to_binary_string(msg)
    #print("hexadecimal = " + str(msg) + " binario = " + str(binary_string) + " longitud = " + str(len(binary_string)))
    signolongitud=binary_string[0]    
    slongitud=binary_string[1:22]
    signolatitud=binary_string[22]
    slatitud=binary_string[23:43]
    saltitud=binary_string[43:57]
    sbearing=binary_string[57:69]
    sspeed=binary_string[69:76]

    longitud=int(slongitud,2)
    longitud=longitud*0.0001
    if(signolongitud=="1"):
        longitud=-longitud
    latitud=int(slatitud,2)
    latitud=latitud*0.0001
    if(signolatitud=="1"):
        latitud=-latitud
    altitud=int(saltitud,2)
    bearing=int(sbearing,2)
    bearing=bearing*0.1
    speed=int(sspeed,2)
    speed=speed*0.1
        
    #print("hola")
    return [longitud,latitud,altitud,bearing,speed]

def decript(idUsuario,MensajeUsuario,nMensaje):
    try:
        connection = http.client.HTTPSConnection(parse_server_url, 443)
        params = urllib.parse.urlencode({"where":json.dumps({
            "UserID": str(idUsuario)
            }),"limit":1})
        connection.connect()
        connection.request('GET', '/parse/classes/DatosUsuarios?%s' % params, '', {
            "X-Parse-Application-Id": paser_server_aplication_id,
            "X-Parse-Master-Key": paser_server_master_key
        })
        jsonfileee = connection.getresponse().read()
        result = json.loads(jsonfileee.decode("utf-8")) 
        Mackey32 = result['results'][0]['Mackey32']
        CifradoKey88 = result['results'][0]['CifradoKey88']
        MensajeUsuario = str(MensajeUsuario.replace("-","")).upper()
        descifrado = fun_libreria_c.descifrado(c_char_p(Mackey32.encode('utf-8')),len(Mackey32),c_char_p(CifradoKey88.encode('utf-8')),len(CifradoKey88),c_char_p(MensajeUsuario.encode('utf-8')),len(MensajeUsuario),nMensaje)
        mdescif = c_char_p(descifrado).value
        mdescif = mdescif[0:20]
        smdescif = mdescif.decode('ascii')
        
        if("Error mac" == str(smdescif)):
            raise "Error mac"
        #print("descifrado = " + str(smdescif))
        #fun_libreria_c.freeme(descifrado)
        data = decodemsg(smdescif)
        print("longitud = " + str(data[0]) + " latitud = " + str(data[1]) + " altitud = " + str(data[2]) + " bearing = " + str(data[3]) + " speed = " + str(data[4]))
        return data
    except Exception as e : 
        print('EXCEPTION decript:' + str(e))
        return  ('Erro proccessing')


def process(objectId,idUsuario,MensajeUsuario,nMensaje):
    updatedata(objectId, decript(idUsuario,MensajeUsuario,nMensaje))
    return 0

@app.route('/')
def hello():
    #print(f'hello')
    return 'Webhooksaaqaa with Python'



@app.route('/',methods=['POST'])
def decri():
    try:
        datos = request.get_json() 
        if(datos["object"]["decript"]=="NULL"):
            process(datos["object"]["objectId"],datos["object"]["idUsuario"],datos["object"]["MensajeUsuario"],datos["object"]["nMensaje"])
            print("exito")
        return jsonify({'success':'ok'})
    except Exception as e : 
        print('EXCEPTION:' + str(e))
        return jsonify({'error':'Error proccessing'})




