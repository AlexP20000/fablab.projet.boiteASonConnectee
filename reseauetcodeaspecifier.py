#Auteur : Varoquier Guillaume
#Version : 1.9.5
#Date : 21 mai 2019
#Support : PYCOM WIPY et Expansion board 3.1
#Description du code :
#Le processus, hormis la connexion, se répète indéfiniment, jusqu'à l'épuisement de la batterie ou à la deconnexion du port usb de l'ordinateur
#Etape 1 : ajout des libraires, déclaration et initialisation des variables
#Etape 2 : initialisation du réseau, du serveur et de la socket de communication
#Etape 3 : récupération et traitement des données collectées via le sound sensor
#Etape 4 : Au bout d'une minute, envoi des données collectées
    #Etape 5 : Récupération et traitement des données lues pour la puissance restante de la batterie

#Etant majoritairement designé pour une lecture par serveur, les print ne sont pas présents dans ce code car inutiles. Libre à vous de les ajouter pour faciliter la compréhension du code ou pour la mise en avant d'erreurs

#ETAPE 1

#Ajout des librairies
import machine
import network
import os
import pycom
import socket
import sys
import time
from machine import Pin
from network import WLAN

#Pins pour la lecture analogue des valeurs envoyées par le sound sensor et pour la capacité restante de la batterie
adc = machine.ADC()             # création d'un objet ADC pour la lecture des valeurs envoyées par le sensor
bAdc = machine.ADC()            # création d'un objet ADC pour la lecture de la capacité restante de la batterie
    #Assignation aux pins
apin = adc.channel(pin='P20')
bApin= bAdc.channel(pin='P19')

#Pins pour la visualisation de la capacité restante de la batterie
pinBattery100=Pin('P22',mode=Pin.OUT)
pinBattery75=Pin('P2',mode=Pin.OUT)
pinBattery50=Pin('P3',mode=Pin.OUT)
pinBattery25=Pin('P4',mode=Pin.OUT)
pinBattery0=Pin('P5',mode=Pin.OUT)

#Pins pour la visualisation du niveau sonore ambiant
pinLow = Pin('P6', mode=Pin.OUT)
pinAverage = Pin('P7', mode=Pin.OUT)
pinAverageBis = Pin('P8', mode=Pin.OUT)
pinHigh = Pin('P9', mode=Pin.OUT)
pinHighBis = Pin('P10', mode=Pin.OUT)
pinEarDamage = Pin('P11', mode=Pin.OUT)
pinEarDamageBis = Pin('P12', mode=Pin.OUT)

#Variables de stockage pour le sound sensor
stock = 0.0 #somme de toutes les valeur captées toutes les 20 millisecondes pendant 1 seconde
sstock = 0.0 #moyenne de toutes les valeur captées toutes les 20 millisecondes pendant 1 seconde
mstock = 0.0 #somme de toutes moyennes des secondes pendant 1 minute
smstock = 0.0 #moyenne de toutes moyennes des secondes pendant 1 minute
scount = 0 #variable de compte du nombre de secondes passées
sendmstock = 0.0 #variable de stockage envoyée au serveur InfluxdB

#Variables de stockage pour la connexion Internet
UDP_IP="<adresse Ip>" #adresse ip de la base InfluxdB
UDP_PORT=<n°port> #port de connexion de la base InfluxdB pour une utilisation du protocole UDP


#ETAPE 2
#initialisation du réseau

    # Duplication de la sortie sur l'UART
uart = machine.UART(0, 115200)
os.dupterm(uart)

# Désactivation du telnet et du serveur FTP avant de se connecter au serveur

server = network.Server()
server.deinit()

# Connexion au  WLAN
wlan = network.WLAN()
wlan = network.WLAN(mode=network.WLAN.STA)
wlan.connect('<nom du reseau>', auth=(WLAN.WPA2, '<mot de passe>'),timeout=5000)
while not wlan.isconnected():
      machine.idle() # economie d'énergie durant l'attente

# Active le telnet et le serveur FTP avec de nouveaux paramètres

# Vous allez devoir mettre à jour votre Atom avec ce login et ce mot de passe
server.init(login=('micro', 'python'), timeout=600)

#Attendez quelques instants avant de continuer
time.sleep(5)

#Desactivation du clignotement de la Led sur la Pycom WIPY
pycom.heartbeat(False)

#Création de la socket de communication
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

#Confirmation visuelle de la bonne connexion au réseau souhaité

pinBattery100.value(0)
pinBattery75.value(0)
pinBattery50.value(0)
pinBattery25.value(0)
pinBattery0.value(0)
pinEarDamageBis.value(0)
pinEarDamage.value(0)
pinHighBis.value(0)
pinHigh.value(0)
pinAverageBis.value(0)
pinAverage.value(0)
pinLow.value(0)

pinEarDamage.toggle()
pinEarDamageBis.toggle()
time.sleep(1)
pinHigh.toggle()
pinHighBis.toggle()
time.sleep(1)
pinAverage.toggle()
pinAverageBis.toggle()
time.sleep(1)
pinLow.toggle()
time.sleep(1)
pinBattery0.toggle()
time.sleep(1)
pinBattery25.toggle()
time.sleep(1)
pinBattery50.toggle()
time.sleep(1)
pinBattery75.toggle()
time.sleep(1)
pinBattery100.toggle()
time.sleep(1)
pinEarDamage.toggle()
pinEarDamageBis.toggle()
time.sleep(1)
pinHigh.toggle()
pinHighBis.toggle()
time.sleep(1)
pinAverage.toggle()
pinAverageBis.toggle()
time.sleep(1)
pinLow.toggle()
time.sleep(1)
pinBattery0.toggle()
time.sleep(1)
pinBattery25.toggle()
time.sleep(1)
pinBattery50.toggle()
time.sleep(1)
pinBattery75.toggle()
time.sleep(1)
pinBattery100.toggle()
time.sleep(1)

#ETAPE 3
while True:#boucle infinie

    for i in range(50):#représentation d'une seconde
        val = apin() #lecture de la valeur au pin 20
        valmap=(val - 0) * (150 - 0) / (4095 - 0) + 0 #mappage de la valeur lue
        stock+=valmap# on ajoute la valeur mappée lue à stock
        time.sleep(0.02)#on attend 0,02 secondes

    sstock=stock/50.0#on récupère la moyenne des 50 relevés pour avoir la valeur d'une seconde

    if sstock<=50.0:# Niveau sonore calme
        pinLow.value(1)
        pinAverage.value(0)
        pinAverageBis.value(0)
        pinHigh.value(0)
        pinHighBis.value(0)
        pinEarDamage.value(0)
        pinEarDamageBis.value(0)

    elif sstock<=80.0:#niveau sonore moyen
        pinLow.value(0)
        pinAverage.value(1)
        pinAverageBis.value(1)
        pinHigh.value(0)
        pinHighBis.value(0)
        pinEarDamage.value(0)
        pinEarDamageBis.value(0)

    elif sstock<120.0:#niveau sonore haut, mise en place du réflexe stapédien
        pinLow.value(0)
        pinAverage.value(0)
        pinAverageBis.value(0)
        pinHigh.value(1)
        pinHighBis.value(1)
        pinEarDamage.value(0)
        pinEarDamageBis.value(0)

    else:#niveau sonore douloureux
        pinLow.value(0)
        pinAverage.value(0)
        pinAverageBis.value(0)
        pinHigh.value(0)
        pinHighBis.value(0)
        pinEarDamage.value(1)
        pinEarDamageBis.value(1)

    mstock+=sstock # on ajoute la moyenne obtenue à mstock
    stock=0.0 #on réinitialise stock pour la prochaine seconde
    sstock=0.0 #on réinitialise sstock pour la prochaine seconde
    scount += 1 #on incrémente scount de 1 pour marquer la seconde passée

#ETAPE 4
    if scount==60:# si une minute est passée

        smstock=mstock/60.0#on affecte la moyenne de mstock à smstock

        #Syntaxe Line Protocol :
        #nom_mesure[,tag_key=)value[...]] field_key=field_value[,...]
        message="<1>,<2>"+str(smstock)#On prépare le message à être envoyé

        #On remet mstock et scount à 0 pour ne pas interférer dans la prochaine minute

        mstock=0.0
        scount=0

        #On envoit le message à la base InfluxdB
        sock.sendto(message, (UDP_IP, UDP_PORT))

        #Une fois le son capté, on regarde le niveau de batterie

#ETAPE 5
        bval=bApin()#lecture de la valeur au pin 19
        bvalmap=((bval/4095)*100) #mise en pourcentage de la valeur lue

        if bvalmap<=10.0:#le niveau de batterie est très faible
            pinBattery0.value(1)
            pinBattery25.value(0)
            pinBattery50.value(0)
            pinBattery75.value(0)
            pinBattery100.value(0)

        elif bvalmap<=25.0:#Il reste un quart de la batterie
            pinBattery0.value(0)
            pinBattery25.value(1)
            pinBattery50.value(0)
            pinBattery75.value(0)
            pinBattery100.value(0)

        elif bvalmap<=50.0:#la moitié de la batterie a été consommée
            pinBattery0.value(0)
            pinBattery25.value(1)
            pinBattery50.value(1)
            pinBattery75.value(0)
            pinBattery100.value(0)

        elif bvalmap<=75:#Il reste les trois quarts de la batterie
            pinBattery0.value(0)
            pinBattery25.value(1)
            pinBattery50.value(1)
            pinBattery75.value(1)
            pinBattery100.value(0)

        else:#la batterie est chargée ou très haute
            pinBattery0.value(0)
            pinBattery25.value(1)
            pinBattery50.value(1)
            pinBattery75.value(1)
            pinBattery100.value(1)

#Nouvelle itération de la boucle while
