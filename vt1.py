
import urllib.request
import json
import random as ra

from flask import Flask, Response, request
app = Flask(__name__)

#@Jukka J

data = None
lokaatio = None
"""
url_s = "http://hazor.eu.pythonanywhere.com/2022/data2022s.json"
with urllib.request.urlopen(url_s) as resp:
    #json -> pythonin dictionary:ksi
    data = json.load(resp)
"""

def palauta_j_listaus():
    sailo = []

    for i in range(len(data["sarjat"])):
        for j in range(len(data["sarjat"][i]["joukkueet"])):
            sailo.append(data["sarjat"][i]["joukkueet"][j])

    #sisältää joukkueen lisäksi pistemäärän avaimineen
    #palauttaa joukkuelistauksen, pistejärjestyksessä
    pisteet = {"pisteet": 0}
    for i in range(len(sailo)):
        tmp = sailo[i]
        tmp.update(pisteet)
        sailo[i] = tmp
        sailo[i]["pisteet"] = laske_pisteet(sailo[i]["rastileimaukset"])

    #======================Joukkueen sisältämien dict:ien sort====================
    #sailo2 = sorted(sailo.items(), key=lambda x: x[1]["pisteet"], reverse=True)
    sailo = sorted(sailo, key=lambda d: d['pisteet'], reverse=True)
    #=============================================================================
    listaus = ""

    for i in range(len(sailo)):
        #listaus += sailo2[i]["nimi"] + " " + "(" + str(sailo2[i]["pisteet"]) + " p)" + "\n"
        listaus += sailo[i]["nimi"] + " " + "(" + str(sailo[i]["pisteet"]) + " p)" + "\n"
        for jasen in sailo[i]["jasenet"]:
            listaus += "  " + jasen + "\n"
        listaus[0:len(listaus)-1]

    """
    # taso 1
    # Jos Joukkue ei listassa, niin lisätään
    tmp = data.get("sarjat")
    for i in range(len(tmp)):
        l = tmp[i].get("joukkueet")

        for j in range(len(l)):
            tmp2 = l[j]
            jnimi = tmp2.get("nimi")
            if jnimi not in listaus:
                if jnimi is not None:
                    listaus.append(jnimi.strip() + "\n")
    # Aakkosellinen sort, ei välitä isoista tai pienistä kirjaimista
    listaus.sort(key = lambda x: x.lower())

    palautettava = ""
    for joukkue in listaus:
       palautettava += joukkue

    #return palautettava[0:len(palautettava)-1]
    """
    return listaus

#========================Tarkistin=================================
def dict_tarkistin(joukkue_dict, sarj_nimi):
   global lokaatio

   #päivitetään sarjan indeksi -> lokaatio
   for i in range(len(data["sarjat"])):

       if data["sarjat"][i]["nimi"] == sarj_nimi:
           lokaatio = i
           #print("\n", lokaatio, "\n")

   paluuarvo = True
   tarkastettavat = {"nimi", "jasenet", "id", "leimaustapa", "rastileimaukset"}
   """
   Nimen tarkistus duplikaattien varalta, jättää isot ja pienet kirjaimet huomiotta.
   Tarkistaa, ettei nimi ole tyhjä.
   Lisäksi tarkastaa rakenteen valiuden
   """

   for avain in tarkastettavat:
       if avain not in joukkue_dict:
           paluuarvo = False
           return paluuarvo
   for p in range(len(data["sarjat"])):

       for i in range(len(data["sarjat"][p]["joukkueet"])):
           nimi = "nimi"
           tmp = data["sarjat"][p]["joukkueet"][i].get(nimi).upper()
           #print(joukkue_dict.get(nimi).upper(), " -> ", tmp)
           if joukkue_dict.get(nimi).upper() == tmp:
               paluuarvo = False
               return paluuarvo

   if joukkue_dict.get(nimi).isspace():
       paluuarvo = False
       return paluuarvo

   return paluuarvo

#========================Id-generointi=============================
def lisaa_id(joukkue_dict):
    #rakenteen toistuvin lukujen num-määrä -> esim. 4882199283236864

    l1 = 1000000000000000
    l2 = 9999999999999999
    iid = ra.randint(l1, l2)

    """
    Luo satunnaisen id:n
    Tarkistaa, onko se jo olemassa
    Jos olemassa toistetaan yllä mainitut

    """

    for item in data["sarjat"][lokaatio]["joukkueet"]:
        if iid == item.get("id"):
            lisaa_id(joukkue_dict)

    joukkue_dict["id"] = iid

    #print("iidee: ", joukkue_dict["id"])
    return joukkue_dict

#==================================================================

def lisaa_joukkue(sarj_nimi, joukkue_dict):
    if dict_tarkistin(joukkue_dict, sarj_nimi) == True:
        joukkue_dict = lisaa_id(joukkue_dict)
        #dict_wrap = {(len(testi_dict) + 1): testi_dict}

        try:
            # tähän indeksi
            data["sarjat"][lokaatio]["joukkueet"].append(joukkue_dict)

        except:
            print("Ei kyseistä sarjaa")
    else:
        print("Lisättävän joukkueen rakenne on virheellinen tai joukkueen nimi ei ole kelvollinen.\n(Joukkue jo sarjassa, tai nimi tyhjä tms.)")

def palauta_int_alkavat(rak):
    sort_lista = []
    mjono = ""
    for item in rak:
        tmp = item.get("koodi")
        try:
            #kaatuu tähän, jos char paikassa nolla ei numeerinen
            print(tmp[0])
            luku = int(tmp[0])
            sort_lista.append(tmp)

        except ValueError:
            pass

    sort_lista.sort(key = lambda x: x.lower())
    for koodi in sort_lista:
        mjono += koodi + ";"

    return mjono[0:len(mjono)-1]


def muotoile(mjono, merkki, lkm):
    rivit = 10
    itr = 0
    lkoko = int(len(mjono) / (lkm + 1)) + 1
    lista = [0]*lkoko

    for i, ch in enumerate(mjono):
        if ch == merkki:
            lista[itr] += i+1
            itr += 1

    tmp = lista[1]
    #print("tmp ", tmp)
    if lista[0] < rivit:
        lista = lista[1:]
        lista = lista[::rivit]
        for i in range(len(lista)):
            lista[i] -= tmp


    for i in range(len(lista)):
        if lista[i] > rivit-1:
            mjono = mjono[:lista[i]] + "\n" + mjono[lista[i]+2:]
            #siirretään ';' esiintymien indeksejä eteenpäin
            for i in range(len(lista)):
                lista[i] += 2
    #return mjono + str(tmp)
    return "\n" + mjono

def poista_joukkue(sarja, poistettava):
    tmp = data["sarjat"]
    for item in tmp:
        if item.get("nimi") == sarja:
            for i in range(len(item["joukkueet"])):
                if item["joukkueet"][i]["nimi"].upper() == poistettava.upper():
                    item["joukkueet"].pop(i)

def lataa_data(reset):
    global data
    url_s = ""
    if reset == "reset":
        url_s = "http://hazor.eu.pythonanywhere.com/2022/data2022s.json"
        with urllib.request.urlopen(url_s) as resp:
            #json -> pythonin dictionary:ksi
            data = json.load(resp)
    else:
        with open('/home/jajoutzs/data.json', 'r') as f:
            data = json.load(f)

def tilan_tulkinta(tila, t_dict, sarja, jnimi):
    if tila == "insert":
        lisaa_joukkue(sarja, t_dict)
    elif tila == "delete":
        poista_joukkue(sarja, jnimi)
    else:
        lisaa_joukkue(sarja, t_dict)


def tarkasta_duplikaatit(esiintyneet_rastit, rasti):
    paluuarvo = True
    for ras in esiintyneet_rastit:
        if ras == rasti:
            paluuarvo = False
    return paluuarvo

#Laskee pisteet joukkueen käymien rastien ekasta merkistä, jos numeerinen ja
#vastaavuus rastit rakenteeessa
def laske_pisteet(rastileimaukset):
    pisteet = 0
    lahto = False
    maali = False
    lahto_id = 0
    maali_id = 0

    #etsitään lähdön ja maalin tunnusluku
    for k in range(len(data["rastit"])):
        if data["rastit"][k]["koodi"] == "LAHTO":
            lahto_id = int(data["rastit"][k]["id"])

        if data["rastit"][k]["koodi"] == "MAALI":
            maali_id = int(data["rastit"][k]["id"])

            #====================================
    esiintyneet_rastit = []
    for i in range(len(rastileimaukset)):
        ras_koodi = 0
        try:
            ras_koodi = int(rastileimaukset[i]["rasti"])
        except:
            pass

        #jos lähtöid löytyy, voidaan aloittaa laskemaan
        if ras_koodi == lahto_id:
            pisteet = 0
            lahto = True
            #maali = False

        #jos maalissa käyty, laskenta loppuu myöhemmässä ehtolauseessa
        if ras_koodi == maali_id:
            if lahto == True:
                maali = True
                lahto = False

        if lahto == True:
            for j in range(len(data["rastit"])):

                if int(data["rastit"][j]["id"]) == ras_koodi and tarkasta_duplikaatit(esiintyneet_rastit, ras_koodi) == True:
                    tmp = data["rastit"][j]["koodi"]
                    esiintyneet_rastit.append(ras_koodi)
                    try:
                        #tässä koitetaan tyyppivalaa rastikoodin ensimmäistä merkkiä, esim 9A, jos
                        #onnistuu, niin lisäys pisteisiin, mikäli maalissa ei vielä käyty
                        if maali == False:
                            luku = int(tmp[0])
                            pisteet += luku
                    except:
                        pass

    return pisteet

#palauttaa leimaustapojen listan
def palauta_ltavat(ltavat):
    paluulista = []
    for i in range(len(ltavat)):
        for j in range(len(data["leimaustapa"])):
            if ltavat[i] == data["leimaustapa"][j]:
                paluulista.append(j)
    return paluulista

#@app.route('/main', methods=['GET', 'POST'])
@app.route('/')
def main():
    #===taso 3===
    reset = request.args.get('reset')
    lataa_data(reset)
    tila = request.args.get('tila')
    ltavat = request.args.getlist('leimaustapa')
    lista = []
    if ltavat is not None:
        lista = palauta_ltavat(ltavat)
    #============
    jnimi = request.args.get('nimi')
    sarja = request.args.get('sarja')
    #kaikki jasen nimiset parametrit listaksi
    jasenet = request.args.getlist('jasen')

    #print("syöte: ", jnimi, sarja, jasenet)
    if jnimi and sarja:
        jasen_et = []
        if jasenet is not None:
            jasen_et = jasenet

        t_dict = {
        "nimi": jnimi,
        "jasenet": jasen_et,
        "id": "0",
        "leimaustapa": lista,
        "rastileimaukset": []}
        tilan_tulkinta(tila, t_dict, sarja, jnimi)

    json_obj = json.dumps(data)
    with open('/home/jajoutzs/data.json', 'w') as f:
        f.write(json_obj)

    #2 -> merkkien määrä rastin koodissa
    # koodit järkevän muotoiseksi tekstiksi rivinvaihdoin, ei järkevällä ratkaisulla
    m_jono = muotoile(palauta_int_alkavat(data["rastit"]), ";", 2)

    return Response(str((palauta_j_listaus() + m_jono)), mimetype="text/plain;charset=UTF-8")


