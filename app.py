# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
from io import BytesIO

class SchoolCodeGenerator:
    def __init__(self):
        self.state_codes = {
            'abia': '01', 'adamawa': '02', 'akwa ibom': '03', 'anambra': '04',
            'bauchi': '05', 'bayelsa': '06', 'benue': '07', 'borno': '08',
            'cross river': '09', 'delta': '10', 'ebonyi': '11', 'edo': '12',
            'ekiti': '13', 'enugu': '14', 'gombe': '15', 'imo': '16',
            'jigawa': '17', 'kaduna': '18', 'kano': '19', 'katsina': '20',
            'kebbi': '21', 'kogi': '22', 'kwara': '23', 'lagos': '24',
            'nasarawa': '25', 'niger': '26', 'ogun': '27', 'ondo': '28',
            'osun': '29', 'oyo': '30', 'plateau': '31', 'rivers': '32',
            'sokoto': '33', 'taraba': '34', 'yobe': '35', 'zamfara': '36',
            'fct': '37'
        }
        
        # COMPLETE LGA codes for ALL states
        self.lga_codes = {
            'abia': {
                "Aba North": "01", "Aba South": "02", "Arochukwu": "03", "Bende": "04",
                "Ikwuano": "05", "Isiala Ngwa North": "06", "Isiala Ngwa South": "07",
                "Isuikwuato": "08", "Obi Ngwa": "09", "Ohafia": "10", "Osisioma": "11",
                "Ugwunagbo": "12", "Ukwa East": "13", "Ukwa West": "14", "Umuahia North": "15",
                "Umuahia South": "16", "Umu Nneochi": "17"
            },
            'adamawa': {
                "Demsa": "01", "Fufure": "02", "Ganye": "03", "Gayuk": "04",
                "Gombi": "05", "Grie": "06", "Hong": "07", "Jada": "08",
                "Lamurde": "09", "Madagali": "10", "Maiha": "11", "Mayo Belwa": "12",
                "Michika": "13", "Mubi North": "14", "Mubi South": "15", "Numan": "16",
                "Shelleng": "17", "Song": "18", "Toungo": "19", "Yola North": "20",
                "Yola South": "21"
            },
            'akwa ibom': {
                "Abak": "01", "Eastern Obolo": "02", "Eket": "03", "Esit Eket": "04",
                "Essien Udim": "05", "Etim Ekpo": "06", "Etinan": "07", "Ibeno": "08",
                "Ibesikpo Asutan": "09", "Ibiono-Ibom": "10", "Ika": "11", "Ikono": "12",
                "Ikot Abasi": "13", "Ikot Ekpene": "14", "Ini": "15", "Itu": "16",
                "Mbo": "17", "Mkpat-Enin": "18", "Nsit-Atai": "19", "Nsit-Ibom": "20",
                "Nsit-Ubium": "21", "Obot Akara": "22", "Okobo": "23", "Onna": "24",
                "Oron": "25", "Oruk Anam": "26", "Udung-Uko": "27", "Ukanafun": "28",
                "Uruan": "29", "Urue-Offong/Oruko": "30", "Uyo": "31"
            },
            'anambra': {
                "Aguata": "01", "Anambra East": "02", "Anambra West": "03", "Anaocha": "04",
                "Awka North": "05", "Awka South": "06", "Ayamelum": "07", "Dunukofia": "08",
                "Ekwusigo": "09", "Idemili North": "10", "Idemili South": "11", "Ihiala": "12",
                "Njikoka": "13", "Nnewi North": "14", "Nnewi South": "15", "Ogbaru": "16",
                "Onitsha North": "17", "Onitsha South": "18", "Orumba North": "19", "Orumba South": "20",
                "Oyi": "21"
            },
            'bauchi': {
                "Alkaleri": "01", "Bauchi": "02", "Bogoro": "03", "Damban": "04",
                "Darazo": "05", "Dass": "06", "Gamawa": "07", "Ganjuwa": "08",
                "Giade": "09", "Itas/Gadau": "10", "Jama'are": "11", "Katagum": "12",
                "Kirfi": "13", "Misau": "14", "Ningi": "15", "Shira": "16",
                "Tafawa Balewa": "17", "Toro": "18", "Warji": "19", "Zaki": "20"
            },
            'bayelsa': {
                "Brass": "01", "Ekeremor": "02", "Kolokuma/Opokuma": "03", "Nembe": "04",
                "Ogbia": "05", "Sagbama": "06", "Southern Ijaw": "07", "Yenagoa": "08"
            },
            'benue': {
                "Ado": "01", "Agatu": "02", "Apa": "03", "Buruku": "04", 
                "Gboko": "05", "Guma": "06", "Gwer East": "07", "Gwer West": "08", 
                "Katsina-Ala": "09", "Konshisha": "10", "Kwande": "11", "Logo": "12", 
                "Makurdi": "13", "Obi": "14", "Ogbadibo": "15", "Ohimini": "16", 
                "Oju": "17", "Okpokwu": "18", "Otukpo": "19", "Tarka": "20", 
                "Ukum": "21", "Ushongo": "22", "Vandeikya": "23"
            },
            'borno': {
                "Abadam": "01", "Askira/Uba": "02", "Bama": "03", "Bayo": "04",
                "Biu": "05", "Chibok": "06", "Damboa": "07", "Dikwa": "08",
                "Gubio": "09", "Guzamala": "10", "Gwoza": "11", "Hawul": "12",
                "Jere": "13", "Kaga": "14", "Kala/Balge": "15", "Konduga": "16",
                "Kukawa": "17", "Kwaya Kusar": "18", "Mafa": "19", "Magumeri": "20",
                "Maiduguri": "21", "Marte": "22", "Mobbar": "23", "Monguno": "24",
                "Ngala": "25", "Nganzai": "26", "Shani": "27"
            },
            'cross river': {
                "Abi": "01", "Akamkpa": "02", "Akpabuyo": "03", "Bakassi": "04",
                "Bekwarra": "05", "Biase": "06", "Boki": "07", "Calabar Municipal": "08",
                "Calabar South": "09", "Etung": "10", "Ikom": "11", "Obanliku": "12",
                "Obubra": "13", "Obudu": "14", "Odukpani": "15", "Ogoja": "16",
                "Yakuur": "17", "Yala": "18"
            },
            'delta': {
                "Aniocha North": "01", "Aniocha South": "02", "Bomadi": "03", "Burutu": "04",
                "Ethiope East": "05", "Ethiope West": "06", "Ika North East": "07", "Ika South": "08",
                "Isoko North": "09", "Isoko South": "10", "Ndokwa East": "11", "Ndokwa West": "12",
                "Okpe": "13", "Oshimili North": "14", "Oshimili South": "15", "Patani": "16",
                "Sapele": "17", "Udu": "18", "Ughelli North": "19", "Ughelli South": "20",
                "Ukwuani": "21", "Uvwie": "22", "Warri North": "23", "Warri South": "24",
                "Warri South West": "25"
            },
            'ebonyi': {
                "Abakaliki": "01", "Afikpo North": "02", "Afikpo South": "03", "Ebonyi": "04",
                "Ezza North": "05", "Ezza South": "06", "Ikwo": "07", "Ishielu": "08",
                "Ivo": "09", "Izzi": "10", "Ohaozara": "11", "Ohaukwu": "12",
                "Onicha": "13"
            },
            'edo': {
                "Akoko-Edo": "01", "Egor": "02", "Esan Central": "03", "Esan North-East": "04",
                "Esan South-East": "05", "Esan West": "06", "Etsako Central": "07", "Etsako East": "08",
                "Etsako West": "09", "Igueben": "10", "Ikpoba Okha": "11", "Orhionmwon": "12",
                "Oredo": "13", "Ovia North-East": "14", "Ovia South-West": "15", "Owan East": "16",
                "Owan West": "17", "Uhunmwonde": "18"
            },
            'ekiti': {
                "Ado Ekiti": "01", "Efon": "02", "Ekiti East": "03", "Ekiti South-West": "04",
                "Ekiti West": "05", "Emure": "06", "Gbonyin": "07", "Ido Osi": "08",
                "Ijero": "09", "Ikere": "10", "Ikole": "11", "Ilejemeje": "12",
                "Irepodun/Ifelodun": "13", "Ise/Orun": "14", "Moba": "15", "Oye": "16"
            },
            'enugu': {
                "Aninri": "01", "Awgu": "02", "Enugu East": "03", "Enugu North": "04",
                "Enugu South": "05", "Ezeagu": "06", "Igbo Etiti": "07", "Igbo Eze North": "08",
                "Igbo Eze South": "09", "Isi Uzo": "10", "Nkanu East": "11", "Nkanu West": "12",
                "Nsukka": "13", "Oji River": "14", "Udenu": "15", "Udi": "16",
                "Uzo Uwani": "17"
            },
            'gombe': {
                "Akko": "01", "Balanga": "02", "Billiri": "03", "Dukku": "04",
                "Funakaye": "05", "Gombe": "06", "Kaltungo": "07", "Kwami": "08",
                "Nafada": "09", "Shongom": "10", "Yamaltu/Deba": "11"
            },
            'imo': {
                "Aboh Mbaise": "01", "Ahiazu Mbaise": "02", "Ehime Mbano": "03", "Ezinihitte": "04",
                "Ideato North": "05", "Ideato South": "06", "Ihitte/Uboma": "07", "Ikeduru": "08",
                "Isiala Mbano": "09", "Isu": "10", "Mbaitoli": "11", "Ngor Okpala": "12",
                "Njaba": "13", "Nkwerre": "14", "Nwangele": "15", "Obowo": "16",
                "Oguta": "17", "Ohaji/Egbema": "18", "Okigwe": "19", "Orlu": "20",
                "Orsu": "21", "Oru East": "22", "Oru West": "23", "Owerri Municipal": "24",
                "Owerri North": "25", "Owerri West": "26", "Unuimo": "27"
            },
            'jigawa': {
                "Auyo": "01", "Babura": "02", "Biriniwa": "03", "Birnin Kudu": "04",
                "Buji": "05", "Dutse": "06", "Gagarawa": "07", "Garki": "08",
                "Gumel": "09", "Guri": "10", "Gwaram": "11", "Gwiwa": "12",
                "Hadejia": "13", "Jahun": "14", "Kafin Hausa": "15", "Kazaure": "16",
                "Kiri Kasama": "17", "Kiyawa": "18", "Kaugama": "19", "Maigatari": "20",
                "Malam Madori": "21", "Miga": "22", "Ringim": "23", "Roni": "24",
                "Sule Tankarkar": "25", "Taura": "26", "Yankwashi": "27"
            },
            'kaduna': {
                "Birnin Gwari": "01", "Chikun": "02", "Giwa": "03", "Igabi": "04",
                "Ikara": "05", "Jaba": "06", "Jema'a": "07", "Kachia": "08",
                "Kaduna North": "09", "Kaduna South": "10", "Kagarko": "11", "Kajuru": "12",
                "Kaura": "13", "Kauru": "14", "Kubau": "15", "Kudan": "16",
                "Lere": "17", "Makarfi": "18", "Sabon Gari": "19", "Sanga": "20",
                "Soba": "21", "Zangon Kataf": "22", "Zaria": "23"
            },
            'kano': {
                "Ajingi": "01", "Albasu": "02", "Bagwai": "03", "Bebeji": "04",
                "Bichi": "05", "Bunkure": "06", "Dala": "07", "Dambatta": "08",
                "Dawakin Kudu": "09", "Dawakin Tofa": "10", "Doguwa": "11", "Fagge": "12",
                "Gabasawa": "13", "Garko": "14", "Garun Mallam": "15", "Gaya": "16",
                "Gezawa": "17", "Gwale": "18", "Gwarzo": "19", "Kabo": "20",
                "Kano Municipal": "21", "Karaye": "22", "Kibiya": "23", "Kiru": "24",
                "Kumbotso": "25", "Kunchi": "26", "Kura": "27", "Madobi": "28",
                "Makoda": "29", "Minjibir": "30", "Nasarawa": "31", "Rano": "32",
                "Rimin Gado": "33", "Rogo": "34", "Shanono": "35", "Sumaila": "36",
                "Takai": "37", "Tarauni": "38", "Tofa": "39", "Tsanyawa": "40",
                "Tudun Wada": "41", "Ungogo": "42", "Warawa": "43", "Wudil": "44"
            },
            'katsina': {
                "Bakori": "01", "Batagarawa": "02", "Batsari": "03", "Baure": "04",
                "Bindawa": "05", "Charanchi": "06", "Dandume": "07", "Danja": "08",
                "Dan Musa": "09", "Daura": "10", "Dutsi": "11", "Dutsin Ma": "12",
                "Faskari": "13", "Funtua": "14", "Ingawa": "15", "Jibia": "16",
                "Kafur": "17", "Kaita": "18", "Kankara": "19", "Kankia": "20",
                "Katsina": "21", "Kurfi": "22", "Kusada": "23", "Mai'Adua": "24",
                "Malumfashi": "25", "Mani": "26", "Mashi": "27", "Matazu": "28",
                "Musawa": "29", "Rimi": "30", "Sabuwa": "31", "Safana": "32",
                "Sandamu": "33", "Zango": "34"
            },
            'kebbi': {
                "Aleiro": "01", "Arewa Dandi": "02", "Argungu": "03", "Augie": "04",
                "Bagudo": "05", "Birnin Kebbi": "06", "Bunza": "07", "Dandi": "08",
                "Fakai": "09", "Gwandu": "10", "Jega": "11", "Kalgo": "12",
                "Koko/Besse": "13", "Maiyama": "14", "Ngaski": "15", "Sakaba": "16",
                "Shanga": "17", "Suru": "18", "Wasagu/Danko": "19", "Yauri": "20",
                "Zuru": "21"
            },
            'kogi': {
                "Adavi": "01", "Ajaokuta": "02", "Ankpa": "03", "Bassa": "04",
                "Dekina": "05", "Ibaji": "06", "Idah": "07", "Igalamela Odolu": "08",
                "Ijumu": "09", "Kabba/Bunu": "10", "Kogi": "11", "Lokoja": "12",
                "Mopa Muro": "13", "Ofu": "14", "Ogori/Magongo": "15", "Okehi": "16",
                "Okene": "17", "Olamaboro": "18", "Omala": "19", "Yagba East": "20",
                "Yagba West": "21"
            },
            'kwara': {
                "Asa": "01", "Baruten": "02", "Edu": "03", "Ekiti": "04",
                "Ifelodun": "05", "Ilorin East": "06", "Ilorin South": "07", "Ilorin West": "08",
                "Irepodun": "09", "Isin": "10", "Kaiama": "11", "Moro": "12",
                "Offa": "13", "Oke Ero": "14", "Oyun": "15", "Pategi": "16"
            },
            'lagos': {
                "Agege": "01", "Ajeromi-Ifelodun": "02", "Alimosho": "03",
                "Amuwo-Odofin": "04", "Apapa": "05", "Badagry": "06",
                "Epe": "07", "Eti-Osa": "08", "Ibeju-Lekki": "09",
                "Ifako-Ijaiye": "10", "Ikeja": "11", "Ikorodu": "12",
                "Kosofe": "13", "Lagos Island": "14", "Lagos Mainland": "15",
                "Mushin": "16", "Ojo": "17", "Oshodi-Isolo": "18",
                "Shomolu": "19", "Surulere": "20"
            },
            'nasarawa': {
                "Akwanga": "01", "Awe": "02", "Doma": "03", "Karu": "04",
                "Keana": "05", "Keffi": "06", "Kokona": "07", "Lafia": "08",
                "Nasarawa": "09", "Nasarawa Egon": "10", "Obi": "11", "Toto": "12",
                "Wamba": "13"
            },
            'niger': {
                "Agaie": "01", "Agwara": "02", "Bida": "03", "Borgu": "04",
                "Bosso": "05", "Chanchaga": "06", "Edati": "07", "Gbako": "08",
                "Gurara": "09", "Katcha": "10", "Kontagora": "11", "Lapai": "12",
                "Lavun": "13", "Magama": "14", "Mariga": "15", "Mashegu": "16",
                "Mokwa": "17", "Moya": "18", "Paikoro": "19", "Rafi": "20",
                "Rijau": "21", "Shiroro": "22", "Suleja": "23", "Tafa": "24",
                "Wushishi": "25"
            },
            'ogun': {
                "Abeokuta North": "01", "Abeokuta South": "02", "Ado-Odo/Ota": "03", "Egbado North": "04",
                "Egbado South": "05", "Ewekoro": "06", "Ifo": "07", "Ijebu East": "08",
                "Ijebu North": "09", "Ijebu North East": "10", "Ijebu Ode": "11", "Ikenne": "12",
                "Imeko Afon": "13", "Ipokia": "14", "Obafemi Owode": "15", "Odeda": "16",
                "Odogbolu": "17", "Ogun Waterside": "18", "Remo North": "19", "Shagamu": "20"
            },
            'ondo': {
                "Akoko North-East": "01", "Akoko North-West": "02", "Akoko South-East": "03", "Akoko South-West": "04",
                "Akure North": "05", "Akure South": "06", "Ese Odo": "07", "Idanre": "08",
                "Ifedore": "09", "Ilaje": "10", "Ile Oluji/Okeigbo": "11", "Irele": "12",
                "Odigbo": "13", "Okitipupa": "14", "Ondo East": "15", "Ondo West": "16",
                "Ose": "17", "Owo": "18"
            },
            'osun': {
                "Aiyedade": "01", "Aiyedire": "02", "Atakunmosa East": "03", "Atakunmosa West": "04",
                "Boluwaduro": "05", "Boripe": "06", "Ede North": "07", "Ede South": "08",
                "Egbedore": "09", "Ejigbo": "10", "Ife Central": "11", "Ife East": "12",
                "Ife North": "13", "Ife South": "14", "Ifedayo": "15", "Ifelodun": "16",
                "Ila": "17", "Ilesa East": "18", "Ilesa West": "19", "Irepodun": "20",
                "Irewole": "21", "Isokan": "22", "Iwo": "23", "Obokun": "24",
                "Odo Otin": "25", "Ola Oluwa": "26", "Olorunda": "27", "Oriade": "28",
                "Orolu": "29", "Osogbo": "30"
            },
            'oyo': {
                "Afijio": "01", "Akinyele": "02", "Atiba": "03", "Atisbo": "04",
                "Egbeda": "05", "Ibadan North": "06", "Ibadan North-East": "07", "Ibadan North-West": "08",
                "Ibadan South-East": "09", "Ibadan South-West": "10", "Ibarapa Central": "11", "Ibarapa East": "12",
                "Ibarapa North": "13", "Ido": "14", "Irepo": "15", "Iseyin": "16",
                "Itesiwaju": "17", "Iwajowa": "18", "Kajola": "19", "Lagelu": "20",
                "Ogbomosho North": "21", "Ogbomosho South": "22", "Ogo Oluwa": "23", "Olorunsogo": "24",
                "Oluyole": "25", "Ona Ara": "26", "Orelope": "27", "Ori Ire": "28",
                "Oyo East": "29", "Oyo West": "30", "Saki East": "31", "Saki West": "32",
                "Surulere": "33"
            },
            'plateau': {
                "Bokkos": "01", "Barkin Ladi": "02", "Bassa": "03", "Jos East": "04",
                "Jos North": "05", "Jos South": "06", "Kanam": "07", "Kanke": "08",
                "Langtang North": "09", "Langtang South": "10", "Mangu": "11", "Mikang": "12",
                "Pankshin": "13", "Qua'an Pan": "14", "Riyom": "15", "Shendam": "16",
                "Wase": "17"
            },
            'rivers': {
                "Abua/Odual": "01", "Ahoada East": "02", "Ahoada West": "03", "Akuku-Toru": "04",
                "Andoni": "05", "Asari-Toru": "06", "Bonny": "07", "Degema": "08",
                "Eleme": "09", "Emuoha": "10", "Etche": "11", "Gokana": "12",
                "Ikwerre": "13", "Khana": "14", "Obio/Akpor": "15", "Ogba/Egbema/Ndoni": "16",
                "Ogu/Bolo": "17", "Okrika": "18", "Omuma": "19", "Opobo/Nkoro": "20",
                "Oyigbo": "21", "Port Harcourt": "22", "Tai": "23"
            },
            'sokoto': {
                "Binji": "01", "Bodinga": "02", "Dange Shuni": "03", "Gada": "04",
                "Goronyo": "05", "Gudu": "06", "Gwadabawa": "07", "Illela": "08",
                "Isa": "09", "Kebbe": "10", "Kware": "11", "Rabah": "12",
                "Sabon Birni": "13", "Shagari": "14", "Silame": "15", "Sokoto North": "16",
                "Sokoto South": "17", "Tambuwal": "18", "Tangaza": "19", "Tureta": "20",
                "Wamako": "21", "Wurno": "22", "Yabo": "23"
            },
            'taraba': {
                "Ardo Kola": "01", "Bali": "02", "Donga": "03", "Gashaka": "04",
                "Gassol": "05", "Ibi": "06", "Jalingo": "07", "Karim Lamido": "08",
                "Kumi": "09", "Lau": "10", "Sardauna": "11", "Takum": "12",
                "Ussa": "13", "Wukari": "14", "Yorro": "15", "Zing": "16"
            },
            'yobe': {
                "Bade": "01", "Bursari": "02", "Damaturu": "03", "Fika": "04",
                "Fune": "05", "Geidam": "06", "Gujba": "07", "Gulani": "08",
                "Jakusko": "09", "Karasuwa": "10", "Machina": "11", "Nangere": "12",
                "Nguru": "13", "Potiskum": "14", "Tarmuwa": "15", "Yunusari": "16",
                "Yusufari": "17"
            },
            'zamfara': {
                "Anka": "01", "Bakura": "02", "Birnin Magaji/Kiyaw": "03", "Bukkuyum": "04",
                "Bungudu": "05", "Gummi": "06", "Gusau": "07", "Kaura Namoda": "08",
                "Maradun": "09", "Maru": "10", "Shinkafi": "11", "Talata Mafara": "12",
                "Chafe": "13", "Zurmi": "14"
            },
            'fct': {
                "Abaji": "01", "Bwari": "02", "Gwagwalada": "03", "Kuje": "04",
                "Kwali": "05", "Municipal Area Council": "06"
            }
        }

    # Rest of the class methods remain the same...
    def get_state_code(self, state_name):
        state_name_lower = state_name.lower()
        return self.state_codes.get(state_name_lower)
    
    def get_lga_code(self, state_name, lga_name):
        state_name_lower = state_name.lower()
        lga_name_lower = lga_name.lower()
        
        if state_name_lower in self.lga_codes:
            for official_name, code in self.lga_codes[state_name_lower].items():
                if official_name.lower() == lga_name_lower:
                    return code
            for official_name, code in self.lga_codes[state_name_lower].items():
                if lga_name_lower in official_name.lower() or official_name.lower() in lga_name_lower:
                    return code
        return None
    
    def get_all_lgas_for_state(self, state_name):
        state_name_lower = state_name.lower()
        if state_name_lower in self.lga_codes:
            return list(self.lga_codes[state_name_lower].keys())
        return []

    def read_existing_codes(self, uploaded_file):
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(uploaded_file)
            else:
                content = uploaded_file.getvalue().decode("utf-8")
                codes = [line.strip() for line in content.split('\n') if line.strip()]
                return codes
            
            if 'School Code' in df.columns:
                return df['School Code'].astype(str).tolist()
            else:
                for col in df.columns:
                    if any(str(x).startswith(tuple(self.state_codes.values())) for x in df[col].dropna()):
                        return df[col].astype(str).tolist()
                return []
        except Exception as e:
            st.error(f"Error reading file: {e}")
            return []
    
    def analyze_existing_codes(self, state_code, existing_codes):
        lga_analysis = {}
        
        for code in existing_codes:
            code_str = str(code).strip()
            if len(code_str) == 8 and code_str.startswith(state_code):
                lga_code = code_str[2:4]
                try:
                    serial = int(code_str[4:])
                    if lga_code not in lga_analysis:
                        lga_analysis[lga_code] = []
                    lga_analysis[lga_code].append(serial)
                except ValueError:
                    continue
        
        next_serials = {}
        for lga_code, serials in lga_analysis.items():
            next_serials[lga_code] = max(serials) + 1 if serials else 1
        
        return next_serials
    
    def generate_school_codes(self, state_name, lga_names, num_schools, existing_codes_file=None):
        state_code = self.get_state_code(state_name)
        if not state_code:
            st.error(f"State '{state_name}' not found!")
            return None
        
        existing_codes = []
        lga_next_serials = {}
        
        if existing_codes_file:
            existing_codes = self.read_existing_codes(existing_codes_file)
            if existing_codes:
                lga_next_serials = self.analyze_existing_codes(state_code, existing_codes)
        
        generated_codes = []
        
        for lga_name in lga_names:
            lga_code = self.get_lga_code(state_name, lga_name)
            if not lga_code:
                st.warning(f"Skipping LGA '{lga_name}' - code not found")
                continue
            
            next_serial = lga_next_serials.get(lga_code, 1)
            
            for i in range(num_schools):
                serial_number = str(next_serial + i).zfill(4)
                school_code = f"{state_code}{lga_code}{serial_number}"
                generated_codes.append({
                    'State': state_name.title(),
                    'LGA': lga_name.title(),
                    'LGA_Code': lga_code,
                    'School_Code': school_code,
                    'Serial_Number': serial_number
                })
        
        return generated_codes

def main():
    st.set_page_config(
        page_title="Nigeria School Code Generator",
        page_icon="🏫",
        layout="wide"
    )
    
    st.title("🏫 Nigeria School Code Generator")
    st.markdown("Generate unique school codes for all Nigerian states and LGAs")
    
    generator = SchoolCodeGenerator()
    
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.radio("Choose Mode", ["Generate Codes", "State Information", "About"])
    
    if app_mode == "Generate Codes":
        generate_codes_ui(generator)
    elif app_mode == "State Information":
        state_info_ui(generator)
    else:
        about_ui()

def generate_codes_ui(generator):
    st.header("Generate School Codes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        state_name = st.selectbox(
            "Select State",
            sorted([state.title() for state in generator.state_codes.keys()])
        )
        
        lgas = generator.get_all_lgas_for_state(state_name)
        
        if lgas:
            use_all_lgas = st.checkbox("Generate for all LGAs", value=True)
            
            if use_all_lgas:
                selected_lgas = lgas
                st.info(f"Selected all {len(lgas)} LGAs in {state_name}")
            else:
                selected_lgas = st.multiselect(
                    "Select LGAs",
                    lgas,
                    default=lgas[:min(3, len(lgas))]
                )
        else:
            st.warning(f"No LGA data available for {state_name}")
            selected_lgas = []
    
    with col2:
        num_schools = st.number_input(
            "Number of schools per LGA",
            min_value=1,
            max_value=1000,
            value=5
        )
        
        st.subheader("Existing Codes (Optional)")
        existing_file = st.file_uploader(
            "Upload existing school codes file",
            type=['csv', 'xlsx', 'xls', 'txt']
        )
    
    if st.button("Generate School Codes", type="primary"):
        if not state_name or not selected_lgas:
            st.error("Please select a state and at least one LGA")
            return
        
        with st.spinner("Generating school codes..."):
            generated_codes = generator.generate_school_codes(
                state_name=state_name,
                lga_names=selected_lgas,
                num_schools=num_schools,
                existing_codes_file=existing_file
            )
        
        if generated_codes:
            display_results(generated_codes, state_name)
        else:
            st.error("No codes were generated. Please check your inputs.")

def display_results(generated_codes, state_name):
    st.success(f"Successfully generated {len(generated_codes)} school codes for {state_name}!")
    
    df = pd.DataFrame(generated_codes)
    
    st.subheader("Summary")
    summary = df.groupby(['LGA', 'LGA_Code']).size().reset_index(name='Number of Schools')
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Schools", len(generated_codes))
    with col2:
        st.metric("Number of LGAs", len(summary))
    with col3:
        st.metric("State", state_name)
    
    st.subheader("Generated School Codes")
    st.dataframe(df, use_container_width=True)
    
    st.subheader("Download Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name=f"school_codes_{state_name.lower()}.csv",
            mime="text/csv"
        )
    
    with col2:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='School Codes')
            summary.to_excel(writer, index=False, sheet_name='Summary')
        excel_data = output.getvalue()
        
        st.download_button(
            label="Download as Excel",
            data=excel_data,
            file_name=f"school_codes_{state_name.lower()}.xlsx",
            mime="application/vnd.ms-excel"
        )
    
    with col3:
        codes_only = "\n".join(df['School_Code'].tolist())
        st.download_button(
            label="Download Codes Only (TXT)",
            data=codes_only,
            file_name=f"school_codes_{state_name.lower()}.txt",
            mime="text/plain"
        )

def state_info_ui(generator):
    st.header("State Information")
    
    state_name = st.selectbox(
        "Select State to View Information",
        sorted([state.title() for state in generator.state_codes.keys()])
    )
    
    if state_name:
        state_code = generator.get_state_code(state_name)
        lgas = generator.get_all_lgas_for_state(state_name)
        
        if lgas:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader(f"{state_name} Information")
                st.metric("State Code", state_code)
                st.metric("Number of LGAs", len(lgas))
            
            with col2:
                st.subheader("Local Government Areas")
                lga_data = []
                for lga in lgas:
                    lga_code = generator.get_lga_code(state_name, lga)
                    lga_data.append({"LGA": lga, "Code": lga_code})
                
                lga_df = pd.DataFrame(lga_data)
                st.dataframe(lga_df, use_container_width=True, hide_index=True)
        else:
            st.warning(f"No LGA data available for {state_name}")

def about_ui():
    st.header("About Nigeria School Code Generator")
    
    st.markdown("""
    ## 🎯 Purpose
    This web application generates unique school codes for all Nigerian states and Local Government Areas (LGAs) 
    following the official format: `SSLLXXXX`
    
    - **SS**: State code (2 digits)
    - **LL**: LGA code (2 digits) 
    - **XXXX**: School serial number (4 digits)
    
    ## 📊 Coverage
    - **36 States** + Federal Capital Territory (FCT)
    - **774 Local Government Areas** nationwide
    - **Official numbering** for all states and LGAs
    
    ## 🚀 Features
    - Generate codes for specific LGAs or entire states
    - Prevent duplicates by checking existing codes
    - Multiple download formats (CSV, Excel, TXT)
    - Official LGA codes and numbering
    
    ## 📝 Usage
    1. Select a state and LGAs
    2. Specify number of schools per LGA
    3. Upload existing codes (optional, to avoid duplicates)
    4. Generate and download results
    
    ## 🛠️ Technical Details
    - Built with Streamlit
    - Uses official Nigerian government LGA numbering
    - Supports CSV, Excel, and text file formats
    """)
    
    st.info("💡 **Tip**: Use the 'State Information' section to view all LGAs and their official codes for any state.")

if __name__ == "__main__":
    main()