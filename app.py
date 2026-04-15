import streamlit as st
import pandas as pd
import numpy as np
import os
import re
import requests
from io import BytesIO
from difflib import SequenceMatcher

class SchoolCodeGenerator:
    def __init__(self):
        self.ou_reference_filename = "State_LGA_Wards_OUs_List.csv"
        self.ou_reference_alias_filename = "ou_index_2026.csv"
        self.parent_match_fuzzy_threshold = 75
        self.parent_match_confident_threshold = 85
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
        
        # LGA codes for each state (in official ascending order)
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
                "Tsafe": "13", "Zurmi": "14"
            },
            'fct': {
                "Abaji": "01", "Abuja Municipal Area Council": "02", "Bwari": "03", "Gwagwalada": "04", "Kuje": "05",
                "Kwali": "06", 
            }
        }
    
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
                df = pd.read_csv(uploaded_file, dtype=str)  # Read all as string
            elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(uploaded_file, dtype=str)  # Read all as string
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

    def _read_table_file(self, file_source):
        if isinstance(file_source, str):
            if file_source.lower().endswith('.csv'):
                return pd.read_csv(file_source, dtype=str)
            return pd.read_excel(file_source, dtype=str)

        file_name = str(getattr(file_source, 'name', '') or '')
        if file_name.lower().endswith('.csv'):
            return pd.read_csv(file_source, dtype=str)
        return pd.read_excel(file_source, dtype=str)

    def _normalize_text(self, value):
        text = str(value or '').strip().lower()
        text = re.sub(r'[^a-z0-9]+', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _build_name_variants(self, value, kind='generic'):
        normalized = self._normalize_text(value)
        if not normalized:
            return set()

        variants = {normalized}
        suffixes = {
            'state': [' state'],
            'lga': [' local government area'],
            'ward': [' ward'],
            'generic': [' state', ' local government area', ' ward']
        }

        queue = [normalized]
        seen = set()
        while queue:
            current = queue.pop()
            if current in seen or not current:
                continue

            seen.add(current)
            variants.add(current)

            words = current.split()
            if len(words) > 1 and len(words[0]) <= 3:
                queue.append(' '.join(words[1:]).strip())

            for suffix in suffixes.get(kind, suffixes['generic']):
                if current.endswith(suffix):
                    queue.append(current[:-len(suffix)].strip())

        return {item for item in variants if item}

    def _rename_matching_columns(self, df, alias_map):
        renamed = df.copy()
        for target_column, aliases in alias_map.items():
            if target_column in renamed.columns:
                continue

            for alias in aliases:
                if alias in renamed.columns:
                    renamed = renamed.rename(columns={alias: target_column})
                    break

        return renamed

    def _normalize_school_level(self, school_level):
        raw_level = str(school_level or '').strip().lower()
        if not raw_level:
            return ''

        normalized_text = re.sub(r'[^a-z0-9]+', ' ', raw_level).strip()
        level_map = {
            'jss': 'JSS',
            'junior secondary': 'JSS',
            'junior secondary school': 'JSS',
            'sss': 'SSS',
            'senior secondary': 'SSS',
            'senior secondary school': 'SSS',
            'pry': 'PRY',
            'primary': 'PRY',
            'primary school': 'PRY',
            'tvet': 'TVET',
            'technical': 'TVET',
            'technical vocational': 'TVET',
            'technical vocational education and training': 'TVET',
            'pvt': 'PVT',
            'private': 'PVT',
            'private school': 'PVT',
            'iqs': 'IQS',
            'islamiyya': 'IQS',
            'islamic': 'IQS'
        }

        return level_map.get(normalized_text, str(school_level or '').strip().upper() if normalized_text in {'jss', 'sss', 'pry', 'tvet', 'pvt', 'iqs'} else '')

    def _format_school_name_with_prefix_and_code(self, school_name, school_code, school_level=''):
        valid_prefixes = {'JSS', 'SSS', 'PRY', 'TVET', 'PVT', 'IQS'}

        name_text = str(school_name or '').strip()
        code_text = str(school_code or '').strip()

        if not name_text:
            return '', '', False

        # Respect user input when it is already in valid form:
        # PREFIX School Name (CODE)
        preformatted_match = re.match(
            r'^(JSS|SSS|PRY|TVET|PVT|IQS)\s+(.+?)\s*\(\s*[^()]+\s*\)\s*$',
            name_text,
            flags=re.IGNORECASE
        )
        if preformatted_match:
            preserved_prefix = str(preformatted_match.group(1) or '').upper().strip()
            preserved_core_name = str(preformatted_match.group(2) or '').strip()
            rebuilt_name = re.sub(r'\s+', ' ', f"{preserved_prefix} {preserved_core_name}").strip()
            if code_text:
                rebuilt_name = f"{rebuilt_name} ({code_text})"
            return rebuilt_name, preserved_prefix, True

        # Remove trailing code in parentheses if present to avoid duplication.
        name_without_suffix = re.sub(r'\s*\(\s*[^()]+\s*\)\s*$', '', name_text).strip()

        # Remove any existing valid prefix from the start; the final prefix should come from school_level when provided.
        core_name = re.sub(r'^(JSS|SSS|PRY|TVET|PVT|IQS)\b\s*', '', name_without_suffix, flags=re.IGNORECASE).strip()

        prefix_from_level = self._normalize_school_level(school_level)
        prefix_match = re.match(r'^(JSS|SSS|PRY|TVET|PVT|IQS)\b\s*(.*)$', name_without_suffix, flags=re.IGNORECASE)
        prefix_from_name = str(prefix_match.group(1) or '').upper().strip() if prefix_match else ''

        prefix = prefix_from_level or prefix_from_name
        if prefix not in valid_prefixes:
            prefix = ''

        if not core_name:
            core_name = 'Unnamed School'

        normalized_name = re.sub(r'\s+', ' ', f"{prefix} {core_name}".strip()).strip()
        if code_text:
            normalized_name = f"{normalized_name} ({code_text})" if normalized_name else f"({code_text})"

        is_valid_format = bool(prefix)
        return normalized_name, prefix, is_valid_format

    def _normalize_code_for_name_suffix(self, code_value, source='generated'):
        code_text = str(code_value or '').strip()
        if not code_text:
            return ''

        if source == 'old_schoolcode':
            # Business rule: old_schoolcode must NOT be a 10-digit number.
            if re.fullmatch(r'\d{10}', code_text):
                return ''
            return code_text

        digits_only = re.sub(r'\D', '', code_text)
        if len(digits_only) >= 10:
            return digits_only[-10:]
        if re.fullmatch(r'\d{10}', code_text):
            return code_text
        return ''

    def _get_ou_reference_path(self):
        for candidate in self._get_ou_reference_candidate_paths():
            if os.path.exists(candidate):
                return candidate
        return self._get_ou_reference_candidate_paths()[0]

    def _get_ou_reference_candidate_paths(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return [
            os.path.join(base_dir, "school_app", "etc", self.ou_reference_alias_filename),
            os.path.join(base_dir, self.ou_reference_alias_filename),
            os.path.join(base_dir, self.ou_reference_filename),
            os.path.join(base_dir, "school_app", "etc", self.ou_reference_filename),
        ]

    def _get_secret_or_env(self, key):
        value = ""
        try:
            value = str(st.secrets.get(key, "") or "").strip()
        except Exception:
            value = ""
        if value:
            return value
        return str(os.getenv(key, "") or "").strip()

    def fetch_ou_reference_from_remote(self):
        reference_url = self._get_secret_or_env("OU_REFERENCE_URL")
        if not reference_url:
            return None, ""

        headers = {}
        bearer_token = self._get_secret_or_env("OU_REFERENCE_BEARER_TOKEN")
        if bearer_token:
            headers["Authorization"] = f"Bearer {bearer_token}"

        response = requests.get(reference_url, headers=headers, timeout=60)
        response.raise_for_status()

        buffer = BytesIO(response.content)
        buffer.name = self.ou_reference_alias_filename
        return buffer, reference_url

    def load_ou_reference(self, reference_path=None, reference_file=None):
        if reference_file is not None:
            reference_df = self._read_table_file(reference_file).fillna('')
            reference_file_path = '<uploaded>'
        else:
            reference_file_path = reference_path or self._get_ou_reference_path()
            if not os.path.exists(reference_file_path):
                raise FileNotFoundError(
                    f"OU reference file not found: {reference_file_path}. "
                    f"Checked: {', '.join(self._get_ou_reference_candidate_paths())}"
                )
            reference_df = self._read_table_file(reference_file_path).fillna('')
        reference_df.columns = [str(col).lower().strip() for col in reference_df.columns]

        required_columns = [
            'state (level2)', 'lga (level3)', 'lgauid', 'lgacode (ssll)',
            'lgaparentuid', 'ward (level 4)', 'warduid'
        ]
        missing_columns = [col for col in required_columns if col not in reference_df.columns]
        if missing_columns:
            raise ValueError(f"OU reference file is missing required columns: {', '.join(missing_columns)}")

        reference_df['lgacode (ssll)'] = reference_df['lgacode (ssll)'].astype(str).str.strip()
        reference_df['lgacode (ssll)'] = reference_df['lgacode (ssll)'].apply(
            lambda value: value.zfill(4) if value.isdigit() else value
        )
        reference_df['state_key'] = reference_df['state (level2)'].apply(
            lambda value: '|'.join(sorted(self._build_name_variants(value, 'state')))
        )
        reference_df['lga_key'] = reference_df['lga (level3)'].apply(
            lambda value: '|'.join(sorted(self._build_name_variants(value, 'lga')))
        )
        reference_df['ward_key'] = reference_df['ward (level 4)'].apply(
            lambda value: '|'.join(sorted(self._build_name_variants(value, 'ward')))
        )

        return reference_df, reference_file_path

    def _row_matches_variants(self, row_value, variants):
        if not variants:
            return True

        row_variants = set(str(row_value or '').split('|'))
        return bool(row_variants.intersection(variants))

    def _similarity_score(self, left_text, right_text):
        left = self._normalize_text(left_text)
        right = self._normalize_text(right_text)
        if not left or not right:
            return 0.0

        if left == right:
            return 100.0

        seq_score = SequenceMatcher(None, left, right).ratio() * 100.0
        left_tokens = set(left.split())
        right_tokens = set(right.split())
        overlap = left_tokens.intersection(right_tokens)
        token_score = (len(overlap) / max(1, len(left_tokens.union(right_tokens)))) * 100.0

        containment_score = 0.0
        if left in right or right in left:
            containment_score = 100.0

        return (seq_score * 0.5) + (token_score * 0.3) + (containment_score * 0.2)

    def _fuzzy_match_ward_within_lga(self, ward_input, lgauid, ward_reference_df):
        lga_wards = ward_reference_df[ward_reference_df['lgauid'] == lgauid]
        if len(lga_wards) == 0:
            return '', '', 0.0

        ward_input_text = str(ward_input or '').strip()
        if not ward_input_text:
            return '', '', 0.0

        best_uid = ''
        best_name = ''
        best_score = 0.0

        for _, candidate in lga_wards.iterrows():
            ward_name = str(candidate.get('ward (level 4)', '') or '').strip()
            ward_uid = str(candidate.get('warduid', '') or '').strip()
            if not ward_name or not ward_uid:
                continue

            score = self._similarity_score(ward_input_text, ward_name)
            if score > best_score:
                best_score = score
                best_uid = ward_uid
                best_name = ward_name

        if best_score >= float(self.parent_match_fuzzy_threshold):
            return best_uid, best_name, round(best_score, 1)

        return '', '', 0.0

    def _match_lga_center_ward(self, lga_name, lgauid, ward_reference_df):
        lga_wards = ward_reference_df[ward_reference_df['lgauid'] == lgauid]
        if len(lga_wards) == 0:
            return '', '', 0.0

        lga_text = self._normalize_text(lga_name)
        center_candidates = [
            f"{lga_text} central",
            f"{lga_text} town",
            f"{lga_text} ward 1",
            lga_text
        ]

        best_uid = ''
        best_name = ''
        best_score = 0.0

        for _, candidate in lga_wards.iterrows():
            ward_name = str(candidate.get('ward (level 4)', '') or '').strip()
            ward_uid = str(candidate.get('warduid', '') or '').strip()
            if not ward_name or not ward_uid:
                continue

            candidate_score = max(self._similarity_score(pattern, ward_name) for pattern in center_candidates)
            if candidate_score > best_score:
                best_score = candidate_score
                best_uid = ward_uid
                best_name = ward_name

        if best_score >= float(self.parent_match_fuzzy_threshold):
            return best_uid, best_name, round(best_score, 1)

        return '', '', 0.0

    def _find_unknown_ward_uid(self, lgauid, ward_reference_df):
        lga_wards = ward_reference_df[ward_reference_df['lgauid'] == lgauid]
        if len(lga_wards) == 0:
            return '', ''

        unknown_wards = lga_wards[
            lga_wards['ward_key'].astype(str).str.contains('unknown', case=False, regex=False)
        ]
        if len(unknown_wards) == 0:
            return '', ''

        preferred = unknown_wards[
            unknown_wards['ward (level 4)'].astype(str).apply(
                lambda value: self._normalize_text(value) == 'unknown ward'
            )
        ]
        chosen_row = preferred.iloc[0] if len(preferred) > 0 else unknown_wards.iloc[0]
        return str(chosen_row.get('warduid', '') or '').strip(), str(chosen_row.get('ward (level 4)', '') or '').strip()

    def _resolve_school_row(self, row, lga_reference_df, ward_reference_df):
        state_variants = self._build_name_variants(row.get('state', ''), 'state')
        lga_variants = self._build_name_variants(row.get('lga', ''), 'lga')
        ward_variants = self._build_name_variants(row.get('ward', ''), 'ward')
        lgacode = str(row.get('lgacode', '') or '').strip()
        lgacode = lgacode.zfill(4) if lgacode.isdigit() else lgacode

        candidates = lga_reference_df
        if lgacode:
            candidates = candidates[candidates['lgacode (ssll)'] == lgacode]
        if state_variants:
            candidates = candidates[candidates['state_key'].apply(lambda value: self._row_matches_variants(value, state_variants))]
        if lga_variants:
            candidates = candidates[candidates['lga_key'].apply(lambda value: self._row_matches_variants(value, lga_variants))]

        if len(candidates) == 0:
            return {
                'match_status': 'unresolved',
                'match_notes': 'Could not resolve state/LGA against the OU reference file',
                'level2uid': '',
                'lgauid': '',
                'warduid': '',
                'resolved_lgacode': lgacode,
                'parentuid_for_create': '',
                'parent_source': '',
                'parent_match_type': 'unresolved',
                'parent_match_score': 0.0,
                'parent_candidate_count': 0,
                'reference_state': '',
                'reference_lga': '',
                'reference_ward': ''
            }

        if len(candidates) > 1:
            return {
                'match_status': 'unresolved',
                'match_notes': 'Multiple LGAs matched. Provide lgacode or cleaner state/LGA values.',
                'level2uid': '',
                'lgauid': '',
                'warduid': '',
                'resolved_lgacode': lgacode,
                'parentuid_for_create': '',
                'parent_source': '',
                'parent_match_type': 'unresolved',
                'parent_match_score': 0.0,
                'parent_candidate_count': int(len(candidates)),
                'reference_state': '',
                'reference_lga': '',
                'reference_ward': ''
            }

        matched_lga = candidates.iloc[0]
        reference_ward = ''
        ward_uid = ''
        match_status = 'resolved'
        match_notes = 'Matched against OU reference file'
        parent_match_type = 'unresolved'
        parent_match_score = 0.0
        parent_candidate_count = 0
        input_ward = str(row.get('ward', '') or '').strip()

        if ward_variants:
            ward_candidates = ward_reference_df[
                (ward_reference_df['lgauid'] == matched_lga['lgauid']) &
                (ward_reference_df['ward_key'].apply(lambda value: self._row_matches_variants(value, ward_variants)))
            ]
            parent_candidate_count = int(len(ward_candidates))

            if len(ward_candidates) == 1:
                matched_ward = ward_candidates.iloc[0]
                reference_ward = matched_ward['ward (level 4)']
                ward_uid = matched_ward['warduid']
                parent_match_type = 'exact_ward'
                parent_match_score = 100.0
            elif len(ward_candidates) > 1:
                fuzzy_uid, fuzzy_ward_name, fuzzy_score = self._fuzzy_match_ward_within_lga(
                    ward_input=input_ward,
                    lgauid=matched_lga['lgauid'],
                    ward_reference_df=ward_reference_df
                )
                if fuzzy_uid:
                    ward_uid = fuzzy_uid
                    reference_ward = fuzzy_ward_name
                    parent_match_type = 'fuzzy_ward'
                    parent_match_score = float(fuzzy_score)
                    match_status = 'resolved_with_warning' if fuzzy_score < self.parent_match_confident_threshold else 'resolved'
                    match_notes = f"Ward had multiple exact candidates; fuzzy-selected '{fuzzy_ward_name}' (score={fuzzy_score})."
                else:
                    match_status = 'resolved_with_warning'
                    match_notes = 'LGA matched, but ward matched multiple records'
            else:
                fuzzy_uid, fuzzy_ward_name, fuzzy_score = self._fuzzy_match_ward_within_lga(
                    ward_input=input_ward,
                    lgauid=matched_lga['lgauid'],
                    ward_reference_df=ward_reference_df
                )
                if fuzzy_uid:
                    ward_uid = fuzzy_uid
                    reference_ward = fuzzy_ward_name
                    parent_match_type = 'fuzzy_ward'
                    parent_match_score = float(fuzzy_score)
                    match_status = 'resolved_with_warning' if fuzzy_score < self.parent_match_confident_threshold else 'resolved'
                    match_notes = f"LGA matched; ward fuzzy-matched to '{fuzzy_ward_name}' (score={fuzzy_score})."
                else:
                    match_status = 'resolved_with_warning'
                    match_notes = 'LGA matched, but ward was not found in the reference file'

            if not ward_uid:
                unknown_ward_uid, unknown_ward_name = self._find_unknown_ward_uid(matched_lga['lgauid'], ward_reference_df)
                if unknown_ward_uid:
                    ward_uid = unknown_ward_uid
                    reference_ward = unknown_ward_name
                    parent_match_type = 'unknown_fallback'
                    parent_match_score = 60.0
                    match_status = 'resolved_with_warning'
                    match_notes = 'LGA matched; ward was provided but not matched, so Unknown Ward parent was assigned'
                else:
                    match_status = 'resolved_with_warning'
                    match_notes = 'LGA matched; ward was provided but not matched, and no Unknown Ward exists for this LGA'
        else:
            center_uid, center_ward_name, center_score = self._match_lga_center_ward(
                lga_name=matched_lga['lga (level3)'],
                lgauid=matched_lga['lgauid'],
                ward_reference_df=ward_reference_df
            )
            if center_uid:
                ward_uid = center_uid
                reference_ward = center_ward_name
                parent_match_type = 'lga_center'
                parent_match_score = float(center_score)
                match_status = 'resolved_with_warning'
                match_notes = f"LGA matched; ward blank, so LGA-center ward '{center_ward_name}' was assigned (score={center_score})."

            unknown_ward_uid, unknown_ward_name = self._find_unknown_ward_uid(matched_lga['lgauid'], ward_reference_df)
            if not ward_uid and unknown_ward_uid:
                ward_uid = unknown_ward_uid
                reference_ward = unknown_ward_name
                parent_match_type = 'unknown_fallback'
                parent_match_score = 60.0
                match_status = 'resolved_with_warning'
                match_notes = 'LGA matched; ward was blank, so Unknown Ward parent was assigned'
            elif not ward_uid:
                match_status = 'resolved_with_warning'
                match_notes = 'LGA matched; ward was blank and no Unknown Ward exists for this LGA'

        parentuid_for_create = ward_uid if str(ward_uid or '').strip() else ''
        parent_source = 'ward' if parentuid_for_create else ''

        return {
            'match_status': match_status,
            'match_notes': match_notes,
            'level2uid': matched_lga['lgaparentuid'],
            'lgauid': matched_lga['lgauid'],
            'warduid': ward_uid,
            'resolved_lgacode': matched_lga['lgacode (ssll)'],
            'parentuid_for_create': parentuid_for_create,
            'parent_source': parent_source,
            'parent_match_type': parent_match_type,
            'parent_match_score': round(float(parent_match_score), 1),
            'parent_candidate_count': int(parent_candidate_count),
            'reference_state': matched_lga['state (level2)'],
            'reference_lga': matched_lga['lga (level3)'],
            'reference_ward': reference_ward
        }

    def fetch_level5_under_multiple_level2(self, base_url, username, password, level2_ids, on_progress=None):
        all_ous = []
        total_states = len(level2_ids)

        for index, level2_id in enumerate(level2_ids, start=1):
            if on_progress:
                on_progress('state_start', index, total_states, level2_id, len(all_ous))

            state_ous = self.fetch_level5_under_level2(
                base_url=base_url,
                username=username,
                password=password,
                level2_id=level2_id,
                on_progress=(
                    lambda fetched, total_pages, page, idx=index, total=total_states, current_level2=level2_id:
                    on_progress('page', idx, total, current_level2, len(all_ous) + fetched, total_pages, page)
                ) if on_progress else None
            )
            all_ous.extend(state_ous)

        return all_ous

    def build_serial_tracker_from_level5_ous(self, level5_ous):
        max_serial_by_lga = {}
        invalid_code_rows = []

        for ou in level5_ous:
            current_code = str(ou.get('code') or '').strip()
            if not current_code:
                continue

            if not re.fullmatch(r'\d{10}', current_code):
                invalid_code_rows.append({
                    'id': ou.get('id', ''),
                    'name': ou.get('name', ''),
                    'current_code': current_code,
                    'reason': 'Existing code is not a 10-digit number'
                })
                continue

            lgacode = current_code[:4]
            serial = int(current_code[4:])
            max_serial_by_lga[lgacode] = max(max_serial_by_lga.get(lgacode, 0), serial)

        return max_serial_by_lga, invalid_code_rows

    def process_new_school_intake(self, uploaded_file, base_url, username, password, reference_path=None, reference_file=None):
        try:
            df = self._read_table_file(uploaded_file).fillna('')
            original_df = df.copy()
            df.columns = [str(col).lower().strip() for col in df.columns]
            df = self._rename_matching_columns(
                df,
                {
                    'state': ['state', 'state name', 'state_name', 'state (level2)'],
                    'lga': ['lga', 'lga name', 'lga_name', 'lga (level3)'],
                    'ward': ['ward', 'ward name', 'ward_name', 'ward (level 4)', 'ward (level4)'],
                    'school_name': ['school_name', 'school name', 'name', 'school', 'schoolname'],
                    'school_level': ['school_level', 'school level', 'level', 'schoollevel'],
                    'old_schoolcode': ['old_schoolcode', 'old schoolcode', 'old_school_code', 'old school code', 'previous_schoolcode', 'previous school code'],
                    'lgacode': ['lgacode', 'lga_code', 'lga code', 'lgacode (ssll)', 'ssll'],
                    'openingdate': ['openingdate', 'opening_date', 'opening date']
                }
            )

            if 'school_name' not in df.columns:
                st.error("Missing required column: 'school_name' (or school name/name)")
                return None, None, None

            if 'state' not in df.columns and 'lgacode' not in df.columns:
                st.error("Provide either 'state' plus 'lga', or a valid 'lgacode' column in the intake file.")
                return None, None, None

            if 'lga' not in df.columns and 'lgacode' not in df.columns:
                st.error("Provide either 'lga' or a valid 'lgacode' column in the intake file.")
                return None, None, None

            for optional_column in ['state', 'lga', 'ward', 'school_level', 'old_schoolcode', 'lgacode', 'openingdate']:
                if optional_column not in df.columns:
                    df[optional_column] = ''

            df['lgacode'] = df['lgacode'].astype(str).str.strip()
            df['lgacode'] = df['lgacode'].apply(lambda value: value.zfill(4) if value.isdigit() else value)
            df['school_level'] = df['school_level'].astype(str).str.strip()
            df['old_schoolcode'] = df['old_schoolcode'].astype(str).str.strip()
            df['openingdate'] = df['openingdate'].astype(str).str.strip()

            opening_date_raw = df['openingdate'].copy()
            opening_date_missing_mask = opening_date_raw.eq('')
            opening_date_parsed = pd.to_datetime(opening_date_raw, errors='coerce')
            opening_date_invalid_mask = (~opening_date_missing_mask) & opening_date_parsed.isna()
            opening_date_valid_mask = (~opening_date_missing_mask) & (~opening_date_invalid_mask)

            df.loc[opening_date_valid_mask, 'openingdate'] = opening_date_parsed[opening_date_valid_mask].dt.strftime('%Y-%m-%d')
            df.loc[opening_date_missing_mask | opening_date_invalid_mask, 'openingdate'] = '2024-01-01'

            reference_df, reference_file_path = self.load_ou_reference(reference_path=reference_path, reference_file=reference_file)
            lga_reference_df = reference_df[
                ['state (level2)', 'lga (level3)', 'lgauid', 'lgacode (ssll)', 'lgaparentuid', 'state_key', 'lga_key']
            ].drop_duplicates().reset_index(drop=True)
            ward_reference_df = reference_df[
                ['lgauid', 'ward (level 4)', 'warduid', 'ward_key']
            ].drop_duplicates().reset_index(drop=True)

            resolved_rows = []
            for _, row in df.iterrows():
                resolved_rows.append(self._resolve_school_row(row, lga_reference_df, ward_reference_df))

            resolved_df = pd.DataFrame(resolved_rows)
            result_df = pd.concat([df.reset_index(drop=True), resolved_df], axis=1)
            result_df['input_lgacode'] = result_df['lgacode']
            result_df['lgacode'] = result_df['resolved_lgacode'].where(
                result_df['resolved_lgacode'].astype(str).str.strip() != '',
                result_df['input_lgacode']
            )
            result_df['school_code'] = ''
            result_df['allocated_serial'] = ''
            result_df['existing_max_serial'] = ''

            eligible_mask = result_df['match_status'].isin(['resolved', 'resolved_with_warning']) & result_df['lgacode'].astype(str).str.match(r'^\d{4}$')
            eligible_df = result_df[eligible_mask]
            level2_ids = sorted({str(value).strip() for value in eligible_df['level2uid'].tolist() if str(value).strip()})

            all_level5_ous = []
            if level2_ids:
                all_level5_ous = self.fetch_level5_under_multiple_level2(
                    base_url=base_url,
                    username=username,
                    password=password,
                    level2_ids=level2_ids
                )

            max_serial_by_lga, invalid_existing_codes = self.build_serial_tracker_from_level5_ous(all_level5_ous)
            existing_code_set = {
                str(ou.get('code')).strip()
                for ou in all_level5_ous
                if re.fullmatch(r'\d{10}', str(ou.get('code') or '').strip())
            }

            lga_stats = []
            final_duplicates = []
            for lgacode, lga_rows in eligible_df.groupby('lgacode', sort=False):
                indices = lga_rows.index.tolist()
                start_serial = max_serial_by_lga.get(lgacode, 0) + 1

                for offset, idx in enumerate(indices, start=0):
                    serial_value = start_serial + offset
                    serial_text = str(serial_value).zfill(6)
                    school_code = f"{lgacode}{serial_text}"
                    result_df.at[idx, 'allocated_serial'] = serial_text
                    result_df.at[idx, 'existing_max_serial'] = max_serial_by_lga.get(lgacode, 0)
                    result_df.at[idx, 'school_code'] = school_code
                    if school_code in existing_code_set:
                        final_duplicates.append(school_code)

                lga_stats.append({
                    'lgacode': lgacode,
                    'reference_lga': lga_rows['reference_lga'].iloc[0],
                    'new_schools': len(indices),
                    'existing_max_serial': max_serial_by_lga.get(lgacode, 0),
                    'start_serial': start_serial,
                    'end_serial': start_serial + len(indices) - 1
                })

            # Enforce school name format: PREFIX School Name (CODE)
            # for rows that have a valid generated school_code.
            school_name_formatted_count = 0
            school_level_missing_count = 0
            school_level_invalid_count = 0
            old_schoolcode_used_count = 0
            old_schoolcode_invalid_ten_digit_count = 0
            result_df['school_level_normalized'] = ''
            result_df['name_format_valid'] = False
            result_df['name_suffix_code_used'] = ''
            code_mask = result_df['school_code'].astype(str).str.match(r'^\d{10}$')
            for idx in result_df[code_mask].index:
                original_name = str(result_df.at[idx, 'school_name'] or '').strip()
                level_value = str(result_df.at[idx, 'school_level'] or '').strip()
                raw_old_schoolcode = str(result_df.at[idx, 'old_schoolcode'] or '').strip()
                generated_code = self._normalize_code_for_name_suffix(result_df.at[idx, 'school_code'], source='generated')
                old_code = self._normalize_code_for_name_suffix(raw_old_schoolcode, source='old_schoolcode')
                name_suffix_code = old_code or generated_code
                formatted_name, normalized_prefix, is_valid_format = self._format_school_name_with_prefix_and_code(
                    school_name=original_name,
                    school_code=name_suffix_code,
                    school_level=level_value
                )

                if old_code:
                    old_schoolcode_used_count += 1
                elif raw_old_schoolcode and re.fullmatch(r'\d{10}', raw_old_schoolcode):
                    old_schoolcode_invalid_ten_digit_count += 1

                if not str(level_value).strip():
                    school_level_missing_count += 1
                elif not self._normalize_school_level(level_value):
                    school_level_invalid_count += 1

                result_df.at[idx, 'school_level_normalized'] = normalized_prefix
                result_df.at[idx, 'name_format_valid'] = bool(is_valid_format)
                result_df.at[idx, 'name_suffix_code_used'] = name_suffix_code
                if formatted_name and formatted_name != original_name:
                    result_df.at[idx, 'school_name'] = formatted_name
                    school_name_formatted_count += 1

            result_df['can_post'] = (
                result_df['match_status'].isin(['resolved', 'resolved_with_warning']) &
                result_df['school_code'].astype(str).str.match(r'^\d{10}$') &
                result_df['parentuid_for_create'].astype(str).str.strip().ne('') &
                result_df['parent_match_type'].astype(str).str.strip().ne('unresolved') &
                result_df['name_format_valid'].astype(bool) &
                result_df['school_name'].astype(str).str.strip().ne('')
            )

            unresolved_df = result_df[result_df['match_status'] == 'unresolved']
            parent_match_counts = result_df['parent_match_type'].astype(str).value_counts().to_dict() if 'parent_match_type' in result_df.columns else {}
            fuzzy_low_confidence_count = int(
                (
                    result_df['parent_match_type'].astype(str).eq('fuzzy_ward') &
                    (pd.to_numeric(result_df['parent_match_score'], errors='coerce').fillna(0) < float(self.parent_match_confident_threshold))
                ).sum()
            ) if 'parent_match_score' in result_df.columns else 0
            processing_stats = {
                'reference_file_path': reference_file_path,
                'input_rows': len(result_df),
                'resolved_rows': int(eligible_mask.sum()),
                'warning_rows': int((result_df['match_status'] == 'resolved_with_warning').sum()),
                'unresolved_rows': len(unresolved_df),
                'affected_states': len(level2_ids),
                'affected_lgas': eligible_df['lgacode'].nunique(),
                'level5_ous_fetched': len(all_level5_ous),
                'invalid_existing_codes': invalid_existing_codes,
                'invalid_existing_codes_count': len(invalid_existing_codes),
                'lga_stats': lga_stats,
                'duplicate_count': len(final_duplicates),
                'final_duplicates': final_duplicates,
                'school_name_formatted_count': int(school_name_formatted_count),
                'school_level_missing_count': int(school_level_missing_count),
                'school_level_invalid_count': int(school_level_invalid_count),
                'old_schoolcode_used_count': int(old_schoolcode_used_count),
                'old_schoolcode_invalid_ten_digit_count': int(old_schoolcode_invalid_ten_digit_count),
                'openingdate_defaulted_count': int((opening_date_missing_mask | opening_date_invalid_mask).sum()),
                'openingdate_invalid_count': int(opening_date_invalid_mask.sum()),
                'ready_to_post_count': int(result_df['can_post'].sum()),
                'parent_match_counts': parent_match_counts,
                'fuzzy_low_confidence_count': fuzzy_low_confidence_count,
                'unresolved_preview': unresolved_df[['school_name', 'state', 'lga', 'ward', 'match_notes']].head(20).to_dict('records')
            }

            output_columns = [
                'school_code', 'school_ou_uid', 'school_level', 'old_schoolcode', 'name_suffix_code_used',
                'school_level_normalized', 'name_format_valid',
                'allocated_serial', 'existing_max_serial', 'openingdate', 'lgacode', 'input_lgacode', 'level2uid',
                'lgauid', 'warduid', 'parentuid_for_create', 'parent_source', 'parent_match_type', 'parent_match_score',
                'parent_candidate_count', 'match_status', 'match_notes', 'reference_state',
                'reference_lga', 'reference_ward'
            ]
            for column in output_columns:
                if column not in result_df.columns:
                    result_df[column] = ''

            ordered_columns = output_columns + [
                column for column in result_df.columns if column not in output_columns
            ]
            result_df = result_df[ordered_columns]

            original_stats = self.analyze_uploaded_file(original_df)
            return result_df, original_stats, processing_stats
        except Exception as e:
            st.error(f"Error: {str(e)}")
            import traceback
            st.error(f"Traceback: {traceback.format_exc()}")
            return None, None, None

    def check_duplicate_names_on_dhis2(self, base_url, username, password, intake_df):
        """
        For every row in intake_df that is flagged for CREATE (no existing UID yet),
        query DHIS2 for all Level-5 OUs under the same LGA and return name-match details.

        Returns a list of dicts:
          incoming_school_name, incoming_school_code, lgauid, reference_lga,
          matched_dhis2_name, matched_dhis2_code, matched_dhis2_uid, match_type
        """
        def _norm(text):
            return re.sub(r'[\s\W]+', ' ', str(text or '').lower()).strip()

        create_rows = intake_df[
            intake_df.get('can_post', intake_df.index.isin(intake_df.index)).astype(bool) &
            intake_df['school_ou_uid'].apply(lambda v: not str(v or '').strip())
        ].copy() if 'school_ou_uid' in intake_df.columns else intake_df.copy()

        unique_lga_uids = [
            uid for uid in create_rows['lgauid'].dropna().unique()
            if re.fullmatch(r'[A-Za-z][A-Za-z0-9]{10}', str(uid or '').strip())
        ] if 'lgauid' in create_rows.columns else []

        # Build lookup: lgauid -> list of existing Level-5 OUs
        lga_children = {}
        for lgauid in unique_lga_uids:
            try:
                resp = self._dhis_request(
                    method='GET',
                    base_url=base_url,
                    username=username,
                    password=password,
                    endpoint='/organisationUnits',
                    params={
                        'fields': 'id,name,code',
                        'filter': f'level:eq:5',
                        'filter': f'path:like:{lgauid}',
                        'paging': 'false'
                    },
                    timeout=60
                )
                lga_children[lgauid] = resp.json().get('organisationUnits', [])
            except Exception:
                lga_children[lgauid] = []

        matches = []
        for _, row in create_rows.iterrows():
            lgauid = str(row.get('lgauid') or '').strip()
            incoming_name = str(row.get('school_name') or '').strip()
            incoming_code = str(row.get('school_code') or '').strip()
            incoming_norm = _norm(incoming_name)
            if not lgauid or not incoming_name:
                continue

            for existing_ou in lga_children.get(lgauid, []):
                existing_name = str(existing_ou.get('name') or '').strip()
                existing_norm = _norm(existing_name)
                if not existing_norm:
                    continue
                if incoming_norm == existing_norm:
                    match_type = 'EXACT'
                elif incoming_norm in existing_norm or existing_norm in incoming_norm:
                    match_type = 'PARTIAL'
                else:
                    continue
                matches.append({
                    'incoming_school_name': incoming_name,
                    'incoming_school_code': incoming_code,
                    'lgauid': lgauid,
                    'reference_lga': str(row.get('reference_lga') or row.get('lga') or ''),
                    'matched_dhis2_name': existing_name,
                    'matched_dhis2_code': str(existing_ou.get('code') or ''),
                    'matched_dhis2_uid': str(existing_ou.get('id') or ''),
                    'match_type': match_type
                })

        return matches

    def post_new_schools_to_dhis2(self, base_url, username, password, intake_df, dry_run=False):
        def _safe_response_payload(response):
            try:
                return response.json()
            except Exception:
                return {'raw': response.text}

        def _fetch_existing_by_codes(codes, expected_name_by_code=None):
            if not codes:
                return {}

            expected_name_by_code = expected_name_by_code or {}

            def _normalize_name(name_value):
                return re.sub(r'\s+', ' ', str(name_value or '').strip().lower())

            def _pick_better_match(current_ou, candidate_ou, expected_name):
                if current_ou is None:
                    return candidate_ou

                def _score(ou):
                    score = 0
                    ou_name = _normalize_name((ou or {}).get('name'))
                    target_name = _normalize_name(expected_name)
                    if target_name and ou_name == target_name:
                        score += 10
                    if str((((ou or {}).get('parent') or {}).get('id')) or '').strip():
                        score += 2
                    if str((ou or {}).get('openingDate') or '').strip():
                        score += 1
                    return score

                return candidate_ou if _score(candidate_ou) > _score(current_ou) else current_ou

            existing = {}
            code_list = sorted(set(codes))
            chunk_size = 25
            for start in range(0, len(code_list), chunk_size):
                chunk = code_list[start:start + chunk_size]
                chunk_text = ','.join(chunk)
                response = self._dhis_request(
                    method='GET',
                    base_url=base_url,
                    username=username,
                    password=password,
                    endpoint='/organisationUnits',
                    params={
                        'fields': 'id,code,name,parent[id],openingDate',
                        'filter': f'code:in:[{chunk_text}]',
                        'paging': 'false'
                    },
                    timeout=60
                )
                ous = response.json().get('organisationUnits', [])
                for ou in ous:
                    code = str(ou.get('code') or '').strip()
                    if code:
                        expected_name = expected_name_by_code.get(code, '')
                        existing[code] = _pick_better_match(existing.get(code), ou, expected_name)

                # Fallback: some DHIS2 servers may not honor code:in filters as expected.
                if len(ous) == 0 and len(chunk) > 0:
                    for code in chunk:
                        single_response = self._dhis_request(
                            method='GET',
                            base_url=base_url,
                            username=username,
                            password=password,
                            endpoint='/organisationUnits',
                            params={
                                'fields': 'id,code,name,parent[id],openingDate',
                                'filter': f'code:eq:{code}',
                                'paging': 'false'
                            },
                            timeout=30
                        )
                        single_ous = single_response.json().get('organisationUnits', [])
                        for ou in single_ous:
                            expected_name = expected_name_by_code.get(code, '')
                            existing[code] = _pick_better_match(existing.get(code), ou, expected_name)

            return existing

        if intake_df is None or len(intake_df) == 0:
            return {'status': 'NO_DATA', 'message': 'No intake rows to publish', 'response': {}}

        required_columns = ['school_name', 'school_code', 'parentuid_for_create', 'openingdate']
        missing_columns = [column for column in required_columns if column not in intake_df.columns]
        if missing_columns:
            return {
                'status': 'INVALID_INPUT',
                'message': f"Intake output is missing required columns: {', '.join(missing_columns)}",
                'response': {}
            }

        rows = intake_df.copy().fillna('')
        if 'can_post' in rows.columns:
            can_post_mask = rows['can_post'].astype(bool)
        else:
            can_post_mask = (
                rows['school_code'].astype(str).str.match(r'^\d{10}$') &
                rows['parentuid_for_create'].astype(str).str.strip().ne('')
            )

        rows_to_post = rows[can_post_mask].reset_index(drop=True)
        if len(rows_to_post) == 0:
            return {
                'status': 'NO_UPDATES',
                'message': 'No rows are ready to be posted. Resolve wards/LGAs first.',
                'response': {}
            }

        incoming_codes = [
            str(code).strip() for code in rows_to_post['school_code'].tolist()
            if re.fullmatch(r'\d{10}', str(code or '').strip())
        ]

        expected_name_by_code = {}
        for _, row in rows_to_post.iterrows():
            _code = str(row.get('school_code', '') or '').strip()
            if re.fullmatch(r'\d{10}', _code) and _code not in expected_name_by_code:
                expected_name_by_code[_code] = str(row.get('school_name', '') or '').strip()

        existing_by_code = {}
        lookup_warning = ''
        try:
            existing_by_code = _fetch_existing_by_codes(incoming_codes, expected_name_by_code=expected_name_by_code)
        except Exception as e:
            # Continue publish even when lookup fails; metadata upsert with identifier=CODE can still update existing rows.
            lookup_warning = f"Pre-publish existing-code lookup failed and was skipped: {e}"
            existing_by_code = {}

        # Prefer UID-based import to match payload references (id/uid, parent.id).
        # If pre-lookup failed entirely, fall back to CODE strategy to avoid hard failures.
        metadata_identifier = 'UID' if not lookup_warning else 'CODE'

        payload_rows = []
        skipped_rows = []
        seen_codes = set()
        create_count = 0
        update_count = 0

        def _clean_dhis_uid(uid_value):
            uid_text = str(uid_value or '').strip()
            # DHIS2 UID format: 11 chars, starts with a letter.
            if re.fullmatch(r'[A-Za-z][A-Za-z0-9]{10}', uid_text):
                return uid_text
            return ''

        for _, row in rows_to_post.iterrows():
            school_name = str(row.get('school_name', '') or '').strip()
            school_code = str(row.get('school_code', '') or '').strip()
            parent_uid = _clean_dhis_uid(row.get('parentuid_for_create', ''))
            opening_date = str(row.get('openingdate', '') or '').strip() or '2024-01-01'

            existing = existing_by_code.get(school_code)
            existing_parent_uid = _clean_dhis_uid((((existing or {}).get('parent') or {}).get('id')))
            resolved_parent_uid = parent_uid or existing_parent_uid

            if not school_name or not school_code:
                skipped_rows.append({
                    'school_name': school_name,
                    'school_code': school_code,
                    'reason': 'Missing required value among school_name and school_code'
                })
                continue

            if (not existing) and (not resolved_parent_uid):
                skipped_rows.append({
                    'school_name': school_name,
                    'school_code': school_code,
                    'reason': 'Missing valid parent UID for create row (parentuid_for_create)'
                })
                continue

            if school_code in seen_codes:
                skipped_rows.append({
                    'school_name': school_name,
                    'school_code': school_code,
                    'reason': 'Duplicate school_code inside the current upload set'
                })
                continue

            seen_codes.add(school_code)
            payload_row = {
                'name': school_name,
                'shortName': school_name[:50] if school_name else school_code,
                'code': school_code,
                'openingDate': opening_date
            }

            # For new OUs, parent is required. For existing OUs, only send parent when valid.
            if resolved_parent_uid:
                payload_row['parent'] = {'id': resolved_parent_uid}

            if existing:
                existing_uid = str(existing.get('id') or '').strip()
                if existing_uid:
                    payload_row['id'] = existing_uid
                    payload_row['uid'] = existing_uid
                update_count += 1
            else:
                create_count += 1

            payload_rows.append(payload_row)

        if len(payload_rows) == 0:
            return {
                'status': 'NO_UPDATES',
                'message': 'No valid rows to publish after validation',
                'response': {'skipped': skipped_rows}
            }

        try:
            response = self._dhis_request(
                method='POST',
                base_url=base_url,
                username=username,
                password=password,
                endpoint='/metadata',
                params={
                    'importMode': 'COMMIT',
                    'dryRun': 'true' if dry_run else 'false',
                    'importStrategy': 'CREATE_AND_UPDATE',
                    'identifier': metadata_identifier,
                    'atomicMode': 'NONE'
                },
                json_data={'organisationUnits': payload_rows},
                timeout=180
            )
            dhis2_payload = _safe_response_payload(response)
        except requests.HTTPError as e:
            http_response = getattr(e, 'response', None)
            dhis2_payload = _safe_response_payload(http_response) if http_response is not None else {'error': str(e)}

            import_report = (dhis2_payload or {}).get('response', {})
            stats = (import_report or {}).get('stats', {})
            created = int(stats.get('created', 0) or 0)
            updated = int(stats.get('updated', 0) or 0)
            deleted = int(stats.get('deleted', 0) or 0)
            ignored = int(stats.get('ignored', 0) or 0)
            total = int(stats.get('total', 0) or 0)

            # Some DHIS2 instances return HTTP 409 with status WARNING even when rows were applied.
            warning_but_applied = total > 0 and ignored == 0 and (created + updated + deleted) == total
            if not warning_but_applied:
                return {
                    'status': 'FAILED',
                    'message': (
                        'DNEMIS rejected part or all of the upsert request. '
                        'Review response.details for conflicts (409).'
                    ),
                    'response': {
                        'dhis2': dhis2_payload,
                        'prepared': len(payload_rows),
                        'to_create': create_count,
                        'to_update': update_count,
                        'skipped': skipped_rows,
                        'http_error': str(e),
                        'lookup_warning': lookup_warning
                    }
                }

        # Seed uid_by_code with pre-lookup UIDs for already-existing schools.
        # These are the canonical DHIS2 UIDs and never change on an in-place update.
        uid_by_code = {}

        # Highest-confidence mapping: DHIS2 import report objectReports are index-aligned
        # with request payload order and include the actual OU UID affected.
        object_reports = ((dhis2_payload or {}).get('response', {}) or {}).get('objectReports', [])
        for object_report in object_reports:
            try:
                index_value = int((object_report or {}).get('index'))
            except Exception:
                continue
            if index_value < 0 or index_value >= len(payload_rows):
                continue
            code_at_index = str((payload_rows[index_value] or {}).get('code') or '').strip()
            uid_value = str((object_report or {}).get('uid') or '').strip()
            if code_at_index and uid_value:
                uid_by_code[code_at_index] = uid_value

        # Pre-lookup UIDs are canonical for known existing schools; only use when objectReports
        # did not provide the mapping for that code.
        for _code, _ou in existing_by_code.items():
            if _code in uid_by_code:
                continue
            _ou_id = str((_ou or {}).get('id') or '').strip()
            if _ou_id:
                uid_by_code[_code] = _ou_id

        # Post-lookup only for newly created schools (not already in uid_by_code).
        new_school_codes = [
            item['code'] for item in payload_rows if item['code'] not in uid_by_code
        ]
        if new_school_codes:
            try:
                post_lookup = _fetch_existing_by_codes(new_school_codes, expected_name_by_code=expected_name_by_code)
                for _code, _ou in post_lookup.items():
                    _ou_id = str((_ou or {}).get('id') or '').strip()
                    if _ou_id:
                        uid_by_code[_code] = _ou_id
            except Exception:
                pass

        is_warning = str((dhis2_payload or {}).get('status', '')).upper() == 'WARNING'
        final_status = 'DRY_RUN' if dry_run else ('POSTED_WITH_WARNING' if is_warning else 'POSTED')
        final_message = (
            f"Prepared {len(payload_rows)} OU upserts ({create_count} create, {update_count} update) in dry run."
            if dry_run else
            f"Submitted {len(payload_rows)} OU upserts to DHIS2 ({create_count} create, {update_count} update)."
        )
        if is_warning and not dry_run:
            final_message = f"{final_message} DNEMIS returned WARNING (check import report details)."

        import_report = (dhis2_payload or {}).get('response', {})
        import_stats = (import_report or {}).get('stats', {})
        actual_created = int(import_stats.get('created', create_count) or 0)
        actual_updated = int(import_stats.get('updated', update_count) or 0)

        return {
            'status': final_status,
            'message': final_message,
            'response': {
                'dhis2': dhis2_payload,
                'prepared': len(payload_rows),
                'to_create': actual_created,
                'to_update': actual_updated,
                'planned_to_create': create_count,
                'planned_to_update': update_count,
                'uid_by_code': uid_by_code,
                'metadata_identifier': metadata_identifier,
                'lookup_warning': lookup_warning,
                'skipped': skipped_rows
            }
        }
    
    def analyze_existing_codes(self, state_code, existing_codes):
        lga_analysis = {}
        
        for code in existing_codes:
            code_str = str(code).strip()
            if len(code_str) == 10 and code_str.startswith(state_code):
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
                serial_number = str(next_serial + i).zfill(6)
                school_code = f"{state_code}{lga_code}{serial_number}"
                generated_codes.append({
                    'State': state_name.title(),
                    'LGA': lga_name.title(),
                    'LGA_Code': lga_code,
                    'School_Code': school_code,
                    'Serial_Number': serial_number
                })
        
        return generated_codes

    def analyze_uploaded_file(self, df):
        """Analyze the uploaded school list file and return statistics"""
        stats = {}
        
        # Basic statistics
        stats['total_schools'] = len(df)
        stats['total_columns'] = len(df.columns)
        
        # Column analysis
        stats['columns'] = list(df.columns)
        stats['missing_values'] = df.isnull().sum().to_dict()
        stats['missing_values_total'] = df.isnull().sum().sum()
        
        # LGA analysis
        if 'lgacode' in df.columns:
            stats['unique_lgas'] = df['lgacode'].nunique()
            stats['lga_distribution'] = df['lgacode'].value_counts().head(10).to_dict()
        
        # State analysis
        if 'state' in df.columns:
            stats['unique_states'] = df['state'].nunique()
            stats['state_distribution'] = df['state'].value_counts().head(10).to_dict()
        
        # School code analysis if already exists
        if 'school_code' in df.columns:
            existing_codes = df['school_code'].dropna()
            stats['existing_codes_count'] = len(existing_codes)
            stats['invalid_codes'] = existing_codes[~existing_codes.astype(str).str.match(r'^\d{10}$')].tolist()
            stats['invalid_codes_count'] = len(stats['invalid_codes'])
        
        return stats
    
    def check_for_duplicates(self, generated_codes, existing_codes):
        """Check for duplicates between generated and existing codes"""
        duplicates = []
        duplicate_details = []
        
        if existing_codes:
            existing_set = set([str(c).strip() for c in existing_codes if str(c).strip()])
            generated_list = [str(c).strip() for c in generated_codes if str(c).strip()]
            
            for code in generated_list:
                if code in existing_set:
                    duplicates.append(code)
                    # Try to find more details about the duplicate
                    duplicate_details.append({
                        'code': code,
                        'type': 'Duplicate with existing code'
                    })
        
        return duplicates, duplicate_details
    
    def process_school_list_file(self, uploaded_file, existing_codes_file=None):
        try:
            # Read the uploaded file
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file, dtype=str)
            else:
                df = pd.read_excel(uploaded_file, dtype=str)
            
            # Store original for statistics
            original_df = df.copy()
            
            # Fill NaN values
            df = df.fillna('')
            
            # Convert column names to lowercase for consistency
            df.columns = [str(col).lower().strip() for col in df.columns]
            
            # Check for required columns
            required_columns = ['state', 'lga', 'school_name', 'lgacode']
            for col in required_columns:
                if col not in df.columns:
                    st.error(f"Missing required column: '{col}'")
                    return None, None, None, None
            
            # Process lgacode - ensure it's 4 digits
            df['lgacode'] = df['lgacode'].astype(str).str.strip()
            df['lgacode'] = df['lgacode'].apply(lambda x: x.zfill(4) if x.isdigit() else x)
            
            # Validate lgacode format
            invalid_mask = ~df['lgacode'].str.match(r'^\d{4}$')
            if invalid_mask.any():
                invalid_count = invalid_mask.sum()
                st.error(f"Found {invalid_count} invalid lgacodes. Must be 4 digits.")
                return None, None, None, None
            
            # Read existing codes
            existing_codes = set()
            existing_codes_list = []
            if existing_codes_file:
                existing_codes_list = self.read_existing_codes(existing_codes_file)
                existing_codes = set([str(c).strip() for c in existing_codes_list if str(c).strip()])
            
            # Initialize school_code column
            df['school_code'] = ''
            
            # Track processing statistics
            processing_stats = {
                'lga_stats': [],
                'total_duplicates_avoided': 0,
                'max_serial_per_lga': {},
                'codes_generated': 0
            }
            
            # Group by LGA and generate codes
            for lgacode in df['lgacode'].unique():
                if not lgacode:
                    continue
                
                # Get indices for this LGA
                lga_indices = df.index[df['lgacode'] == lgacode].tolist()
                num_schools = len(lga_indices)
                
                # Get existing serials for this LGA
                existing_serials = []
                duplicate_codes_in_lga = []
                for code in existing_codes:
                    code_str = str(code).strip()
                    # Check if code matches this LGA and is 10 digits
                    if code_str.startswith(lgacode) and len(code_str) == 10:
                        try:
                            serial = int(code_str[4:])  # Extract the last 6 digits
                            existing_serials.append(serial)
                            duplicate_codes_in_lga.append(code_str)
                        except:
                            pass
                
                # Start from next available serial
                start_serial = max(existing_serials) + 1 if existing_serials else 1
                
                # Generate codes for each school in this LGA
                generated_codes_for_lga = []
                for i, idx in enumerate(lga_indices):
                    serial_num = str(start_serial + i).zfill(6)
                    school_code = f"{lgacode}{serial_num}"
                    df.at[idx, 'school_code'] = school_code
                    generated_codes_for_lga.append(school_code)
                
                # Track stats for this LGA
                lga_stats = {
                    'lgacode': lgacode,
                    'num_schools': num_schools,
                    'start_serial': start_serial,
                    'end_serial': start_serial + num_schools - 1,
                    'existing_serials_count': len(existing_serials),
                    'duplicate_codes_avoided': duplicate_codes_in_lga,
                    'generated_codes': generated_codes_for_lga[:5]  # First 5 for preview
                }
                processing_stats['lga_stats'].append(lga_stats)
                processing_stats['total_duplicates_avoided'] += len(duplicate_codes_in_lga)
                processing_stats['max_serial_per_lga'][lgacode] = start_serial + num_schools - 1
                processing_stats['codes_generated'] += num_schools
            
            # Check for any duplicates that might have been created
            generated_codes_list = [code for code in df['school_code'].tolist() if str(code).strip() != '']
            duplicates, duplicate_details = self.check_for_duplicates(generated_codes_list, existing_codes_list)
            
            # Update processing stats with duplicate info
            processing_stats['final_duplicates'] = duplicates
            processing_stats['duplicate_details'] = duplicate_details
            processing_stats['duplicate_count'] = len(duplicates)
            
            # Analyze original file for statistics
            original_stats = self.analyze_uploaded_file(original_df)
            
            # Ensure all expected columns exist
            expected_columns = [
                'school_code', 'lgacode', 'category', 'state', 'lga', 'ward', 
                'school_name', 'prefix', 'town', 'location', 'school_level', 
                'year', 'set_name'
            ]
            
            for col in expected_columns:
                if col not in df.columns:
                    df[col] = ''
            
            # Reorder columns
            df = df[expected_columns]
            
            return df, original_stats, processing_stats, duplicates
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            import traceback
            st.error(f"Traceback: {traceback.format_exc()}")
            return None, None, None, None

    def _normalize_dhis_api_base(self, base_url):
        base = str(base_url or "").strip().rstrip("/")
        if not base:
            raise ValueError("DHIS2 base URL is required")

        if base.endswith("/api"):
            return base

        if "/api/" in base:
            return base.split("/api/")[0] + "/api"

        return f"{base}/api"

    def _dhis_request(self, method, base_url, username, password, endpoint, params=None, json_data=None, timeout=60):
        api_base = self._normalize_dhis_api_base(base_url)
        url = f"{api_base}{endpoint}"
        response = requests.request(
            method=method,
            url=url,
            params=params,
            json=json_data,
            auth=(username, password),
            timeout=timeout,
            headers={"Accept": "application/json"}
        )
        response.raise_for_status()
        return response

    def fetch_level2_ous(self, base_url, username, password):
        params = {
            "fields": "id,name,code,level",
            "filter": "level:eq:2",
            "order": "name:asc",
            "paging": "false"
        }

        response = self._dhis_request(
            method="GET",
            base_url=base_url,
            username=username,
            password=password,
            endpoint="/organisationUnits",
            params=params
        )
        return response.json().get("organisationUnits", [])

    def fetch_level5_under_level2(self, base_url, username, password, level2_id, on_progress=None):
        """Fetch all level-5 OUs under a level-2 OU using pagination.
        on_progress(fetched, total_pages, page) is called after each page if provided."""
        all_ous = []
        page = 1
        page_size = 1000
        total_pages = None
        while True:
            params = {
                "fields": "id,name,code,shortName,openingDate,closedDate,geometry,parent[id]",
                "filter": [
                    "level:eq:5",
                    f"path:like:/{level2_id}"
                ],
                "order": "name:asc",
                "paging": "true",
                "page": str(page),
                "pageSize": str(page_size),
            }
            response = self._dhis_request(
                method="GET",
                base_url=base_url,
                username=username,
                password=password,
                endpoint="/organisationUnits",
                params=params
            )
            data = response.json()
            ous = data.get("organisationUnits", [])
            all_ous.extend(ous)
            pager = data.get("pager", {})
            total_pages = pager.get("pageCount", 1)
            if on_progress:
                on_progress(len(all_ous), total_pages, page)
            if page >= total_pages or len(ous) == 0:
                break
            page += 1
        return all_ous

    def _extract_level3_lga(self, ou):
        """Derive 4-digit LGA code from available school code hints."""
        current_code = str(ou.get("code") or "").strip()
        if re.fullmatch(r"\d{10}", current_code):
            lga_code = current_code[:4]
            return {"id": "", "name": self._lookup_lga_name_from_code(lga_code), "code": lga_code}

        school_name = str(ou.get("name") or "")
        old_code = self._extract_old_code_from_school_name(school_name)
        if re.fullmatch(r"\d{4,10}", old_code):
            lga_code = old_code[:4]
            return {"id": "", "name": self._lookup_lga_name_from_code(lga_code), "code": lga_code}

        return {"id": "", "name": "", "code": ""}

    def _extract_old_code_from_school_name(self, school_name):
        school_name_str = str(school_name or "").strip()
        match = re.search(r"\((\d{4,10})\)\s*$", school_name_str)
        return match.group(1) if match else ""

    def _lookup_lga_name_from_code(self, lga_code):
        """Resolve LGA name from 4-digit SSLL code using local state/LGA mappings."""
        code = str(lga_code or "").strip()
        if not re.fullmatch(r"\d{4}", code):
            return ""

        state_code = code[:2]
        local_lga_code = code[2:]

        state_name = ""
        for name, s_code in self.state_codes.items():
            if s_code == state_code:
                state_name = name
                break

        if not state_name:
            return ""

        lga_map = self.lga_codes.get(state_name, {})
        for lga_name, lg_code in lga_map.items():
            if str(lg_code).zfill(2) == local_lga_code:
                return lga_name

        return ""

    def generate_level5_code_updates(self, level5_ous):
        updates = []
        serial_by_prefix = {}

        # Seed serial counters from valid existing codes matching the LGA prefix.
        for ou in level5_ous:
            lga = self._extract_level3_lga(ou)
            lga_code = lga.get("code", "")
            current_code = str(ou.get("code") or "").strip()

            if not re.fullmatch(r"\d{4}", lga_code):
                continue

            if re.fullmatch(r"\d{10}", current_code) and current_code.startswith(lga_code):
                serial = int(current_code[4:])
                serial_by_prefix[lga_code] = max(serial_by_prefix.get(lga_code, 0), serial)

        for ou in level5_ous:
            school_name = str(ou.get("name") or "")
            old_code = self._extract_old_code_from_school_name(school_name)
            parent_uid = str((ou.get("parent") or {}).get("id") or "")
            lga = self._extract_level3_lga(ou)
            lga_name = lga.get("name", "")
            lga_code = lga.get("code", "")
            current_code = str(ou.get("code") or "").strip()

            if not re.fullmatch(r"\d{4}", lga_code):
                updates.append({
                    "id": ou.get("id"),
                    "parent_uid": parent_uid,
                    "name": school_name,
                    "old_code": old_code,
                    "lga_name": lga_name,
                    "lga_code": lga_code,
                    "current_code": current_code,
                    "new_code": "",
                    "action": "skip",
                    "reason": "Level-3 LGA code is missing or not 4 digits"
                })
                continue

            # Keep existing valid 10-digit codes unchanged.
            is_valid = bool(re.fullmatch(r"\d{10}", current_code) and current_code.startswith(lga_code))
            if is_valid:
                updates.append({
                    "id": ou.get("id"),
                    "parent_uid": parent_uid,
                    "name": school_name,
                    "old_code": old_code,
                    "lga_name": lga_name,
                    "lga_code": lga_code,
                    "current_code": current_code,
                    "new_code": current_code,
                    "action": "keep",
                    "reason": "Existing code is already valid"
                })
                continue

            next_serial = serial_by_prefix.get(lga_code, 0) + 1
            serial_by_prefix[lga_code] = next_serial
            new_code = f"{lga_code}{str(next_serial).zfill(6)}"

            updates.append({
                "id": ou.get("id"),
                "parent_uid": parent_uid,
                "name": school_name,
                "old_code": old_code,
                "lga_name": lga_name,
                "lga_code": lga_code,
                "current_code": current_code,
                "new_code": new_code,
                "action": "update",
                "reason": "Generated next code within LGA"
            })

        return updates

    def apply_level5_code_updates(self, base_url, username, password, updates, update_mode="put_merge"):
        update_rows = [
            item for item in updates
            if item.get("action") == "update" and item.get("new_code") and item.get("id")
        ]

        if not update_rows:
            return {"status": "NO_UPDATES", "message": "No organisation units to update", "response": {}}

        if update_mode == "metadata_bulk":
            payload_updates = [
                {"id": item["id"], "code": item["new_code"]}
                for item in update_rows
            ]

            response = self._dhis_request(
                method="POST",
                base_url=base_url,
                username=username,
                password=password,
                endpoint="/metadata",
                params={
                    "importMode": "UPDATE",
                    "identifier": "UID"
                },
                json_data={"organisationUnits": payload_updates},
                timeout=120
            )

            return {
                "status": "UPDATED",
                "message": f"Submitted {len(payload_updates)} updates via bulk /metadata mode",
                "response": response.json(),
                "mode": "metadata_bulk"
            }

        readonly_fields = [
            "lastUpdated", "created", "href", "lastUpdatedBy", "createdBy",
            "displayName", "displayShortName", "displayFormName", "displayDescription",
            "displayOpeningDate", "displayClosedDate", "path", "children", "leaf",
            "access", "user", "favorites", "allItems", "translations"
        ]

        results = {
            "attempted": len(update_rows),
            "updated": 0,
            "failed": 0,
            "details": []
        }

        for row in update_rows:
            ou_id = row.get("id")
            new_code = row.get("new_code")
            current_code = row.get("current_code")

            try:
                # Fetch current OU so we preserve existing values and change only code.
                current_response = self._dhis_request(
                    method="GET",
                    base_url=base_url,
                    username=username,
                    password=password,
                    endpoint=f"/organisationUnits/{ou_id}",
                    timeout=60
                )
                current_data = current_response.json()

                update_payload = dict(current_data)
                update_payload["code"] = new_code

                # Explicitly preserve coordinates/geometry when available.
                coord_response = self._dhis_request(
                    method="GET",
                    base_url=base_url,
                    username=username,
                    password=password,
                    endpoint=f"/organisationUnits/{ou_id}",
                    params={"fields": "id,coordinates,geometry"},
                    timeout=60
                )
                coord_data = coord_response.json()
                if coord_data.get("coordinates") is not None:
                    update_payload["coordinates"] = coord_data.get("coordinates")
                if coord_data.get("geometry") is not None:
                    update_payload["geometry"] = coord_data.get("geometry")

                for field in readonly_fields:
                    update_payload.pop(field, None)

                self._dhis_request(
                    method="PUT",
                    base_url=base_url,
                    username=username,
                    password=password,
                    endpoint=f"/organisationUnits/{ou_id}",
                    json_data=update_payload,
                    timeout=60
                )

                results["updated"] += 1
                results["details"].append({
                    "id": ou_id,
                    "from": current_code,
                    "to": new_code,
                    "status": "updated"
                })
            except Exception as e:
                results["failed"] += 1
                results["details"].append({
                    "id": ou_id,
                    "from": current_code,
                    "to": new_code,
                    "status": "failed",
                    "error": str(e)
                })

        status = "UPDATED" if results["failed"] == 0 else "PARTIAL"
        message = f"Updated {results['updated']} of {results['attempted']} organisation units"

        return {
            "status": status,
            "message": message,
            "response": results,
            "mode": "put_merge"
        }

def main():
    st.set_page_config(
        page_title="Nigeria School Code Generator",
        page_icon="🏫",
        layout="wide"
    )
    
    st.title("🏫 Nigeria School Code Generator")
    st.markdown("Generate unique school codes for all Nigerian states and LGAs")
    
    # Initialize generator
    generator = SchoolCodeGenerator()
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.radio(
        "Choose Mode",
        ["Generate Codes", "Process School List", "New School Intake", "DHIS2 Level-5 Update", "State Information", "About"],
        index=2
    )
    
    if app_mode == "Generate Codes":
        generate_codes_ui(generator)
    elif app_mode == "Process School List":
        process_school_list_ui(generator)
    elif app_mode == "New School Intake":
        new_school_intake_ui(generator)
    elif app_mode == "DHIS2 Level-5 Update":
        dhis2_level5_update_ui(generator)
    elif app_mode == "State Information":
        state_info_ui(generator)
    else:
        about_ui()

def dhis2_level5_update_ui(generator):
    st.header("DHIS2: Level-5 OU Code Update")
    st.markdown("Fetch level-5 organisation units under a selected level-2 OU and generate SSLLXXXXXX school codes.")

    if "dhis2_level2_ous" not in st.session_state:
        st.session_state["dhis2_level2_ous"] = []
    if "dhis2_level5_ous" not in st.session_state:
        st.session_state["dhis2_level5_ous"] = []
    if "dhis2_code_preview" not in st.session_state:
        st.session_state["dhis2_code_preview"] = []

    col1, col2 = st.columns(2)
    with col1:
        base_url = st.text_input("DHIS2 Base URL", value="https://asc.education.gov.ng/dhis")
        username = st.text_input("Username")
    with col2:
        password = st.text_input("Password", type="password")
        st.caption("Format: LGA code from Level-3 (4 digits) + XXXXXX school serial (6 digits) = 10-digit school code. Existing valid codes are preserved.")

    update_mode = st.radio(
        "Update Mode",
        options=["put_merge", "metadata_bulk"],
        format_func=lambda v: "Safe per-OU PUT (preserves full OU payload incl. coordinates)" if v == "put_merge" else "Fast bulk /metadata (best for very large batches)",
        index=0,
        horizontal=False
    )

    if st.button("1) Load Level-2 OUs"):
        if not base_url or not username or not password:
            st.error("Please provide base URL, username, and password.")
        else:
            try:
                with st.spinner("Fetching level-2 organisation units..."):
                    level2_ous = generator.fetch_level2_ous(base_url, username, password)
                st.session_state["dhis2_level2_ous"] = level2_ous
                st.session_state["dhis2_level5_ous"] = []
                st.session_state["dhis2_code_preview"] = []
                st.success(f"Loaded {len(level2_ous)} level-2 OUs")
            except Exception as e:
                st.error(f"Failed to load level-2 OUs: {e}")

    level2_ous = st.session_state.get("dhis2_level2_ous", [])
    if level2_ous:
        option_map = {
            f"{ou.get('name', '')} ({ou.get('id', '')}) | code: {ou.get('code', '')}": ou
            for ou in level2_ous
        }
        selected_label = st.selectbox("Select Level-2 OU", options=list(option_map.keys()))
        selected_level2 = option_map[selected_label]

        if st.button("2) Fetch Level-5 OUs under selected Level-2"):
            try:
                status_placeholder = st.empty()
                status_placeholder.info("Fetching level-5 organisation units — page 1...")

                def _on_progress(fetched, total_pages, page):
                    if total_pages and total_pages > 1:
                        status_placeholder.info(
                            f"Fetching level-5 OUs — page {page} of {total_pages} ({fetched} loaded so far)..."
                        )

                level5_ous = generator.fetch_level5_under_level2(
                    base_url=base_url,
                    username=username,
                    password=password,
                    level2_id=selected_level2.get("id"),
                    on_progress=_on_progress
                )
                status_placeholder.empty()
                st.session_state["dhis2_level5_ous"] = level5_ous
                st.session_state["dhis2_code_preview"] = []
                st.success(f"Loaded {len(level5_ous)} level-5 OUs under {selected_level2.get('name')}")
            except Exception as e:
                st.error(f"Failed to fetch level-5 OUs: {e}")

    level5_ous = st.session_state.get("dhis2_level5_ous", [])
    if level5_ous:
        st.info(f"Level-5 OUs fetched: {len(level5_ous)}")

        if st.button("3) Generate 10-digit code preview"):
            preview = generator.generate_level5_code_updates(level5_ous)
            st.session_state["dhis2_code_preview"] = preview

        preview = st.session_state.get("dhis2_code_preview", [])
        if preview:
            preview_df = pd.DataFrame(preview)
            st.subheader("Preview")

            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Total Level-5 OUs", len(preview_df))
            with col_b:
                st.metric("Will Update", int((preview_df["action"] == "update").sum()))
            with col_c:
                st.metric("Skipped/Kept", int((preview_df["action"] != "update").sum()))

            st.dataframe(
                preview_df[["lga_name", "lga_code", "name", "id", "parent_uid", "old_code", "current_code", "new_code", "action", "reason"]],
                use_container_width=True
            )

            confirm = st.checkbox("I confirm I want to apply these updates to DHIS2")
            if st.button("4) Apply updates to DHIS2", type="primary"):
                if not confirm:
                    st.error("Please confirm before applying updates.")
                else:
                    try:
                        with st.spinner("Applying updates to DHIS2..."):
                            result = generator.apply_level5_code_updates(
                                base_url=base_url,
                                username=username,
                                password=password,
                                updates=preview,
                                update_mode=update_mode
                            )

                        if result.get("status") == "NO_UPDATES":
                            st.info(result.get("message"))
                        else:
                            st.success(result.get("message"))
                            st.json(result.get("response"))
                    except Exception as e:
                        st.error(f"Failed to apply updates: {e}")

def generate_codes_ui(generator):
    st.header("Generate School Codes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        state_name = st.selectbox(
            "Select State",
            sorted([state.title() for state in generator.state_codes.keys()])
        )
        
        # Get LGAs for selected state
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
            value=5,
            help="Number of school codes to generate for each selected LGA"
        )
        
        st.subheader("Existing Codes (Optional)")
        existing_file = st.file_uploader(
            "Upload existing school codes file",
            type=['csv', 'xlsx', 'xls', 'txt'],
            help="Upload a file with existing codes to avoid duplicates"
        )
    
    if st.button("Generate School Codes", type="primary"):
        if not state_name:
            st.error("Please select a state")
            return
        
        if not selected_lgas:
            st.error("Please select at least one LGA")
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

def process_school_list_ui(generator):
    st.header("📋 Process School List")
    
    # File upload
    school_list_file = st.file_uploader(
        "Upload School List (Excel/CSV)",
        type=['csv', 'xlsx', 'xls']
    )
    
    existing_codes_file = st.file_uploader(
        "Upload Existing School Codes (Optional)",
        type=['csv', 'xlsx', 'xls', 'txt']
    )
    
    if st.button("Generate School Codes", type="primary"):
        if not school_list_file:
            st.error("Please upload a school list file")
            return
        
        with st.spinner("Processing school list and generating codes..."):
            result_df, original_stats, processing_stats, duplicates = generator.process_school_list_file(
                uploaded_file=school_list_file,
                existing_codes_file=existing_codes_file
            )
        
        if result_df is not None:
            display_school_list_results(
                result_df, 
                school_list_file, 
                original_stats, 
                processing_stats, 
                duplicates
            )

def new_school_intake_ui(generator):
    st.header("🆕 New School Intake")
    st.markdown(
        "Upload your new school list. The app will match each school to the right State/LGA/Ward using "
        "the reference file, check existing school codes in DNEMIS, and then generate the next available codes "
        "for each LGA automatically."
    )

    reference_path = generator._get_ou_reference_path()
    ref_file_available = os.path.exists(reference_path)
    if ref_file_available:
        st.caption(f"Using OU reference file: {os.path.basename(reference_path)}")
    else:
        if 'ou_reference_file_bytes' not in st.session_state:
            try:
                remote_buffer, remote_source = generator.fetch_ou_reference_from_remote()
                if remote_buffer is not None:
                    st.session_state['ou_reference_file_bytes'] = remote_buffer.getvalue()
                    st.session_state['ou_reference_file_name'] = getattr(remote_buffer, 'name', generator.ou_reference_alias_filename)
                    st.session_state['ou_reference_source'] = remote_source
            except Exception as exc:
                st.session_state['ou_reference_remote_error'] = str(exc)

        if 'ou_reference_file_bytes' in st.session_state:
            source_label = st.session_state.get('ou_reference_source', 'remote source')
            st.caption(f"Using OU reference file from secure source: {source_label}")
        else:
            st.error("OU reference file is not available on this server.")
            st.info(
                "Place the renamed reference CSV at school_app/etc/ou_index_2026.csv, "
                "or set OU_REFERENCE_URL in Streamlit secrets/environment for automatic secure download."
            )
            if 'ou_reference_remote_error' in st.session_state:
                st.caption(f"Remote fetch error: {st.session_state['ou_reference_remote_error']}")
            return

    col1, col2 = st.columns(2)
    with col1:
        intake_file = st.file_uploader(
            "Upload New Schools List",
            type=['csv', 'xlsx', 'xls'],
            key='new_school_intake_file'
        )
        base_url = st.text_input("DHIS2 Base URL", value="https://asc.education.gov.ng/dhis", key='intake_base_url')
    with col2:
        username = st.text_input("Username", key='intake_username')
        password = st.text_input("Password", type='password', key='intake_password')

    st.info(
        "Recommended intake columns: school_name, school_level, old_schoolcode, state, lga, ward, lgacode, openingDate. "
        "Required: school_name, plus either lgacode or a state/LGA combination. "
        "Optional: old_schoolcode, openingDate."
    )
    st.caption("Valid school_level values for name prefixing: JSS, SSS, PRY, TVET, PVT, IQS.")
    st.caption("If old_schoolcode is provided, the school_name suffix uses old_schoolcode; otherwise it uses the newly generated school_code. old_schoolcode must not be a 10-digit number.")

    intake_template_df = pd.DataFrame([
        {
            'school_name': 'Government Junior Secondary School Ajim',
            'school_level': 'JSS',
            'old_schoolcode': '1020120041',
            'state': 'Abia',
            'lga': 'Umuahia South',
            'ward': 'Ahiaukwu',
            'lgacode': '',
            'openingDate': '2024-01-01'
        }
    ])
    st.download_button(
        label="📥 Download Intake Template (CSV)",
        data=intake_template_df.to_csv(index=False),
        file_name='new_school_intake_template.csv',
        mime='text/csv',
        use_container_width=False
    )
    st.caption("If openingDate is blank or invalid, the app defaults to 2024-01-01. If ward is blank, the app tries to use Unknown Ward in the resolved LGA.")

    if st.button("Resolve Schools and Generate Next Codes", type='primary'):
        if not intake_file:
            st.error("Please upload a new school intake file.")
            return
        if not base_url or not username or not password:
            st.error("Please provide DHIS2 base URL, username, and password.")
            return

        with st.spinner("Resolving schools and fetching current DHIS2 codes..."):
            ref_kwarg = {}
            if not ref_file_available:
                if 'ou_reference_file_bytes' in st.session_state:
                    buf = BytesIO(st.session_state['ou_reference_file_bytes'])
                    buf.name = st.session_state.get('ou_reference_file_name', generator.ou_reference_alias_filename)
                    ref_kwarg['reference_file'] = buf
                else:
                    st.error("OU reference file is not available. Configure local file or OU_REFERENCE_URL.")
                    return
            else:
                ref_kwarg['reference_path'] = reference_path
            result_df, original_stats, processing_stats = generator.process_new_school_intake(
                uploaded_file=intake_file,
                base_url=base_url,
                username=username,
                password=password,
                **ref_kwarg
            )

        if result_df is not None:
            st.session_state['new_intake_result_df'] = result_df
            st.session_state['new_intake_original_stats'] = original_stats
            st.session_state['new_intake_processing_stats'] = processing_stats
            st.session_state['new_intake_original_name'] = intake_file.name

    if 'new_intake_result_df' in st.session_state:
        display_new_school_intake_results(
            generator=generator,
            result_df=st.session_state['new_intake_result_df'],
            original_name=st.session_state.get('new_intake_original_name', 'intake_upload.csv'),
            original_stats=st.session_state.get('new_intake_original_stats', {}),
            processing_stats=st.session_state.get('new_intake_processing_stats', {}),
            base_url=base_url,
            username=username,
            password=password
        )

def display_new_school_intake_results(generator, result_df, original_name, original_stats, processing_stats, base_url, username, password):
    st.success(f"✅ Intake processed for {len(result_df)} schools")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview",
        "🧭 Resolution",
        "🔢 Serial Allocation",
        "📥 Download",
        "🚀 Publish"
    ])

    with tab1:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Input Rows", processing_stats.get('input_rows', 0))
        with col2:
            st.metric("Resolved Rows", processing_stats.get('resolved_rows', 0))
        with col3:
            st.metric("Warnings", processing_stats.get('warning_rows', 0))
        with col4:
            st.metric("Unresolved", processing_stats.get('unresolved_rows', 0))

        col5, col6, col7 = st.columns(3)
        with col5:
            st.metric("Affected LGAs", processing_stats.get('affected_lgas', 0))
        with col6:
            st.metric("States Fetched", processing_stats.get('affected_states', 0))
        with col7:
            st.metric("Level-5 OUs Fetched", processing_stats.get('level5_ous_fetched', 0))

        col8, col9 = st.columns(2)
        with col8:
            st.metric("OpeningDate Defaulted", processing_stats.get('openingdate_defaulted_count', 0))
        with col9:
            st.metric("Ready To Publish", processing_stats.get('ready_to_post_count', 0))

        col10, col11 = st.columns(2)
        with col10:
            st.metric("school_level Missing", processing_stats.get('school_level_missing_count', 0))
        with col11:
            st.metric("school_level Invalid", processing_stats.get('school_level_invalid_count', 0))

        parent_match_counts = processing_stats.get('parent_match_counts', {})
        col12, col13, col14, col15 = st.columns(4)
        with col12:
            st.metric("Parent Exact", int(parent_match_counts.get('exact_ward', 0)))
        with col13:
            st.metric("Parent Fuzzy", int(parent_match_counts.get('fuzzy_ward', 0)))
        with col14:
            st.metric("LGA Center", int(parent_match_counts.get('lga_center', 0)))
        with col15:
            st.metric("Unknown Fallback", int(parent_match_counts.get('unknown_fallback', 0)))

        if processing_stats.get('fuzzy_low_confidence_count', 0) > 0:
            st.warning(
                f"{processing_stats.get('fuzzy_low_confidence_count', 0)} row(s) were fuzzy matched with score below "
                f"{int(generator.parent_match_confident_threshold)}. Review before publishing."
            )

        st.caption(f"old_schoolcode used in name suffix for {processing_stats.get('old_schoolcode_used_count', 0)} row(s).")
        if processing_stats.get('old_schoolcode_invalid_ten_digit_count', 0) > 0:
            st.warning(
                f"{processing_stats.get('old_schoolcode_invalid_ten_digit_count', 0)} row(s) have 10-digit old_schoolcode values. "
                "Those values were ignored for name suffix, and generated school_code was used instead."
            )

        if processing_stats.get('duplicate_count', 0) > 0:
            st.error(f"Detected {processing_stats['duplicate_count']} duplicate school codes against fetched DHIS2 data.")
        else:
            st.success("Generated codes are clear against the fetched DHIS2 codes.")

        preview_columns = [
            'school_code', 'school_ou_uid', 'school_level', 'school_level_normalized', 'name_format_valid',
            'old_schoolcode', 'name_suffix_code_used', 'lgacode', 'reference_lga', 'school_name', 'state', 'lga',
            'ward', 'openingdate', 'parentuid_for_create', 'parent_match_type', 'parent_match_score', 'match_status', 'match_notes'
        ]
        available_preview_columns = [column for column in preview_columns if column in result_df.columns]
        st.dataframe(result_df[available_preview_columns].head(20), use_container_width=True)

        if original_stats:
            st.caption(
                f"Uploaded file stats: {original_stats.get('total_schools', len(result_df))} rows, "
                f"{original_stats.get('total_columns', 0)} columns."
            )

    with tab2:
        unresolved_preview = processing_stats.get('unresolved_preview', [])
        if unresolved_preview:
            st.warning("Some rows could not be resolved against the OU reference file.")
            st.dataframe(pd.DataFrame(unresolved_preview), use_container_width=True)
        else:
            st.success("All rows were resolved against the OU reference file.")

        no_parent_df = result_df[result_df['parentuid_for_create'].astype(str).str.strip() == '']
        if not no_parent_df.empty:
            st.warning("Some rows do not have a parent UID for create and cannot be published yet.")
            no_parent_columns = [
                column for column in ['school_name', 'state', 'lga', 'ward', 'parent_match_type', 'parent_match_score', 'match_notes']
                if column in no_parent_df.columns
            ]
            st.dataframe(
                no_parent_df[no_parent_columns].head(20),
                use_container_width=True
            )

        low_confidence_df = result_df[
            result_df['parent_match_type'].astype(str).eq('fuzzy_ward') &
            (pd.to_numeric(result_df['parent_match_score'], errors='coerce').fillna(0) < float(generator.parent_match_confident_threshold))
        ] if ('parent_match_type' in result_df.columns and 'parent_match_score' in result_df.columns) else pd.DataFrame()
        if not low_confidence_df.empty:
            st.warning("Some rows have low-confidence fuzzy parent matches. Review before publishing.")
            low_confidence_columns = [
                column for column in [
                    'school_name', 'state', 'lga', 'ward', 'reference_ward',
                    'parent_match_type', 'parent_match_score', 'parentuid_for_create', 'match_notes'
                ] if column in low_confidence_df.columns
            ]
            st.dataframe(low_confidence_df[low_confidence_columns].head(20), use_container_width=True)

        invalid_level_df = result_df[~result_df['name_format_valid'].astype(bool)] if 'name_format_valid' in result_df.columns else pd.DataFrame()
        if not invalid_level_df.empty:
            st.warning("Some rows have invalid/missing school_level prefix format and are blocked from publish.")
            level_columns = [
                column for column in ['school_name', 'school_level', 'school_level_normalized', 'school_code', 'state', 'lga']
                if column in invalid_level_df.columns
            ]
            st.dataframe(invalid_level_df[level_columns].head(20), use_container_width=True)

        invalid_existing_codes = processing_stats.get('invalid_existing_codes', [])
        if invalid_existing_codes:
            st.info(
                f"Fetched DHIS2 data included {processing_stats.get('invalid_existing_codes_count', 0)} "
                "existing Level-5 codes that were ignored because they were not valid 10-digit values."
            )
            st.dataframe(pd.DataFrame(invalid_existing_codes).head(20), use_container_width=True)

    with tab3:
        lga_stats = processing_stats.get('lga_stats', [])
        if lga_stats:
            st.dataframe(pd.DataFrame(lga_stats), use_container_width=True)
        else:
            st.info("No LGA allocations were generated.")

    with tab4:
        csv_data = result_df.to_csv(index=False)
        file_stub = str(original_name).split('.')[0]
        st.download_button(
            label="📄 Download Intake Results as CSV",
            data=csv_data,
            file_name=f"new_school_intake_{file_stub}.csv",
            mime='text/csv',
            type='primary',
            use_container_width=True
        )

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            result_df.to_excel(writer, index=False, sheet_name='Intake Results')
            pd.DataFrame(processing_stats.get('lga_stats', [])).to_excel(writer, index=False, sheet_name='LGA Allocation')
            pd.DataFrame(processing_stats.get('unresolved_preview', [])).to_excel(writer, index=False, sheet_name='Unresolved')

        st.download_button(
            label="📊 Download Intake Results as Excel",
            data=output.getvalue(),
            file_name=f"new_school_intake_{file_stub}.xlsx",
            mime='application/vnd.ms-excel',
            use_container_width=True
        )

        # Slim export for downstream tasks like OU grouping and dataset assignment.
        post_actions_df = result_df.copy()
        post_actions_df['state_name'] = post_actions_df['reference_state'].where(
            post_actions_df['reference_state'].astype(str).str.strip() != '',
            post_actions_df['state'].astype(str)
        )
        post_actions_columns = [
            'school_name', 'school_code', 'school_ou_uid', 'state_name',
            'lgacode', 'lgauid', 'warduid', 'parentuid_for_create',
            'reference_lga', 'reference_ward', 'openingdate'
        ]
        available_post_actions_columns = [
            column for column in post_actions_columns if column in post_actions_df.columns
        ]
        post_actions_df = post_actions_df[available_post_actions_columns]

        st.download_button(
            label="🧩 Download Post-Actions File (CSV)",
            data=post_actions_df.to_csv(index=False),
            file_name=f"post_actions_{file_stub}.csv",
            mime='text/csv',
            use_container_width=True
        )

    with tab5:
        ready_df = result_df[result_df['can_post'].astype(bool)] if 'can_post' in result_df.columns else pd.DataFrame()
        st.metric("Rows Ready To Publish", len(ready_df))
        if ready_df.empty:
            st.info("No rows are ready to publish. Resolve all required fields first.")
            return

        # Count rows that are new creates (no existing UID)
        create_df = ready_df[ready_df['school_ou_uid'].apply(lambda v: not str(v or '').strip())] if 'school_ou_uid' in ready_df.columns else ready_df
        # All candidate create rows in current result set (including rows blocked from ready_df)
        if 'school_code' in result_df.columns and 'school_ou_uid' in result_df.columns:
            create_scope_df = result_df[
                result_df['school_code'].astype(str).str.match(r'^\d{10}$') &
                result_df['school_ou_uid'].astype(str).str.strip().eq('')
            ].copy()
        else:
            create_scope_df = create_df.copy()

        if 'name_format_valid' in create_scope_df.columns:
            invalid_level_create_df = create_scope_df[~create_scope_df['name_format_valid'].astype(bool)].copy()
        else:
            invalid_level_create_df = pd.DataFrame()

        if 'parent_match_type' in create_scope_df.columns and 'parent_match_score' in create_scope_df.columns:
            low_confidence_create_df = create_scope_df[
                create_scope_df['parent_match_type'].astype(str).eq('fuzzy_ward') &
                (pd.to_numeric(create_scope_df['parent_match_score'], errors='coerce').fillna(0) < float(generator.parent_match_confident_threshold))
            ].copy()
        else:
            low_confidence_create_df = pd.DataFrame()

        create_codes_signature = '|'.join(sorted(create_scope_df['school_code'].astype(str).tolist())) if 'school_code' in create_scope_df.columns else ''
        update_count_preview = len(ready_df) - len(create_df)
        st.caption(f"{len(create_df)} new create(s), {update_count_preview} update(s) in ready set.")

        ready_preview_columns = [
            column for column in [
                'school_name', 'school_level', 'old_schoolcode', 'name_suffix_code_used', 'school_level_normalized', 'school_code',
                'school_ou_uid', 'openingdate', 'parentuid_for_create', 'parent_match_type', 'parent_match_score', 'reference_lga'
            ] if column in ready_df.columns
        ]
        st.dataframe(
            ready_df[ready_preview_columns].head(20),
            use_container_width=True
        )

        # ── Duplicate check ──────────────────────────────────────────────────
        st.subheader("Step 1 — Check for Duplicate Schools on DNEMIS")
        st.caption("Queries DNEMIS for existing Level-5 OUs under the same LGA as each new-create row and flags name matches.")

        col_check, col_clear = st.columns([2, 1])
        with col_check:
            run_dup_check = st.button("🔍 Check for Duplicates on DNEMIS", key='new_intake_dup_check_button')
        with col_clear:
            if st.button("Clear duplicate check results", key='new_intake_dup_clear_button'):
                st.session_state.pop('new_intake_dup_results', None)
                st.session_state.pop('new_intake_dup_check_signature', None)
                st.rerun()

        if run_dup_check:
            if not base_url or not username or not password:
                st.error("Please provide DHIS2 credentials before checking.")
            else:
                with st.spinner("Checking DNEMIS for duplicate school names in each LGA..."):
                    try:
                        dup_matches = generator.check_duplicate_names_on_dhis2(
                            base_url=base_url,
                            username=username,
                            password=password,
                            intake_df=ready_df
                        )
                        st.session_state['new_intake_dup_results'] = dup_matches
                        st.session_state['new_intake_dup_check_signature'] = create_codes_signature
                    except Exception as e:
                        st.error(f"Duplicate check failed: {e}")

        dup_results = st.session_state.get('new_intake_dup_results')
        dup_check_signature = st.session_state.get('new_intake_dup_check_signature', '')
        duplicate_check_run_for_current = (dup_results is not None) and (dup_check_signature == create_codes_signature)
        duplicates_acknowledged = True  # default: allow publish when check not yet run

        if dup_results is not None:
            if len(dup_results) == 0:
                st.success("No duplicate school names found in DNEMIS for the create rows.")
            else:
                st.warning(f"{len(dup_results)} potential duplicate(s) found. Review before publishing.")
                dup_df = pd.DataFrame(dup_results)
                st.dataframe(dup_df, use_container_width=True)

                # Separate exact vs partial
                exact_count = sum(1 for d in dup_results if d.get('match_type') == 'EXACT')
                partial_count = len(dup_results) - exact_count
                if exact_count:
                    st.error(f"{exact_count} EXACT name match(es) — these schools likely already exist.")
                if partial_count:
                    st.warning(f"{partial_count} PARTIAL name match(es) — review carefully.")

                duplicates_acknowledged = st.checkbox(
                    "I have reviewed the duplicate results and want to proceed anyway",
                    key='new_intake_dup_acknowledge'
                )

        # ── Publish ──────────────────────────────────────────────────────────
        st.subheader("Step 2 — Publish to DNEMIS")
        strict_publish_gate = st.checkbox(
            "Strict gate: block publish unless duplicate-check was run, school_level is valid, and fuzzy parent matches are high confidence",
            value=True,
            key='new_intake_strict_publish_gate'
        )

        if strict_publish_gate:
            if len(create_scope_df) > 0 and not duplicate_check_run_for_current:
                st.info("Strict gate active: run duplicate-check for the current create rows before publishing.")

            if len(invalid_level_create_df) > 0:
                st.error(
                    f"Strict gate active: {len(invalid_level_create_df)} create row(s) have missing/invalid school_level prefix and must be fixed."
                )
                invalid_preview_columns = [
                    column for column in ['school_name', 'school_level', 'school_level_normalized', 'school_code', 'state', 'lga']
                    if column in invalid_level_create_df.columns
                ]
                st.dataframe(invalid_level_create_df[invalid_preview_columns].head(20), use_container_width=True)

            if len(low_confidence_create_df) > 0:
                st.warning(
                    f"Strict gate active: {len(low_confidence_create_df)} create row(s) have fuzzy parent-match score below "
                    f"{int(generator.parent_match_confident_threshold)}."
                )
                confidence_preview_columns = [
                    column for column in [
                        'school_name', 'state', 'lga', 'ward', 'reference_ward',
                        'parent_match_type', 'parent_match_score', 'parentuid_for_create', 'match_notes'
                    ] if column in low_confidence_create_df.columns
                ]
                st.dataframe(low_confidence_create_df[confidence_preview_columns].head(20), use_container_width=True)

        dry_run = st.checkbox("Dry run only (recommended first)", value=True, key='new_intake_publish_dry_run')
        confirm_publish = st.checkbox("I confirm I want to create or update these schools on DNEMIS", key='new_intake_publish_confirm')

        publish_disabled = not duplicates_acknowledged
        if strict_publish_gate:
            if len(create_scope_df) > 0 and not duplicate_check_run_for_current:
                publish_disabled = True
            if len(invalid_level_create_df) > 0:
                publish_disabled = True
            if len(low_confidence_create_df) > 0:
                publish_disabled = True

        if publish_disabled:
            st.info("Publish is blocked by quality checks. Resolve the messages above.")

        if st.button("Post New Schools to DNEMIS", type='primary', key='new_intake_publish_button', disabled=publish_disabled):
            if not base_url or not username or not password:
                st.error("Please provide DHIS2 credentials before publishing.")
                return
            if not confirm_publish:
                st.error("Please confirm before publishing.")
                return

            try:
                with st.spinner("Posting new schools to DNEMIS..."):
                    publish_result = generator.post_new_schools_to_dhis2(
                        base_url=base_url,
                        username=username,
                        password=password,
                        intake_df=ready_df,
                        dry_run=dry_run
                    )
                # Persist result so it survives st.rerun()
                st.session_state['new_intake_publish_result'] = publish_result

                def _normalize_school_code(code_value):
                    code_text = str(code_value or '').strip()
                    digits_only = re.sub(r'\D', '', code_text)
                    if len(digits_only) >= 10:
                        return digits_only[-10:]
                    if digits_only:
                        return digits_only.zfill(10)
                    return ''

                uid_by_code = (publish_result.get('response', {}) or {}).get('uid_by_code', {})
                if isinstance(uid_by_code, dict) and uid_by_code:
                    updated_df = result_df.copy()
                    if 'school_ou_uid' not in updated_df.columns:
                        updated_df['school_ou_uid'] = ''

                    normalized_uid_map = {
                        _normalize_school_code(school_code): str(ou_uid or '').strip()
                        for school_code, ou_uid in uid_by_code.items()
                        if _normalize_school_code(school_code)
                    }

                    normalized_codes = updated_df['school_code'].apply(_normalize_school_code)
                    populated_count = 0
                    for idx, normalized_code in normalized_codes.items():
                        if not normalized_code:
                            continue
                        ou_uid = normalized_uid_map.get(normalized_code, '')
                        if ou_uid:
                            updated_df.at[idx, 'school_ou_uid'] = ou_uid
                            populated_count += 1

                    st.session_state['new_intake_result_df'] = updated_df
                    st.session_state['new_intake_publish_result']['_populated_count'] = populated_count

                st.rerun()
            except Exception as e:
                st.error(f"Failed to publish new schools: {e}")

        # Render publish result persistently (read from session state so it survives st.rerun())
        if 'new_intake_publish_result' in st.session_state:
            pr = st.session_state['new_intake_publish_result']
            status = pr.get('status', '')
            if status in ['FAILED', 'FAILED_LOOKUP', 'INVALID_INPUT']:
                st.error(pr.get('message', 'Publish failed'))
            elif status in ['DRY_RUN', 'POSTED']:
                st.success(pr.get('message', 'Done'))
            elif status == 'POSTED_WITH_WARNING':
                st.warning(pr.get('message', 'Published with warnings'))
            else:
                st.info(pr.get('message', 'Done'))
            populated_count = pr.get('_populated_count')
            if populated_count is not None:
                st.caption(f"school_ou_uid populated for {populated_count} row(s) from DNEMIS response.")
            st.json(pr.get('response', {}))

def display_school_list_results(result_df, original_file, original_stats, processing_stats, duplicates):
    st.success(f"✅ Successfully processed {len(result_df)} schools!")
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", 
        "📈 Uploaded File Stats", 
        "⚙️ Processing Stats", 
        "🔍 Duplicate Check", 
        "📥 Download"
    ])
    
    with tab1:
        # Overview statistics
        st.subheader("📊 Overview Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_schools = len(result_df)
            st.metric("Total Schools", total_schools)
        
        with col2:
            generated_codes = result_df['school_code'].apply(lambda x: str(x).strip() != '').sum()
            st.metric("Generated Codes", generated_codes)
        
        with col3:
            unique_lgas = result_df['lgacode'].nunique()
            st.metric("Unique LGAs", unique_lgas)
        
        with col4:
            unique_states = result_df['state'].nunique()
            st.metric("States", unique_states)
        
        # Check if school codes were generated
        if generated_codes == 0:
            st.error("❌ CRITICAL ISSUE: No school codes were generated!")
            st.info("Please check the debug information above to identify the issue.")
        elif generated_codes < total_schools:
            st.warning(f"⚠️ {total_schools - generated_codes} schools did not receive codes!")
        else:
            st.success(f"✅ Successfully generated codes for all {generated_codes} schools")
        
        # Preview of results
        st.subheader("📋 Preview of Generated Codes")
        
        # Show first 10 rows with key columns
        preview_cols = ['school_code', 'lgacode', 'state', 'lga', 'school_name']
        if 'ward' in result_df.columns:
            preview_cols.append('ward')
        if 'category' in result_df.columns:
            preview_cols.append('category')
        
        preview_df = result_df[preview_cols].head(10)
        st.dataframe(preview_df, use_container_width=True)
    
    with tab2:
        # Uploaded file statistics
        st.subheader("📈 Uploaded File Statistics")
        
        if original_stats:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Schools", original_stats.get('total_schools', 0))
                st.metric("Total Columns", original_stats.get('total_columns', 0))
            
            with col2:
                if 'unique_lgas' in original_stats:
                    st.metric("Unique LGAs", original_stats['unique_lgas'])
                if 'unique_states' in original_stats:
                    st.metric("Unique States", original_stats['unique_states'])
            
            with col3:
                st.metric("Missing Values", original_stats.get('missing_values_total', 0))
                if 'existing_codes_count' in original_stats:
                    st.metric("Existing Codes", original_stats['existing_codes_count'])
            
            # Show column information
            st.subheader("📋 File Columns")
            st.write(f"Total columns: {len(original_stats.get('columns', []))}")
            st.write(f"Columns: {', '.join(original_stats.get('columns', []))}")
            
            # Show top LGAs
            if 'lga_distribution' in original_stats and original_stats['lga_distribution']:
                st.subheader("🏙️ Top LGAs in Uploaded File")
                lga_df = pd.DataFrame(list(original_stats['lga_distribution'].items()), 
                                    columns=['LGA Code', 'Number of Schools'])
                st.dataframe(lga_df, use_container_width=True)
        
        else:
            st.info("No statistics available for the uploaded file.")
    
    with tab3:
        # Processing statistics
        st.subheader("⚙️ Processing Statistics")
        
        if processing_stats:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Codes Generated", processing_stats.get('codes_generated', 0))
                st.metric("Duplicates Avoided", processing_stats.get('total_duplicates_avoided', 0))
            
            with col2:
                st.metric("LGAs Processed", len(processing_stats.get('lga_stats', [])))
            
            with col3:
                if duplicates:
                    st.metric("Final Duplicates Found", len(duplicates))
                else:
                    st.metric("Final Duplicates Found", 0)
            
            # Show LGA processing details
            if processing_stats.get('lga_stats'):
                st.subheader("🏙️ LGA Processing Details")
                lga_stats_df = pd.DataFrame(processing_stats['lga_stats'])
                st.dataframe(lga_stats_df[['lgacode', 'num_schools', 'start_serial', 'end_serial', 'existing_serials_count']], 
                           use_container_width=True)
            
            # Show serial number ranges
            if processing_stats.get('max_serial_per_lga'):
                st.subheader("🔢 Serial Number Ranges per LGA")
                serial_df = pd.DataFrame(list(processing_stats['max_serial_per_lga'].items()), 
                                       columns=['LGA Code', 'Max Serial'])
                st.dataframe(serial_df.sort_values('Max Serial', ascending=False), use_container_width=True)
    
    with tab4:
        # Duplicate check results
        st.subheader("🔍 Duplicate Code Analysis")
        
        if duplicates:
            st.error(f"❌ {len(duplicates)} DUPLICATE CODES FOUND!")
            st.write("These generated codes already exist in the uploaded existing codes file:")
            
            # Show duplicates in a table
            dup_df = result_df[result_df['school_code'].isin(duplicates)]
            if not dup_df.empty:
                st.dataframe(dup_df[['school_code', 'lgacode', 'state', 'lga', 'school_name']].head(10))
                
                if len(duplicates) > 10:
                    st.write(f"... and {len(duplicates) - 10} more duplicates")
            
            # Show detailed duplicate information
            if processing_stats and 'duplicate_details' in processing_stats:
                st.subheader("📋 Duplicate Details")
                dup_details_df = pd.DataFrame(processing_stats['duplicate_details'])
                st.dataframe(dup_details_df, use_container_width=True)
        else:
            st.success("✅ No duplicate codes found!")
            
            if processing_stats and processing_stats.get('total_duplicates_avoided', 0) > 0:
                st.info(f"⚠️ Note: {processing_stats['total_duplicates_avoided']} potential duplicates were avoided during processing by skipping existing serial numbers.")
    
    with tab5:
        # Download options
        st.subheader("📥 Download Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV Download
            csv_data = result_df.to_csv(index=False)
            original_name = original_file.name.split('.')[0]
            st.download_button(
                label="📄 Download as CSV",
                data=csv_data,
                file_name=f"school_codes_{original_name}.csv",
                mime="text/csv",
                type="primary",
                use_container_width=True
            )
        
        with col2:
            # Excel Download
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                result_df.to_excel(writer, index=False, sheet_name='School Codes')
                
                # Add summary sheet
                summary_df = result_df.groupby(['state', 'lga', 'lgacode']).size().reset_index(name='Number of Schools')
                summary_df.to_excel(writer, index=False, sheet_name='Summary')
            
            excel_data = output.getvalue()
            
            st.download_button(
                label="📊 Download as Excel",
                data=excel_data,
                file_name=f"school_codes_{original_name}.xlsx",
                mime="application/vnd.ms-excel",
                type="primary",
                use_container_width=True
            )
        
        # Debug information
        with st.expander("🔍 Debug Information"):
            st.write("**DataFrame Info:**")
            st.write(f"Shape: {result_df.shape}")
            st.write(f"Columns: {list(result_df.columns)}")
            
            st.write("**Sample of first 5 rows (all columns):**")
            st.dataframe(result_df.head(5), use_container_width=True)
            
            # Check for empty school codes
            empty_codes = result_df['school_code'].apply(lambda x: str(x).strip() == '').sum()
            st.write(f"Empty school codes: {empty_codes}")
            
            if empty_codes > 0:
                st.write("**Rows with empty school codes:**")
                empty_rows = result_df[result_df['school_code'].apply(lambda x: str(x).strip() == '')].head(5)
                st.dataframe(empty_rows)

def display_results(generated_codes, state_name):
    st.success(f"✅ Successfully generated {len(generated_codes)} school codes for {state_name}!")
    
    # Create DataFrame
    df = pd.DataFrame(generated_codes)
    
    # Display summary
    st.subheader("📊 Summary")
    summary = df.groupby(['LGA', 'LGA_Code']).size().reset_index(name='Number of Schools')
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Schools", len(generated_codes))
    with col2:
        st.metric("Number of LGAs", len(summary))
    with col3:
        st.metric("State", state_name)
    
    # Display data
    st.subheader("📋 Generated School Codes")
    st.dataframe(df, use_container_width=True)
    
    # Download options
    st.subheader("📥 Download Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # CSV Download
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name=f"school_codes_{state_name.lower()}.csv",
            mime="text/csv"
        )
    
    with col2:
        # Excel Download
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
        # Text file with codes only
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
                
                st.info("💡 LGA codes follow official government numbering")
            
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
    following the official format: `SSLLXXXXXX`
    
    - **SS**: State code (2 digits)
    - **LL**: LGA code (2 digits) 
    - **XXXXXX**: School serial number (6 digits)
    
    ## 📊 Coverage
    - **36 States** + Federal Capital Territory (FCT)
    - **774 Local Government Areas** nationwide
    - **Official numbering** for all states and LGAs
    
    ## 🚀 Features
    ### 1. Generate Codes
    - Generate codes for specific LGAs or entire states
    - Prevent duplicates by checking existing codes
    - Multiple download formats (CSV, Excel, TXT)
    
    ### 2. Process School List (NEW)
    - Upload Excel/CSV files with school lists
    - **Automatic handling of leading zeros** in lgacode
    - **Case-insensitive column names** (State, state, STATE all work)
    - Assign unique school codes to each school
    - Group by LGA and assign sequential serial numbers
    - Preserve all existing data in the file
    - Download the updated file with generated codes
    - **Comprehensive statistics** on uploaded files
    - **Duplicate detection** and reporting
    
    ## ⚠️ Important Note for School List Processing
    When uploading Excel files with lgacode column:
    - Excel may drop leading zeros from numbers (e.g., `0101` becomes `101`)
    - The tool automatically pads numbers to 4 digits with leading zeros
    - Examples: `101` → `0101`, `201` → `0201`, `2401` → `2401`
    
    ## 📝 Usage
    ### For School List Processing:
    1. Prepare Excel/CSV file with required columns
    2. Ensure 'lgacode' column contains SS+LL format
    3. Upload the file
    4. View comprehensive statistics and duplicate reports
    5. Generate and download results
    
    ### For Bulk Code Generation:
    1. Select a state and LGAs
    2. Specify number of schools per LGA
    3. Upload existing School codes (optional, to avoid duplicates)
    4. Generate and download results
    
    ## 🛠️ Technical Details
    - Built with Streamlit
    - Uses official Nigerian government LGA numbering
    - Supports CSV, Excel, and text file formats
    - Handles Excel's automatic number formatting issues
    - Case-insensitive column name matching
    - Comprehensive duplicate detection and reporting
    """)
    
    st.info("💡 **Tip**: Use the 'State Information' section to view all LGAs and their official codes for any state.")

if __name__ == "__main__":
    main()