# generate_large_dataset_fixed.py
import json
import random
import pandas as pd
from datetime import datetime
import os
from tqdm import tqdm
import itertools


class PakistanAgricultureDatasetGenerator:
    def __init__(self):
        """Initialize with comprehensive Pakistan agriculture knowledge"""

        # ============ CROPS (50+ CROPS) ============
        self.crops = {
            # Cereals
            "wheat": {
                "category": "cereal",
                "season": "Rabi (Oct-Dec)",
                "sowing": "October to December",
                "harvest": "March to May",
                "duration": "110-130 days",
                "soil": "Loamy, clay loam",
                "ph": "6.0-7.5",
                "temp": "20-25°C",
                "water": "4-5 irrigations",
                "varieties": ["Sehar-2006", "Galaxy-2013", "Faisalabad-2008", "Inqalab-91", "Aas-2011", "Punjab-2011",
                              "Millat-2020"],
                "regions": ["Punjab", "Sindh", "KPK", "Balochistan"],
                "districts": ["Sahiwal", "Faisalabad", "Multan", "Bahawalpur", "Rahim Yar Khan", "Ghazi", "Tandojam"],
                "fertilizer": "NPK 120:60:40 kg/ha, Urea 2-3 bags/acre, DAP 1-2 bags/acre",
                "yield": "30-40 maunds/acre",
                "profit": "Rs. 40,000-60,000/acre",
                "diseases": ["Yellow Rust", "Leaf Rust", "Karnal Bunt", "Powdery Mildew"],
                "pests": ["Aphids", "Armyworm", "Termites"]
            },
            "rice": {
                "category": "cereal",
                "season": "Kharif (May-Jul)",
                "sowing": "May to July",
                "harvest": "October to December",
                "duration": "Basmati: 130-150 days, Irri: 100-120 days",
                "soil": "Clay, clay loam",
                "ph": "5.5-7.0",
                "temp": "25-30°C",
                "water": "Standing water 2-5cm, 1200-2000mm",
                "varieties": ["Super Basmati", "Basmati-515", "Basmati-385", "IRRI-6", "KS-282", "NIAB-6"],
                "regions": ["Punjab", "Sindh"],
                "districts": ["Gujranwala", "Sialkot", "Sheikhupura", "Hafizabad", "Badin", "Thatta"],
                "fertilizer": "NPK 100:50:50 kg/ha, Urea 3-4 bags/acre, DAP 1.5 bags/acre, Zinc 10-15 kg/acre",
                "yield": "Basmati: 25-35 maunds/acre, Irri: 50-70 maunds/acre",
                "profit": "Rs. 50,000-80,000/acre",
                "diseases": ["Blast", "Bacterial Blight", "Sheath Blight", "Kernel Smut"],
                "pests": ["Stem Borer", "Brown Plant Hopper", "Leaf Folder"]
            },
            "maize": {
                "category": "cereal",
                "season": "Spring (Jan-Feb), Autumn (Jul-Aug)",
                "sowing": "Spring: Jan-Feb, Autumn: Jul-Aug",
                "harvest": "Spring: May-Jun, Autumn: Oct-Nov",
                "duration": "Hybrid: 90-110 days, Open: 100-120 days",
                "soil": "Well-drained loamy, sandy loam",
                "ph": "5.8-7.5",
                "temp": "24-30°C",
                "water": "5-6 irrigations",
                "varieties": ["P-1543", "DK-919", "P-30T60", "Azam", "Jalal", "Sahiwal-2002"],
                "regions": ["Punjab", "KPK"],
                "districts": ["Sahiwal", "Okara", "Pakpattan", "Kasur", "Swat", "Mardan"],
                "fertilizer": "NPK 150:75:75 kg/ha, Urea 4-5 bags/acre, DAP 2 bags/acre",
                "yield": "Hybrid: 70-100 maunds/acre, Open: 40-60 maunds/acre",
                "profit": "Rs. 45,000-70,000/acre",
                "diseases": ["Stalk Rot", "Leaf Blight", "Rust", "Maize Mosaic"],
                "pests": ["Stem Borer", "Armyworm", "Shoot Fly"]
            },
            "barley": {
                "category": "cereal",
                "season": "Rabi (Oct-Nov)",
                "sowing": "October-November",
                "harvest": "March-April",
                "duration": "110-130 days",
                "soil": "Sandy loam, well-drained",
                "ph": "6.0-7.5",
                "temp": "15-25°C",
                "water": "2-3 irrigations",
                "varieties": ["Haider-93", "Jau-2017", "Sultan-17"],
                "regions": ["Punjab", "Sindh", "Balochistan"],
                "districts": ["Bhakkar", "Layyah", "Muzaffargarh", "Khuzdar"],
                "fertilizer": "NPK 60:30:30 kg/ha",
                "yield": "20-25 maunds/acre",
                "profit": "Rs. 25,000-35,000/acre",
                "diseases": ["Rust", "Powdery Mildew", "Leaf Blight"],
                "pests": ["Aphids", "Armyworm"]
            },

            # Cash Crops
            "cotton": {
                "category": "cash",
                "season": "Kharif (Apr-Jun)",
                "sowing": "April to June",
                "harvest": "October to January",
                "duration": "150-180 days",
                "soil": "Well-drained loamy, black soil",
                "ph": "6.0-8.0",
                "temp": "25-35°C",
                "water": "8-10 irrigations",
                "varieties": ["Bt-121", "Bt-703", "Bt-886", "NIAB-878", "CIM-602", "FH-142"],
                "regions": ["Punjab", "Sindh"],
                "districts": ["Bahawalpur", "Rahim Yar Khan", "Multan", "Vehari", "Sanghar", "Nawabshah"],
                "fertilizer": "NPK 80:40:40 kg/ha, Urea 2-3 bags/acre, DAP 1 bag/acre, Boron 2-3 kg/acre",
                "yield": "Bt: 20-30 maunds/acre, Non-Bt: 15-25 maunds/acre",
                "profit": "Rs. 40,000-70,000/acre",
                "diseases": ["Cotton Leaf Curl Virus", "Bacterial Blight", "Root Rot", "Verticillium Wilt"],
                "pests": ["Whitefly", "Bollworm", "Thrips", "Mealybug"]
            },
            "sugarcane": {
                "category": "cash",
                "season": "Spring (Feb-Mar), Autumn (Sep-Oct)",
                "sowing": "Feb-Mar (spring), Sep-Oct (autumn)",
                "harvest": "Nov-Mar (10-16 months)",
                "duration": "10-16 months",
                "soil": "Deep fertile loamy, well-drained",
                "ph": "6.5-7.5",
                "temp": "25-32°C",
                "water": "15-20 irrigations",
                "varieties": ["CPF-248", "CPF-247", "HSF-240", "SPF-245", "CSSG-668", "Thatta-10"],
                "regions": ["Punjab", "Sindh", "KPK"],
                "districts": ["Faisalabad", "Jhang", "Sargodha", "Rahim Yar Khan", "Badin", "Charsadda"],
                "fertilizer": "NPK 250:115:115 kg/ha, Urea 5-6 bags/acre, DAP 2-3 bags/acre, FYM 15-20 tons/acre",
                "yield": "700-900 maunds/acre",
                "profit": "Rs. 60,000-90,000/acre",
                "diseases": ["Red Rot", "Smut", "Rust", "Grassy Shoot"],
                "pests": ["Top Borer", "Root Borer", "Scale Insect", "Termites"]
            },
            "tobacco": {
                "category": "cash",
                "season": "Rabi (Oct-Nov)",
                "sowing": "October-November",
                "harvest": "February-April",
                "duration": "120-150 days",
                "soil": "Sandy loam, well-drained",
                "ph": "5.5-6.5",
                "temp": "20-30°C",
                "water": "4-5 irrigations",
                "varieties": ["Speight G-28", "K-399", "Virginia", "FCV", "Burley"],
                "regions": ["KPK", "Punjab"],
                "districts": ["Swabi", "Mardan", "Charsadda", "Okara"],
                "fertilizer": "NPK 100:80:80 kg/ha, Urea 2 bags/acre, DAP 1.5 bags/acre",
                "yield": "20-25 maunds/acre",
                "profit": "Rs. 80,000-100,000/acre",
                "diseases": ["Frogeye Leaf Spot", "Black Shank", "Powdery Mildew", "Mosaic Virus"],
                "pests": ["Aphids", "Cutworm", "Hornworm", "Flea Beetle"]
            },
            "sugarbeet": {
                "category": "cash",
                "season": "Rabi (Oct-Nov)",
                "sowing": "October-November",
                "harvest": "April-May",
                "duration": "160-180 days",
                "soil": "Deep loamy, well-drained",
                "ph": "6.5-7.5",
                "temp": "15-25°C",
                "water": "5-6 irrigations",
                "varieties": ["KWS", "Sesvanderhave", "Beta"],
                "regions": ["Punjab", "KPK"],
                "districts": ["Faisalabad", "Okara", "Pakpattan", "Mardan"],
                "fertilizer": "NPK 150:100:100 kg/ha",
                "yield": "400-500 maunds/acre",
                "profit": "Rs. 50,000-70,000/acre",
                "diseases": ["Cercospora Leaf Spot", "Root Rot", "Powdery Mildew"],
                "pests": ["Aphids", "Leaf Miner", "Cutworm"]
            },

            # Pulses
            "gram (chickpea)": {
                "category": "pulse",
                "season": "Rabi (Oct-Nov)",
                "sowing": "October to November",
                "harvest": "March to April",
                "duration": "90-120 days",
                "soil": "Sandy loam, well-drained",
                "ph": "6.0-8.0",
                "temp": "15-25°C",
                "water": "1-2 irrigations",
                "varieties": ["Desi", "Kabuli", "Bittal-2016", "Noor-2019", "Punjab-2008"],
                "regions": ["Punjab", "Sindh", "KPK"],
                "districts": ["Bhakkar", "Layyah", "Muzaffargarh", "Dera Ghazi Khan", "Mianwali", "Khushab"],
                "fertilizer": "NPK 25:50:0 kg/ha, DAP 0.5 bag/acre, Rhizobium inoculation",
                "yield": "Rainfed: 10-15 maunds/acre, Irrigated: 15-20 maunds/acre",
                "profit": "Rs. 20,000-35,000/acre",
                "diseases": ["Ascochyta Blight", "Wilt", "Root Rot"],
                "pests": ["Pod Borer", "Cutworm", "Aphids"]
            },
            "lentil (masoor)": {
                "category": "pulse",
                "season": "Rabi (Oct-Nov)",
                "sowing": "October-November",
                "harvest": "March-April",
                "duration": "90-110 days",
                "soil": "Sandy loam, well-drained",
                "ph": "6.0-7.5",
                "temp": "15-25°C",
                "water": "1-2 irrigations",
                "varieties": ["Masoor-2006", "Punjab Masoor", "NIAB Masoor-2002"],
                "regions": ["Punjab", "Sindh", "KPK"],
                "districts": ["Attock", "Rawalpindi", "Jhelum", "Chakwal"],
                "fertilizer": "DAP 0.5 bag/acre, Rhizobium inoculation",
                "yield": "8-10 maunds/acre",
                "profit": "Rs. 15,000-20,000/acre",
                "diseases": ["Wilt", "Root Rot", "Rust"],
                "pests": ["Aphids", "Pod Borer"]
            },
            "mung bean": {
                "category": "pulse",
                "season": "Spring (Feb-Mar), Kharif (Jul-Aug)",
                "sowing": "Spring: Feb-Mar, Kharif: Jul-Aug",
                "harvest": "Spring: May-Jun, Kharif: Oct-Nov",
                "duration": "70-90 days",
                "soil": "Sandy loam, well-drained",
                "ph": "6.0-7.5",
                "temp": "25-35°C",
                "water": "2-3 irrigations",
                "varieties": ["NIAB Mung-2011", "Azri Mung-2006", "Ramzan"],
                "regions": ["Punjab", "Sindh"],
                "districts": ["Vehari", "Lodhran", "Bahawalnagar", "Rahim Yar Khan"],
                "fertilizer": "DAP 0.5 bag/acre, Rhizobium inoculation",
                "yield": "8-12 maunds/acre",
                "profit": "Rs. 20,000-30,000/acre",
                "diseases": ["Yellow Mosaic Virus", "Cercospora Leaf Spot", "Powdery Mildew"],
                "pests": ["Whitefly", "Aphids", "Pod Borer"]
            },
            "mash bean": {
                "category": "pulse",
                "season": "Kharif (Jul-Aug)",
                "sowing": "July-August",
                "harvest": "October-November",
                "duration": "80-90 days",
                "soil": "Sandy loam",
                "ph": "6.0-7.5",
                "temp": "25-35°C",
                "water": "2-3 irrigations",
                "varieties": ["Mash-2006", "Mash-2011"],
                "regions": ["Punjab", "Sindh"],
                "districts": ["Bahawalpur", "Rahim Yar Khan", "Multan"],
                "fertilizer": "DAP 0.5 bag/acre",
                "yield": "6-8 maunds/acre",
                "profit": "Rs. 15,000-20,000/acre",
                "diseases": ["Yellow Mosaic Virus", "Leaf Spot"],
                "pests": ["Whitefly", "Pod Borer"]
            },

            # Oilseeds
            "mustard": {
                "category": "oilseed",
                "season": "Rabi (Oct-Nov)",
                "sowing": "October-November",
                "harvest": "March-April",
                "duration": "110-130 days",
                "soil": "Loamy, sandy loam",
                "ph": "6.0-7.5",
                "temp": "10-25°C",
                "water": "2-3 irrigations",
                "varieties": ["Raya Anmol", "Punjab Sarson", "Canola", "Abaseen"],
                "regions": ["Punjab", "Sindh"],
                "districts": ["Bahawalpur", "Rahim Yar Khan", "Multan", "Dera Ghazi Khan"],
                "fertilizer": "NPK 60:40:40 kg/ha, Urea 1-1.5 bags/acre, DAP 0.5-1 bag/acre",
                "yield": "10-15 maunds/acre",
                "profit": "Rs. 20,000-25,000/acre",
                "diseases": ["White Rust", "Downy Mildew", "Alternaria Blight"],
                "pests": ["Aphids", "Painted Bug", "Caterpillar"]
            },
            "sunflower": {
                "category": "oilseed",
                "season": "Spring (Jan-Feb), Autumn (Jul-Aug)",
                "sowing": "Spring: Jan-Feb, Autumn: Jul-Aug",
                "harvest": "Spring: May-Jun, Autumn: Oct-Nov",
                "duration": "100-120 days",
                "soil": "Loamy, well-drained",
                "ph": "6.0-7.5",
                "temp": "20-30°C",
                "water": "3-4 irrigations",
                "varieties": ["Hysun-33", "NK-Senil", "DK-4045", "SMH-0907"],
                "regions": ["Punjab", "Sindh", "KPK"],
                "districts": ["Sargodha", "Mandi Bahauddin", "Gujrat", "Hafizabad"],
                "fertilizer": "NPK 80:60:60 kg/ha, Urea 2 bags/acre, DAP 1.5 bags/acre",
                "yield": "15-20 maunds/acre",
                "profit": "Rs. 25,000-35,000/acre",
                "diseases": ["Downy Mildew", "Rust", "Head Rot", "Sclerotinia Rot"],
                "pests": ["Cutworm", "Armyworm", "Aphids", "Sunflower Moth"]
            },
            "canola": {
                "category": "oilseed",
                "season": "Rabi (Oct-Nov)",
                "sowing": "October-November",
                "harvest": "March-April",
                "duration": "120-140 days",
                "soil": "Loamy, well-drained",
                "ph": "6.0-7.0",
                "temp": "10-25°C",
                "water": "3-4 irrigations",
                "varieties": ["Canola-2018", "Punjab Canola", "Rainbow", "Shiralee"],
                "regions": ["Punjab", "Sindh"],
                "districts": ["Sahiwal", "Okara", "Pakpattan", "Bahawalnagar"],
                "fertilizer": "NPK 80:50:50 kg/ha, Urea 2 bags/acre, DAP 1.5 bags/acre",
                "yield": "12-16 maunds/acre",
                "profit": "Rs. 30,000-40,000/acre",
                "diseases": ["White Rust", "Alternaria Blight", "Downy Mildew"],
                "pests": ["Aphids", "Flea Beetle", "Cabbage Caterpillar"]
            },
            "groundnut": {
                "category": "oilseed",
                "season": "Kharif (May-Jun)",
                "sowing": "May-June",
                "harvest": "October-November",
                "duration": "140-160 days",
                "soil": "Sandy loam, well-drained",
                "ph": "6.0-7.0",
                "temp": "25-30°C",
                "water": "4-5 irrigations",
                "varieties": ["BARI-2011", "Chakwal-2016", "Golden", "Banki"],
                "regions": ["Punjab", "KPK"],
                "districts": ["Attock", "Rawalpindi", "Chakwal", "Jhelum", "Karor"],
                "fertilizer": "NPK 40:80:60 kg/ha, Gypsum 200 kg/acre",
                "yield": "20-25 maunds/acre (unshelled)",
                "profit": "Rs. 40,000-50,000/acre",
                "diseases": ["Tikka Leaf Spot", "Rust", "Stem Rot"],
                "pests": ["White Grub", "Aphids", "Thrips", "Termites"]
            },
            "sesame": {
                "category": "oilseed",
                "season": "Kharif (Jun-Jul)",
                "sowing": "June-July",
                "harvest": "October-November",
                "duration": "90-110 days",
                "soil": "Sandy loam, well-drained",
                "ph": "5.5-7.0",
                "temp": "25-30°C",
                "water": "2-3 irrigations",
                "varieties": ["TS-5", "PR-129", "SG-30", "NIAB Sesame"],
                "regions": ["Punjab", "Sindh"],
                "districts": ["Bahawalpur", "Rahim Yar Khan", "Multan", "Sukkur"],
                "fertilizer": "NPK 30:40:20 kg/ha",
                "yield": "5-7 maunds/acre",
                "profit": "Rs. 25,000-35,000/acre",
                "diseases": ["Phytophthora Blight", "Leaf Spot", "Wilt"],
                "pests": ["Leaf Roller", "Gall Fly", "Aphids"]
            },

            # Vegetables
            "potato": {
                "category": "vegetable",
                "season": "Autumn (Sep-Oct), Spring (Jan-Feb)",
                "sowing": "Autumn: Sep-Oct, Spring: Jan-Feb",
                "harvest": "Autumn: Dec-Jan, Spring: Apr-May",
                "duration": "90-120 days",
                "soil": "Sandy loam, well-drained",
                "ph": "5.5-6.5",
                "temp": "15-20°C",
                "water": "8-10 irrigations",
                "varieties": ["Desiree", "Cardinal", "Sante", "Asterix", "Diamond", "Ultimus"],
                "regions": ["Punjab", "KPK"],
                "districts": ["Sahiwal", "Okara", "Pakpattan", "Kasur", "Depalpur", "Swat", "Abbottabad"],
                "fertilizer": "NPK 200:100:100 kg/ha, Urea 4-5 bags/acre, DAP 2 bags/acre, MOP 2 bags/acre, FYM 15-20 tons/acre",
                "yield": "150-200 maunds/acre",
                "profit": "Rs. 80,000-120,000/acre",
                "diseases": ["Late Blight", "Early Blight", "Black Scurf", "Common Scab"],
                "pests": ["Potato Tuber Moth", "Aphids", "Cutworm"]
            },
            "tomato": {
                "category": "vegetable",
                "season": "Rabi (Oct-Nov), Spring (Feb-Mar), Kharif (Jun-Jul)",
                "sowing": "Region-specific",
                "harvest": "70-90 days after transplanting",
                "duration": "90-120 days",
                "soil": "Sandy loam, well-drained",
                "ph": "6.0-6.8",
                "temp": "18-28°C",
                "water": "Drip irrigation recommended",
                "varieties": ["Roma", "Money Maker", "Rio Grande", "Nagina", "Sahel", "T-1359"],
                "regions": ["Punjab", "Sindh", "KPK", "Balochistan"],
                "districts": ["Multan", "Khanewal", "Vehari", "Tandojam", "Kalat", "Pishin"],
                "fertilizer": "NPK 120:60:60 kg/ha, Urea 2-3 bags/acre, DAP 1.5 bags/acre, MOP 1 bag/acre, FYM 15-20 tons/acre",
                "yield": "Hybrid: 200-300 maunds/acre, Open: 150-200 maunds/acre",
                "profit": "Rs. 80,000-150,000/acre",
                "diseases": ["Early Blight", "Late Blight", "Leaf Curl", "Fusarium Wilt"],
                "pests": ["Whitefly", "Fruit Borer", "Aphids", "Mites"]
            },
            "onion": {
                "category": "vegetable",
                "season": "Rabi (Oct-Dec), Kharif (May-Jun)",
                "sowing": "Seed: Oct-Nov, Transplants: Dec-Jan",
                "harvest": "April-June",
                "duration": "100-150 days",
                "soil": "Sandy loam, loamy",
                "ph": "6.0-7.0",
                "temp": "13-24°C",
                "water": "8-10 irrigations",
                "varieties": ["Phulkara", "Swat-1", "Nasarpuri", "F1 Galaxy", "Red Creole"],
                "regions": ["Punjab", "Sindh", "Balochistan"],
                "districts": ["Sahiwal", "Okara", "Pakpattan", "Sukkur", "Khairpur", "Kalat", "Mastung"],
                "fertilizer": "NPK 100:50:50 kg/ha, Urea 2 bags/acre, DAP 1 bag/acre, MOP 1 bag/acre, FYM 15-20 tons/acre",
                "yield": "Hybrid: 200-300 maunds/acre, Local: 150-200 maunds/acre",
                "profit": "Rs. 60,000-100,000/acre",
                "diseases": ["Purple Blotch", "Downy Mildew", "Smut", "Basal Rot"],
                "pests": ["Thrips", "Onion Fly", "Cutworm"]
            },
            "chili": {
                "category": "vegetable",
                "season": "Kharif (Apr-May), Rabi (Oct-Nov)",
                "sowing": "April-May (main)",
                "harvest": "60-90 days after transplanting",
                "duration": "90-120 days",
                "soil": "Sandy loam",
                "ph": "6.0-7.0",
                "temp": "20-30°C",
                "water": "Drip irrigation preferred",
                "varieties": ["Longi", "Mirch-444", "Sanam", "Tatapuri", "Hybrids"],
                "regions": ["Sindh", "Punjab"],
                "districts": ["Kunri", "Umarkot", "Mirpurkhas", "Tando Allahyar", "Vehari"],
                "fertilizer": "NPK 120:60:60 kg/ha, Urea 2.5 bags/acre, DAP 1.5 bags/acre, MOP 1 bag/acre, FYM 15-20 tons/acre",
                "yield": "Green: 80-100 maunds/acre, Dry: 15-20 maunds/acre",
                "profit": "Rs. 60,000-90,000/acre",
                "diseases": ["Anthracnose", "Leaf Curl", "Damping Off"],
                "pests": ["Thrips", "Mites", "Fruit Borer"]
            },
            "brinjal (eggplant)": {
                "category": "vegetable",
                "season": "Kharif (May-Jun), Spring (Feb-Mar)",
                "sowing": "May-June (main)",
                "harvest": "70-90 days after transplanting",
                "duration": "100-120 days",
                "soil": "Loamy",
                "ph": "5.5-7.5",
                "temp": "22-30°C",
                "water": "8-10 irrigations",
                "varieties": ["Black Beauty", "Purple Long", "Nirala", "Sandal"],
                "regions": ["Punjab", "Sindh", "KPK"],
                "districts": ["Multan", "Bahawalpur", "Sahiwal", "Tandojam"],
                "fertilizer": "NPK 100:60:60 kg/ha, Urea 2 bags/acre, DAP 1.5 bags/acre, MOP 1 bag/acre, FYM 15-20 tons/acre",
                "yield": "200-250 maunds/acre",
                "profit": "Rs. 50,000-80,000/acre",
                "diseases": ["Bacterial Wilt", "Phomopsis Blight", "Little Leaf"],
                "pests": ["Shoot Borer", "Whitefly", "Epilachna Beetle"]
            },
            "okra (ladyfinger)": {
                "category": "vegetable",
                "season": "Kharif (May-Jun)",
                "sowing": "May-June",
                "harvest": "50-60 days after sowing",
                "duration": "90-100 days",
                "soil": "Loamy",
                "ph": "6.0-7.5",
                "temp": "25-35°C",
                "water": "6-7 irrigations",
                "varieties": ["Sabz Pari", "Green Star", "Punjab Selection"],
                "regions": ["Punjab", "Sindh"],
                "districts": ["Multan", "Bahawalpur", "Lahore", "Hyderabad"],
                "fertilizer": "NPK 80:40:40 kg/ha, Urea 1.5 bags/acre, DAP 1 bag/acre",
                "yield": "80-100 maunds/acre",
                "profit": "Rs. 40,000-60,000/acre",
                "diseases": ["Yellow Vein Mosaic", "Powdery Mildew", "Fusarium Wilt"],
                "pests": ["Jassids", "Whitefly", "Fruit Borer"]
            },
            "cabbage": {
                "category": "vegetable",
                "season": "Rabi (Sep-Oct)",
                "sowing": "September-October",
                "harvest": "December-February",
                "duration": "90-120 days",
                "soil": "Loamy",
                "ph": "6.0-7.5",
                "temp": "15-20°C",
                "water": "6-8 irrigations",
                "varieties": ["Golden Acre", "Copenhagen Market"],
                "regions": ["Punjab", "KPK", "Balochistan"],
                "districts": ["Lahore", "Sheikhupura", "Sahiwal", "Peshawar", "Quetta"],
                "fertilizer": "NPK 120:80:60 kg/ha, Urea 2.5 bags/acre, DAP 1.5 bags/acre, MOP 1 bag/acre",
                "yield": "250-300 maunds/acre",
                "profit": "Rs. 60,000-80,000/acre",
                "diseases": ["Black Rot", "Downy Mildew", "Club Root"],
                "pests": ["Cabbage Worm", "Aphids", "Diamondback Moth"]
            },
            "cauliflower": {
                "category": "vegetable",
                "season": "Rabi (Sep-Oct)",
                "sowing": "September-October",
                "harvest": "December-March",
                "duration": "100-130 days",
                "soil": "Loamy",
                "ph": "6.0-7.0",
                "temp": "15-20°C",
                "water": "6-8 irrigations",
                "varieties": ["Snowball", "Early Kunwari"],
                "regions": ["Punjab", "KPK"],
                "districts": ["Lahore", "Kasur", "Sahiwal", "Peshawar"],
                "fertilizer": "NPK 100:60:60 kg/ha, Urea 2 bags/acre, DAP 1.5 bags/acre, MOP 1 bag/acre",
                "yield": "200-250 maunds/acre",
                "profit": "Rs. 50,000-70,000/acre",
                "diseases": ["Black Rot", "Club Root", "Downy Mildew"],
                "pests": ["Diamondback Moth", "Aphids", "Cutworm"]
            },
            "carrot": {
                "category": "vegetable",
                "season": "Rabi (Sep-Oct)",
                "sowing": "September-October",
                "harvest": "December-February",
                "duration": "90-110 days",
                "soil": "Sandy loam",
                "ph": "6.0-7.0",
                "temp": "16-20°C",
                "water": "5-6 irrigations",
                "varieties": ["T-29", "Nantes"],
                "regions": ["Punjab", "KPK", "Sindh"],
                "districts": ["Kasur", "Okara", "Sahiwal", "Hyderabad"],
                "fertilizer": "NPK 60:40:40 kg/ha, Urea 1 bag/acre, DAP 0.5 bag/acre",
                "yield": "150-200 maunds/acre",
                "profit": "Rs. 40,000-60,000/acre",
                "diseases": ["Leaf Blight", "Root Rot"],
                "pests": ["Aphids", "Cutworm", "Carrot Fly"]
            },
            "radish": {
                "category": "vegetable",
                "season": "Rabi (Sep-Oct)",
                "sowing": "September-October",
                "harvest": "November-December",
                "duration": "40-60 days",
                "soil": "Sandy loam",
                "ph": "6.0-7.5",
                "temp": "10-20°C",
                "water": "4-5 irrigations",
                "varieties": ["White Icicle", "Desi Long"],
                "regions": ["Punjab", "Sindh", "KPK"],
                "districts": ["Lahore", "Kasur", "Sahiwal", "Hyderabad"],
                "fertilizer": "NPK 50:40:40 kg/ha",
                "yield": "150-200 maunds/acre",
                "profit": "Rs. 30,000-40,000/acre",
                "diseases": ["Downy Mildew", "White Rust"],
                "pests": ["Aphids", "Flea Beetle"]
            },
            "spinach": {
                "category": "vegetable",
                "season": "Rabi (Sep-Oct), Spring (Feb-Mar)",
                "sowing": "September-October, February-March",
                "harvest": "30-45 days after sowing",
                "duration": "50-70 days",
                "soil": "Loamy",
                "ph": "6.0-7.5",
                "temp": "15-20°C",
                "water": "4-5 irrigations",
                "varieties": ["Local Green"],
                "regions": ["All regions"],
                "districts": ["All districts"],
                "fertilizer": "NPK 60:40:40 kg/ha",
                "yield": "80-100 maunds/acre",
                "profit": "Rs. 25,000-35,000/acre",
                "diseases": ["Downy Mildew", "White Rust"],
                "pests": ["Leaf Miner", "Aphids"]
            },
            "cucumber": {
                "category": "vegetable",
                "season": "Spring (Feb-Mar), Kharif (Jun-Jul)",
                "sowing": "February-March, June-July",
                "harvest": "50-70 days after sowing",
                "duration": "80-100 days",
                "soil": "Sandy loam",
                "ph": "6.0-7.0",
                "temp": "20-30°C",
                "water": "Drip irrigation recommended",
                "varieties": ["Marketmore", "Local Hybrid"],
                "regions": ["Punjab", "Sindh"],
                "districts": ["Lahore", "Kasur", "Sahiwal", "Hyderabad"],
                "fertilizer": "NPK 80:40:40 kg/ha",
                "yield": "150-200 maunds/acre",
                "profit": "Rs. 50,000-70,000/acre",
                "diseases": ["Powdery Mildew", "Downy Mildew", "Mosaic Virus"],
                "pests": ["Fruit Fly", "Aphids", "Mites"]
            },
            "peas": {
                "category": "vegetable",
                "season": "Rabi (Oct-Nov)",
                "sowing": "October-November",
                "harvest": "January-February",
                "duration": "90-110 days",
                "soil": "Loamy",
                "ph": "6.0-7.5",
                "temp": "10-20°C",
                "water": "3-4 irrigations",
                "varieties": ["Climax", "Meteor"],
                "regions": ["Punjab", "KPK"],
                "districts": ["Kasur", "Okara", "Sahiwal", "Peshawar"],
                "fertilizer": "DAP 1 bag/acre, organic manure",
                "yield": "40-50 maunds/acre",
                "profit": "Rs. 30,000-45,000/acre",
                "diseases": ["Powdery Mildew", "Downy Mildew", "Root Rot"],
                "pests": ["Pod Borer", "Aphids"]
            },
            "pumpkin": {
                "category": "vegetable",
                "season": "Kharif (May-Jun)",
                "sowing": "May-June",
                "harvest": "August-October",
                "duration": "90-120 days",
                "soil": "Sandy loam",
                "ph": "6.0-7.5",
                "temp": "20-30°C",
                "water": "5-6 irrigations",
                "varieties": ["Local Round"],
                "regions": ["Punjab", "Sindh"],
                "districts": ["Multan", "Bahawalpur", "Rahim Yar Khan"],
                "fertilizer": "NPK 80:40:40 kg/ha",
                "yield": "150-200 maunds/acre",
                "profit": "Rs. 30,000-40,000/acre",
                "diseases": ["Powdery Mildew", "Downy Mildew"],
                "pests": ["Fruit Fly", "Pumpkin Beetle"]
            },
            "bitter gourd": {
                "category": "vegetable",
                "season": "Kharif (May-Jun)",
                "sowing": "May-June",
                "harvest": "60-80 days after sowing",
                "duration": "100-120 days",
                "soil": "Loamy",
                "ph": "6.0-7.0",
                "temp": "25-30°C",
                "water": "Drip irrigation recommended",
                "varieties": ["Palee", "Faisalabad Long"],
                "regions": ["Punjab", "Sindh"],
                "districts": ["Multan", "Bahawalpur", "Lahore", "Hyderabad"],
                "fertilizer": "NPK 80:40:40 kg/ha",
                "yield": "80-100 maunds/acre",
                "profit": "Rs. 50,000-70,000/acre",
                "diseases": ["Downy Mildew", "Powdery Mildew", "Mosaic Virus"],
                "pests": ["Fruit Fly", "Mites", "Aphids"]
            },
            "bottle gourd": {
                "category": "vegetable",
                "season": "Kharif (May-Jun)",
                "sowing": "May-June",
                "harvest": "60-75 days after sowing",
                "duration": "90-110 days",
                "soil": "Loamy",
                "ph": "6.0-7.5",
                "temp": "22-30°C",
                "water": "6-7 irrigations",
                "varieties": ["Anmol"],
                "regions": ["Punjab", "Sindh"],
                "districts": ["Multan", "Bahawalpur", "Lahore", "Hyderabad"],
                "fertilizer": "NPK 80:40:40 kg/ha",
                "yield": "150-200 maunds/acre",
                "profit": "Rs. 40,000-50,000/acre",
                "diseases": ["Powdery Mildew", "Downy Mildew", "Mosaic Virus"],
                "pests": ["Fruit Fly", "Mites", "Aphids"]
            },
            "turnip": {
                "category": "vegetable",
                "season": "Rabi (Sep-Oct)",
                "sowing": "September-October",
                "harvest": "November-December",
                "duration": "60-80 days",
                "soil": "Sandy loam",
                "ph": "6.0-7.5",
                "temp": "10-20°C",
                "water": "4-5 irrigations",
                "varieties": ["Purple Top"],
                "regions": ["Punjab", "KPK"],
                "districts": ["Lahore", "Kasur", "Sahiwal", "Peshawar"],
                "fertilizer": "NPK 60:40:40 kg/ha",
                "yield": "150-200 maunds/acre",
                "profit": "Rs. 30,000-40,000/acre",
                "diseases": ["Downy Mildew", "White Rust"],
                "pests": ["Aphids", "Flea Beetle"]
            },
            "garlic": {
                "category": "vegetable",
                "season": "Rabi (Sep-Oct)",
                "sowing": "September-October",
                "harvest": "February-March",
                "duration": "120-150 days",
                "soil": "Sandy loam",
                "ph": "6.0-7.0",
                "temp": "12-25°C",
                "water": "6-7 irrigations",
                "varieties": ["Chinese White", "Local White"],
                "regions": ["Punjab", "Sindh"],
                "districts": ["Kasur", "Sahiwal", "Okara", "Hyderabad"],
                "fertilizer": "NPK 100:50:50 kg/ha, FYM 15-20 tons/acre",
                "yield": "80-100 maunds/acre",
                "profit": "Rs. 80,000-100,000/acre",
                "diseases": ["White Rot", "Purple Blotch", "Downy Mildew"],
                "pests": ["Thrips", "Mites"]
            },

            # Fruits
            "mango": {
                "category": "fruit",
                "season": "Summer (Jun-Aug)",
                "sowing": "August-September (grafting)",
                "harvest": "June-August",
                "duration": "5-8 years to bearing",
                "soil": "Well-drained loamy",
                "ph": "5.5-7.5",
                "temp": "24-30°C",
                "water": "Drip irrigation recommended",
                "varieties": ["Sindhri", "Chaunsa", "Anwar Ratol", "Dusehri", "Langra"],
                "regions": ["Punjab", "Sindh"],
                "districts": ["Multan", "Rahim Yar Khan", "Bahawalpur", "Mirpurkhas", "Hyderabad"],
                "fertilizer": "FYM 40-50 kg/tree, NPK 1:1:1 kg/tree/year",
                "yield": "150-200 kg/tree",
                "profit": "Rs. 200,000-300,000/acre",
                "diseases": ["Powdery Mildew", "Anthracnose", "Mango Malformation", "Die Back"],
                "pests": ["Fruit Fly", "Mango Hopper", "Mealybug", "Scale Insect"]
            },
            "citrus": {
                "category": "fruit",
                "season": "Winter (Dec-Feb)",
                "sowing": "February-March",
                "harvest": "December-February",
                "duration": "3-5 years to bearing",
                "soil": "Well-drained loamy",
                "ph": "6.0-8.0",
                "temp": "10-35°C",
                "water": "Drip irrigation recommended",
                "varieties": ["Kinnow", "Feutrell's Early", "Musambi", "Red Blood", "Grapefruit"],
                "regions": ["Punjab", "KPK"],
                "districts": ["Sargodha", "Toba Tek Singh", "Jhang", "Mandi Bahauddin"],
                "fertilizer": "FYM 40-50 kg/tree, NPK 1:1:1 kg/tree/year",
                "yield": "200-250 kg/tree",
                "profit": "Rs. 150,000-200,000/acre",
                "diseases": ["Citrus Canker", "Gummosis", "Greening", "Scab"],
                "pests": ["Citrus Psyllid", "Leaf Miner", "Scale Insect", "Aphids"]
            },
            "banana": {
                "category": "fruit",
                "season": "Year-round",
                "sowing": "February-March",
                "harvest": "12-14 months after planting",
                "duration": "12-14 months",
                "soil": "Deep loamy, well-drained",
                "ph": "6.0-7.5",
                "temp": "25-35°C",
                "water": "Drip irrigation recommended",
                "varieties": ["Basrai", "Grand Naine", "William Hybrid"],
                "regions": ["Sindh"],
                "districts": ["Thatta", "Badin", "Hyderabad", "Mirpurkhas"],
                "fertilizer": "NPK 200:100:300 g/plant/year",
                "yield": "30-40 tons/acre",
                "profit": "Rs. 150,000-200,000/acre",
                "diseases": ["Panama Wilt", "Sigatoka Leaf Spot", "Bunchy Top"],
                "pests": ["Rhizome Weevil", "Pseudostem Borer", "Aphids"]
            },
            "apple": {
                "category": "fruit",
                "season": "Autumn (Aug-Oct)",
                "sowing": "February-March",
                "harvest": "August-October",
                "duration": "4-6 years to bearing",
                "soil": "Well-drained loamy",
                "ph": "6.0-7.0",
                "temp": "10-25°C",
                "water": "Drip irrigation recommended",
                "varieties": ["Kala Kulu", "Amri", "Kashmiri", "Red Delicious", "Golden Delicious"],
                "regions": ["Balochistan", "KPK"],
                "districts": ["Quetta", "Kalat", "Ziarat", "Hunza", "Skardu"],
                "fertilizer": "FYM 30-40 kg/tree, NPK 1:0.5:1 kg/tree/year",
                "yield": "80-100 kg/tree",
                "profit": "Rs. 200,000-300,000/acre",
                "diseases": ["Scab", "Powdery Mildew", "Fire Blight", "Collar Rot"],
                "pests": ["Codling Moth", "Aphids", "Mites", "Scale Insect"]
            },
            "date palm": {
                "category": "fruit",
                "season": "Summer (Jul-Aug)",
                "sowing": "Throughout year",
                "harvest": "July-August",
                "duration": "4-5 years to bearing",
                "soil": "Sandy loam, well-drained",
                "ph": "7.0-8.5",
                "temp": "25-40°C",
                "water": "Flood irrigation",
                "varieties": ["Aseel", "Halawi", "Zahidi", "Dhakki", "Begum Jangi"],
                "regions": ["Sindh", "Balochistan", "Punjab"],
                "districts": ["Khairpur", "Sukkur", "Turbat", "Panjgur", "Dera Ismail Khan"],
                "fertilizer": "FYM 40-50 kg/palm, NPK 2:1:1 kg/palm/year",
                "yield": "80-100 kg/palm",
                "profit": "Rs. 250,000-350,000/acre",
                "diseases": ["Black Scorch", "Fruit Rot", "Leaf Spot", "Bayoud Disease"],
                "pests": ["Dusky Date Bug", "Red Palm Weevil", "Scale Insect", "Mites"]
            },
            "guava": {
                "category": "fruit",
                "season": "Summer (Jul-Aug), Winter (Dec-Jan)",
                "sowing": "February-March",
                "harvest": "July-August, December-January",
                "duration": "2-3 years to bearing",
                "soil": "Well-drained loamy",
                "ph": "5.5-7.0",
                "temp": "20-30°C",
                "water": "6-8 irrigations/year",
                "varieties": ["Surahi", "Lahori Red", "Seedless", "Allahabad Safeda"],
                "regions": ["Punjab", "Sindh", "KPK"],
                "districts": ["Lahore", "Sheikhupura", "Sahiwal", "Hyderabad", "Peshawar"],
                "fertilizer": "FYM 20-30 kg/tree, NPK 0.5:0.3:0.5 kg/tree/year",
                "yield": "60-80 kg/tree",
                "profit": "Rs. 100,000-150,000/acre",
                "diseases": ["Wilt", "Anthracnose", "Canker", "Rust"],
                "pests": ["Fruit Fly", "Mealybug", "Scale Insect", "Aphids"]
            },

            # Fodder
            "alfalfa": {
                "category": "fodder",
                "season": "Year-round",
                "sowing": "October-November, February-March",
                "harvest": "Every 30-35 days",
                "duration": "3-5 years (perennial)",
                "soil": "Well-drained loamy",
                "ph": "6.5-7.0",
                "temp": "15-25°C",
                "water": "8-10 irrigations/year",
                "varieties": ["Lucerne", "Sargodha-2002", "Punjab-2010"],
                "regions": ["Punjab", "Sindh", "KPK", "Balochistan"],
                "districts": ["All districts"],
                "fertilizer": "DAP 1 bag/acre, Rhizobium inoculation",
                "yield": "400-500 maunds/acre/year",
                "profit": "Rs. 60,000-80,000/acre/year",
                "diseases": ["Downy Mildew", "Leaf Spot", "Rust"],
                "pests": ["Aphids", "Leafhopper"]
            },
            "maize (fodder)": {
                "category": "fodder",
                "season": "Spring (Feb-Mar), Autumn (Jul-Aug)",
                "sowing": "February-March, July-August",
                "harvest": "50-60 days after sowing",
                "duration": "50-60 days",
                "soil": "Loamy",
                "ph": "6.0-7.5",
                "temp": "25-30°C",
                "water": "3-4 irrigations",
                "varieties": ["Akbar", "Sultan"],
                "regions": ["Punjab", "Sindh", "KPK"],
                "districts": ["All districts"],
                "fertilizer": "Urea 1.5 bags/acre, DAP 0.5 bag/acre",
                "yield": "300-400 maunds/acre",
                "profit": "Rs. 40,000-50,000/acre",
                "diseases": ["Stalk Rot", "Leaf Blight"],
                "pests": ["Stem Borer"]
            },
            "sorghum": {
                "category": "fodder",
                "season": "Kharif (Apr-May)",
                "sowing": "April-May",
                "harvest": "60-70 days after sowing",
                "duration": "60-70 days",
                "soil": "Sandy loam",
                "ph": "6.0-7.5",
                "temp": "25-35°C",
                "water": "2-3 irrigations",
                "varieties": ["JS-2002", "JS-263", "Pegasus"],
                "regions": ["Punjab", "Sindh"],
                "districts": ["Sahiwal", "Okara", "Faisalabad", "Hyderabad"],
                "fertilizer": "Urea 1 bag/acre, DAP 0.5 bag/acre",
                "yield": "250-300 maunds/acre",
                "profit": "Rs. 35,000-45,000/acre",
                "diseases": ["Anthracnose", "Rust", "Leaf Blight"],
                "pests": ["Shoot Fly", "Stem Borer"]
            }
        }

        # ============ SOIL TYPES ============
        self.soils = {
            "sandy": {
                "name": "Sandy Soil",
                "local": "Raitli",
                "texture": "Coarse, loose",
                "drainage": "Excellent",
                "water_holding": "Poor",
                "nutrients": "Low",
                "ph": "6.0-8.0",
                "improvement": ["Add FYM 20-25 tons/acre", "Green manuring", "Mulching", "Frequent light irrigation"],
                "crops": ["Groundnut", "Watermelon", "Carrot", "Potato", "Sunflower", "Millet"],
                "regions": ["Thal desert", "Cholistan", "Coastal Sindh", "Balochistan"]
            },
            "clay": {
                "name": "Clay Soil",
                "local": "Gharo",
                "texture": "Fine, sticky",
                "drainage": "Poor",
                "water_holding": "Excellent",
                "nutrients": "High",
                "ph": "5.5-7.5",
                "improvement": ["Add sand/silt", "Gypsum application", "Deep ploughing", "Raised beds"],
                "crops": ["Rice", "Wheat", "Sugarcane", "Cotton", "Cabbage", "Spinach"],
                "regions": ["Rice belt", "Indus delta", "Central Punjab"]
            },
            "loamy": {
                "name": "Loamy Soil",
                "local": "Domat",
                "texture": "Medium, ideal",
                "drainage": "Good",
                "water_holding": "Good",
                "nutrients": "Moderate to high",
                "ph": "6.0-7.5",
                "improvement": ["Maintain organic matter", "Crop rotation", "Balanced fertilization"],
                "crops": ["All crops - wheat, maize, cotton, vegetables"],
                "regions": ["Central Punjab", "Irrigated plains", "Peshawar valley"]
            },
            "saline": {
                "name": "Saline Soil",
                "local": "Kallar",
                "texture": "Variable",
                "drainage": "Poor",
                "water_holding": "Variable",
                "nutrients": "Low (salt toxicity)",
                "ph": "7.5-9.0",
                "improvement": ["Gypsum application", "Leaching", "Salt-tolerant crops", "Organic matter"],
                "crops": ["Kallar grass", "Date palm", "Barley", "Sugarbeet", "Sunflower"],
                "regions": ["Thatta", "Badin", "Sujawal", "Southern Punjab"]
            },
            "waterlogged": {
                "name": "Waterlogged Soil",
                "local": "Sem",
                "texture": "Variable",
                "drainage": "Very poor",
                "water_holding": "Excess",
                "nutrients": "Low (anaerobic)",
                "ph": "5.5-7.0",
                "improvement": ["Surface drainage", "Subsurface drainage", "Tubewells", "Biological drainage"],
                "crops": ["Rice", "Deep water rice", "Bana grass", "Bamboo"],
                "regions": ["Rice-wheat zone", "Sindh", "Waterlogged areas"]
            },
            "alluvial": {
                "name": "Alluvial Soil",
                "local": "Sailabi",
                "texture": "Silt loam to clay loam",
                "drainage": "Moderate",
                "water_holding": "Good",
                "nutrients": "Moderate to high",
                "ph": "6.5-8.0",
                "improvement": ["River silt application", "Organic matter", "Balanced fertilization"],
                "crops": ["Cotton", "Wheat", "Sugarcane", "Rice", "Maize"],
                "regions": ["Indus plains", "River banks", "Flood plains"]
            }
        }

        # ============ INTENTS ============
        self.intents = [
            "Cultivation", "SowingTime", "HarvestTime", "Soil", "Irrigation",
            "Fertilizer", "Pesticide", "Diseases", "Yield", "Profit",
            "Varieties", "Climate", "Water", "Storage", "Intercropping",
            "Organic", "SeedRate", "Spacing", "Regions", "Government"
        ]

        # ============ QUESTION TEMPLATES ============
        self.templates = {
            "Cultivation": [
                "How to grow {crop} in Pakistan?",
                "Complete cultivation guide for {crop}",
                "How to cultivate {crop}?",
                "Tell me about {crop} farming",
                "Step by step process for growing {crop}",
                "{crop} cultivation practices",
                "How to get high yield of {crop}?",
                "Best practices for {crop} cultivation",
                "Can you explain {crop} farming?",
                "What is the method to grow {crop}?",
                "How do farmers grow {crop} in Pakistan?",
                "I want to learn about {crop} cultivation",
                "Guide for {crop} farming",
                "How to plant {crop}?",
                "{crop} growing tips"
            ],
            "SowingTime": [
                "When to sow {crop}?",
                "Best time for planting {crop}",
                "{crop} sowing season in Pakistan",
                "When should I plant {crop}?",
                "Optimum sowing time for {crop}",
                "What is the best season for {crop}?",
                "When is {crop} planted in Punjab?",
                "{crop} planting time in Sindh",
                "Which month to sow {crop}?",
                "What is the sowing window for {crop}?"
            ],
            "HarvestTime": [
                "When to harvest {crop}?",
                "{crop} harvesting time",
                "How to know {crop} is ready for harvest?",
                "When is {crop} harvested in Pakistan?",
                "Harvesting season for {crop}",
                "What is the maturity period of {crop}?",
                "How long does {crop} take to mature?",
                "When do farmers harvest {crop}?",
                "Signs of {crop} maturity",
                "{crop} picking time"
            ],
            "Soil": [
                "What type of soil is best for {crop}?",
                "Soil requirements for {crop}",
                "Which soil is suitable for {crop}?",
                "Ideal pH for {crop} cultivation",
                "How to prepare soil for {crop}?",
                "Best soil for {crop} in Pakistan",
                "Soil texture needed for {crop}",
                "How to improve soil for {crop}?",
                "What kind of soil does {crop} need?",
                "Land preparation for {crop}"
            ],
            "Irrigation": [
                "Water requirements for {crop}",
                "How many irrigations for {crop}?",
                "Irrigation schedule for {crop}",
                "Best irrigation method for {crop}",
                "How to irrigate {crop}?",
                "Water management in {crop}",
                "Drip irrigation for {crop}",
                "How much water does {crop} need?",
                "Critical stages for irrigation in {crop}",
                "Irrigation intervals for {crop}"
            ],
            "Fertilizer": [
                "Fertilizer recommendation for {crop}",
                "How much fertilizer for {crop} per acre?",
                "NPK ratio for {crop}",
                "Best fertilizer for {crop}",
                "Organic fertilizer for {crop}",
                "When to apply fertilizer to {crop}?",
                "Urea dose for {crop}",
                "DAP requirement for {crop}",
                "Zinc application in {crop}",
                "Fertilizer schedule for {crop}"
            ],
            "Pesticide": [
                "Common pests of {crop}",
                "How to control pests in {crop}?",
                "Pest management in {crop}",
                "Insecticides for {crop}",
                "Organic pest control for {crop}",
                "Whitefly control in {crop}",
                "Bollworm management in {crop}",
                "Aphid control in {crop}",
                "How to protect {crop} from insects?",
                "What pests attack {crop}?"
            ],
            "Diseases": [
                "Common diseases of {crop}",
                "How to control diseases in {crop}?",
                "Disease management in {crop}",
                "Fungicides for {crop} diseases",
                "Symptoms of {crop} diseases",
                "How to identify {crop} diseases?",
                "Prevention of {crop} diseases",
                "Rust disease in {crop}",
                "Blight in {crop}",
                "Viral diseases of {crop}"
            ],
            "Yield": [
                "Average yield of {crop} per acre",
                "How to increase {crop} yield?",
                "{crop} production in Pakistan",
                "What is the yield potential of {crop}?",
                "How much {crop} can I get per acre?",
                "Factors affecting {crop} yield",
                "High yielding varieties of {crop}",
                "Yield improvement techniques for {crop}",
                "Record yield of {crop} in Pakistan",
                "{crop} productivity"
            ],
            "Profit": [
                "Is {crop} cultivation profitable?",
                "Profit margin of {crop} farming",
                "Cost of cultivating {crop} per acre",
                "Economics of {crop} in Pakistan",
                "How much profit from {crop} per acre?",
                "ROI for {crop} farming",
                "Is {crop} a good cash crop?",
                "Break-even point for {crop}",
                "Government support for {crop}",
                "Subsidy on {crop} inputs"
            ],
            "Varieties": [
                "Popular varieties of {crop} in Pakistan",
                "Best high-yielding varieties of {crop}",
                "Hybrid varieties of {crop}",
                "Disease-resistant varieties of {crop}",
                "Which variety of {crop} is best?",
                "{crop} varieties for Punjab",
                "{crop} varieties for Sindh",
                "Recommended {crop} varieties",
                "New varieties of {crop}",
                "Bt varieties of {crop}"
            ],
            "Climate": [
                "Climate requirements for {crop}",
                "Temperature range for {crop}",
                "Best climate for {crop} cultivation",
                "Can {crop} grow in {region}?",
                "Effect of temperature on {crop}",
                "Ideal weather for {crop}",
                "Frost tolerance of {crop}",
                "Heat stress in {crop}"
            ],
            "Water": [
                "Water requirement of {crop}",
                "How much water does {crop} need?",
                "Drought tolerance of {crop}",
                "Water stress symptoms in {crop}",
                "Critical stages for water in {crop}",
                "Water use efficiency of {crop}",
                "Can {crop} survive with less water?"
            ],
            "Storage": [
                "How to store {crop} after harvest?",
                "Storage methods for {crop}",
                "Post-harvest management of {crop}",
                "How long can {crop} be stored?",
                "Storage pests of {crop}",
                "Moisture content for {crop} storage",
                "Cold storage for {crop}",
                "Grain storage tips for {crop}"
            ],
            "Intercropping": [
                "Companion plants for {crop}",
                "What to plant with {crop}?",
                "Intercropping systems with {crop}",
                "Best intercrop for {crop}",
                "Can I grow {crop1} with {crop2}?",
                "Mixed cropping with {crop}",
                "Crop rotation with {crop}",
                "What to grow after {crop}?"
            ],
            "Organic": [
                "How to grow organic {crop}?",
                "Organic farming for {crop}",
                "Organic fertilizers for {crop}",
                "Organic pest control for {crop}",
                "Certified organic {crop} production",
                "Natural farming methods for {crop}",
                "Vermicompost for {crop}",
                "Biofertilizers for {crop}"
            ],
            "SeedRate": [
                "Seed rate for {crop} per acre",
                "How much seed for {crop}?",
                "Seed quantity for {crop}",
                "Planting density for {crop}",
                "How many seeds per acre for {crop}?",
                "Seed requirement for {crop} cultivation",
                "Optimum seed rate for {crop}"
            ],
            "Spacing": [
                "Plant spacing for {crop}",
                "Row spacing for {crop}",
                "Plant population for {crop} per acre",
                "Distance between plants for {crop}",
                "How much space for {crop}?",
                "Bed size for {crop} cultivation",
                "Optimum spacing for {crop}"
            ],
            "Regions": [
                "Where is {crop} grown in Pakistan?",
                "Major {crop} producing areas in Pakistan",
                "Best region for {crop} cultivation",
                "Which province grows most {crop}?",
                "{crop} farming districts in Punjab",
                "{crop} cultivation areas in Sindh",
                "Can {crop} be grown in {region}?",
                "Top {crop} producing districts"
            ],
            "Government": [
                "Government support for {crop} farmers",
                "Subsidy on {crop} inputs",
                "Support price for {crop}",
                "Crop loan for {crop}",
                "Insurance schemes for {crop}",
                "Agriculture department schemes for {crop}",
                "Government programs for {crop} cultivation",
                "Subsidy on {crop} seeds",
                "Fertilizer subsidy for {crop}",
                "Irrigation subsidy for {crop}"
            ]
        }

        # ============ SOIL-SPECIFIC TEMPLATES (FIXED) ============
        self.soil_templates = [
            "Tell me about {soil} soil",
            "Characteristics of {soil} soil",
            "How to improve {soil} soil?",
            "Crops suitable for {soil} soil",
            "Problems with {soil} soil",
            "What is {soil} soil good for?",
            "How to manage {soil} soil?",
            "pH range of {soil} soil",
            "Water retention in {soil} soil",
            "Fertilizers for {soil} soil",
            "{soil} soil improvement methods",
            "Best crops for {soil} soil",
            "Where is {soil} soil found in Pakistan?",
            "Local name for {soil} soil",
            "Advantages and disadvantages of {soil} soil"
        ]

        # ============ REGIONS ============
        self.regions = ["Punjab", "Sindh", "KPK", "Balochistan", "Gilgit-Baltistan"]
        self.districts_pool = [
            "Sahiwal", "Faisalabad", "Multan", "Bahawalpur", "Rahim Yar Khan", "Okara", "Kasur", "Lahore",
            "Gujranwala", "Sialkot", "Sheikhupura", "Hafizabad", "Narowal", "Badin", "Thatta", "Hyderabad",
            "Sukkur", "Khairpur", "Mirpurkhas", "Sanghar", "Nawabshah", "Peshawar", "Mardan", "Swat",
            "Charsadda", "Abbottabad", "Quetta", "Kalat", "Mastung", "Khuzdar", "Turbat"
        ]

    def generate_answer(self, crop, intent, **kwargs):
        """Generate answer based on crop and intent"""
        crop_info = self.crops.get(crop, {})

        if not crop_info:
            return f"I don't have detailed information about {crop} in my database."

        crop_display = crop.title()

        if intent == "Cultivation":
            return f"""🌾 **{crop_display} CULTIVATION GUIDE - PAKISTAN** 🌾

**Season:** {crop_info.get('season', 'N/A')}
**Sowing Time:** {crop_info.get('sowing', 'N/A')}
**Harvest Time:** {crop_info.get('harvest', 'N/A')}
**Duration:** {crop_info.get('duration', 'N/A')}

**Soil Requirements:** {crop_info.get('soil', 'N/A')}, pH {crop_info.get('ph', 'N/A')}
**Temperature:** {crop_info.get('temp', 'N/A')}
**Water:** {crop_info.get('water', 'N/A')}

**Recommended Varieties:** {', '.join(crop_info.get('varieties', ['N/A'])[:5])}
**Fertilizer:** {crop_info.get('fertilizer', 'N/A')}
**Expected Yield:** {crop_info.get('yield', 'N/A')}
**Major Regions:** {', '.join(crop_info.get('regions', ['N/A']))}

For successful cultivation, ensure proper seed selection, timely operations, balanced nutrition, and integrated pest management."""

        elif intent == "SowingTime":
            return f"""📅 **{crop_display} SOWING TIME IN PAKISTAN** 📅

**Season:** {crop_info.get('season', 'N/A')}
**Sowing Window:** {crop_info.get('sowing', 'N/A')}
**Optimum Time:** {crop_info.get('sowing', 'N/A').split(',')[0] if ',' in crop_info.get('sowing', '') else crop_info.get('sowing', 'N/A')}

**Temperature Requirement:** {crop_info.get('temp', 'N/A')}

**Regional Variations:**
• Punjab: Within the recommended window
• Sindh: Slightly earlier/later depending on variety
• KPK: Follow local advisory

**Tip:** Timely sowing can increase yield by 20-30%. Avoid delay beyond the recommended window."""

        elif intent == "HarvestTime":
            return f"""📅 **{crop_display} HARVEST TIME IN PAKISTAN** 📅

**Harvest Period:** {crop_info.get('harvest', 'N/A')}
**Crop Duration:** {crop_info.get('duration', 'N/A')}

**Maturity Signs:**
• {self.get_maturity_signs(crop)}

**Harvesting Method:** 
• Small fields: Manual harvesting
• Large fields: Mechanical harvester/combine

**Moisture Content at Harvest:** 
• Grain crops: 20-25%
• For storage: Dry to 12-14% moisture

**Post-Harvest:** Clean, dry, and store in proper conditions to maintain quality."""

        elif intent == "Soil":
            return f"""🌱 **SOIL REQUIREMENTS FOR {crop_display.upper()}** 🌱

**Preferred Soil Type:** {crop_info.get('soil', 'Well-drained fertile soil')}
**Ideal pH Range:** {crop_info.get('ph', '6.0-7.5')}

**Soil Preparation:**
• Plough the field 2-3 times to achieve fine tilth
• Level the field for uniform irrigation
• Apply well-decomposed FYM 15-20 tons/acre during land preparation
• Ensure proper drainage

**Soil Testing:** Always conduct soil test before planting to determine nutrient status and pH. Collect samples from 10-15 spots per field from 0-6 inch depth."""

        elif intent == "Irrigation":
            return f"""💧 **IRRIGATION GUIDE FOR {crop_display.upper()}** 💧

**Water Requirement:** {crop_info.get('water', 'Moderate')}

**Critical Irrigation Stages:**
• {self.get_critical_stages(crop)}

**Recommended Methods:**
• Traditional: Flood/furrow irrigation
• Efficient: Drip irrigation (saves 30-50% water)
• Sprinkler: Suitable for light soils

**Irrigation Interval:**
• Summer: 7-10 days
• Winter: 10-15 days

**Government Subsidy:** 60-80% subsidy available on drip and sprinkler irrigation systems. Contact Agriculture Department."""

        elif intent == "Fertilizer":
            return f"""💊 **FERTILIZER RECOMMENDATION FOR {crop_display.upper()} (PER ACRE)** 💊

**Recommended Dose:** {crop_info.get('fertilizer', 'Based on soil test')}

**Application Schedule:**
• **Basal Dose (At Sowing):** Apply full DAP + MOP + 1/3 Urea
• **Vegetative Stage (25-30 days):** 1/3 Urea top dressing
• **Reproductive Stage (45-60 days):** 1/3 Urea top dressing

**Organic Option:**
• Farm Yard Manure: 15-20 tons/acre during land preparation
• Green manuring: Dhaincha, Sunn hemp

**Micronutrients (Soil Test Based):**
• Zinc: 10-15 kg/acre (Zinc Sulphate)
• Boron: 2-3 kg/acre (Borax)

**Tip:** Split nitrogen application increases efficiency by 30%."""

        elif intent == "Pesticide":
            pests = crop_info.get('pests', [])
            pest_list = '\n• '.join(pests[:4]) if pests else 'Varies by region and season'

            return f"""🐛 **PEST MANAGEMENT IN {crop_display.upper()}** 🐛

**Major Pests in Pakistan:**
• {pest_list}

**Integrated Pest Management (IPM) Strategies:**

🌱 **Cultural Control:**
• Use resistant varieties
• Optimal planting time
• Proper spacing
• Balanced fertilization
• Crop rotation

🦋 **Biological Control:**
• Release Trichogramma wasps for borers
• Ladybird beetles for aphids
• NPV for bollworms

⚙️ **Mechanical Control:**
• Pheromone traps
• Yellow sticky traps (for whitefly)
• Light traps

💊 **Chemical Control (Last Resort):**
• Use recommended pesticides at economic threshold level
• Rotate chemical groups to avoid resistance

**Organic Options:** Neem oil (5ml/L), garlic extract for light infestations."""

        elif intent == "Diseases":
            diseases = crop_info.get('diseases', [])
            disease_list = '\n• '.join(diseases[:4]) if diseases else 'Varies by region and season'

            return f"""🦠 **DISEASE MANAGEMENT IN {crop_display.upper()}** 🦠

**Common Diseases in Pakistan:**
• {disease_list}

**Preventive Measures:**
• Use disease-resistant varieties
• Treat seeds before sowing
• Practice crop rotation (2-3 years)
• Maintain field sanitation
• Avoid water stress

**Chemical Control:**
• Apply recommended fungicides at early stages
• Follow proper dosage and timing
• Rotate fungicides to avoid resistance

**Biological Control:**
• Trichoderma harzianum for soil-borne diseases
• Pseudomonas fluorescens

**Integrated Disease Management (IDM):** Combine resistant varieties, cultural practices, biological control, and need-based chemical application."""

        elif intent == "Yield":
            return f"""📊 **{crop_display.upper()} YIELD IN PAKISTAN** 📊

**Average Yield:** {crop_info.get('yield', 'Varies by variety and management')}

**Factors Affecting Yield:**
1. Variety selection - Use high-yielding certified seeds
2. Soil fertility - Balanced fertilization based on soil test
3. Water management - Timely irrigation at critical stages
4. Pest & disease control - Effective IPM implementation
5. Timely operations - Sowing, weeding, harvesting

**Yield Improvement Tips:**
• Conduct soil test and follow recommendations
• Use quality certified seed
• Maintain optimum plant population
• Practice integrated nutrient management
• Implement integrated pest management
• Adopt water-saving technologies"""

        elif intent == "Profit":
            return f"""💰 **ECONOMICS OF {crop_display.upper()} FARMING (PER ACRE)** 💰

**Cost of Cultivation:** {crop_info.get('profit', 'Rs. 40,000-60,000').split(',')[0] if 'Rs.' in crop_info.get('profit', '') else 'Rs. 40,000-60,000'}
**Expected Yield:** {crop_info.get('yield', 'Varies')}
**Expected Profit:** {crop_info.get('profit', 'Rs. 40,000-80,000')}

**Government Support:**
• Support price for wheat, sugarcane
• Subsidized fertilizers
• Crop loan at reduced interest rates
• Crop insurance schemes

**Profit Maximization Tips:**
1. Use high-yielding certified seeds
2. Follow recommended fertilizer schedule
3. Adopt water-saving technologies (60-80% subsidy)
4. Practice integrated pest management
5. Explore direct marketing channels"""

        elif intent == "Varieties":
            varieties = crop_info.get('varieties', [])
            variety_list = '\n• '.join(
                varieties) if varieties else 'Contact local agriculture department for recommended varieties'

            return f"""🌱 **{crop_display.upper()} VARIETIES IN PAKISTAN** 🌱

**Recommended Varieties:**
• {variety_list}

**Variety Selection Criteria:**
• **Yield potential:** Choose high-yielding varieties
• **Disease resistance:** Prefer varieties resistant to common diseases
• **Duration:** Select based on your cropping system
• **Region suitability:** Varieties recommended for your area
• **Market demand:** Popular varieties fetch better prices

**New Releases:** Check with your local agriculture extension officer for newly approved varieties."""

        elif intent == "Regions":
            regions = crop_info.get('regions', [])
            districts = crop_info.get('districts', [])

            return f"""📍 **{crop_display.upper()} GROWING REGIONS IN PAKISTAN** 📍

**Major Provinces:**
• {', '.join(regions) if regions else 'Punjab, Sindh'}

**Key Districts:**
• {', '.join(districts[:8]) if districts else 'Contact agriculture department for district-level information'}

**Best Regions:**
• {self.get_best_region(crop)}

**Climate Suitability:** {crop_display} thrives in {crop_info.get('temp', 'moderate')} temperature with {crop_info.get('water', 'adequate')} water availability."""

        elif intent == "Organic":
            return f"""🌿 **ORGANIC {crop_display.upper()} FARMING GUIDE** 🌿

**Soil Preparation:**
• Apply well-decomposed FYM (15-20 tons/acre)
• Green manuring with dhaincha/sunn hemp
• Vermicompost (2-3 tons/acre)

**Organic Nutrient Management:**
• Neem cake: 250-500 kg/acre
• Poultry manure: 4-5 tons/acre
• Bone meal: 100-200 kg/acre
• Biofertilizers: Rhizobium, Azotobacter, PSB

**Organic Pest Management:**
• Neem oil (5 ml/L water)
• Garlic-chili extract
• Yellow sticky traps
• Pheromone traps

**Certification Process:**
• Conversion period: 3 years
• No synthetic inputs during this period
• Apply to Organic Certification Body
• Maintain farm records
• Annual inspection required

**Market Premium:** Organic produce fetches 20-50% higher prices in export and niche domestic markets."""

        elif intent == "Government":
            return f"""🏛️ **GOVERNMENT SUPPORT FOR {crop_display.upper()} FARMERS** 🏛️

**Support Price/Marketing:**
• Wheat: Support price announced annually (Rs. 3,900/40kg)
• Sugarcane: Procurement zones, mill price
• Cotton: Minimum support price

**Subsidies:**
• **Fertilizers:** Subsidized DAP, Urea, Potash
• **Seeds:** Certified seed subsidy through PASSCO, Punjab Seed Corporation
• **Irrigation:** 60-80% subsidy on drip/sprinkler systems
• **Farm Machinery:** Subsidy on laser land levelers, bed planters, harvesters

**Crop Loans:**
• ZTBL, commercial banks offer agricultural credit
• Interest rate: 7-8% for crop loans
• Kissan Card scheme in Punjab

**How to Avail:**
1. Visit your nearest Agriculture Extension office
2. Contact Punjab/Sindh Agriculture Department
3. Apply through bank for crop loans
4. Register for subsidy schemes online

**Helpline:** Punjab Agriculture Department: 0800-15000"""

        else:
            return f"I have information about {crop_display}. What specific aspect would you like to know? (cultivation, sowing time, harvest, fertilizer, irrigation, pests, diseases, varieties, yield, profit, etc.)"

    def generate_soil_answer(self, soil):
        """Generate answer for soil-related questions"""
        soil_info = self.soils.get(soil, {})

        if not soil_info:
            return f"I don't have detailed information about {soil} soil."

        return f"""🌱 **{soil_info['name']} ({soil_info['local']}) - COMPLETE GUIDE** 🌱

**Characteristics:**
• Texture: {soil_info['texture']}
• Drainage: {soil_info['drainage']}
• Water Holding: {soil_info['water_holding']}
• Nutrient Status: {soil_info['nutrients']}
• pH Range: {soil_info['ph']}

**Improvement Methods:**
• {soil_info['improvement'][0]}
• {soil_info['improvement'][1]}
• {soil_info['improvement'][2]}
• {soil_info['improvement'][3] if len(soil_info['improvement']) > 3 else 'Regular soil testing'}

**Suitable Crops:**
• {', '.join(soil_info['crops'][:8])}

**Found in Pakistan:**
• {', '.join(soil_info['regions'])}

**Management Tips:**
• {'Drip irrigation recommended for water efficiency' if soil_info['water_holding'] == 'Poor' else 'Avoid over-irrigation to prevent waterlogging'}
• {'Apply organic matter regularly' if soil_info['nutrients'] == 'Low' else 'Maintain organic matter through crop residues'}
• {'Soil testing recommended every 2-3 years'}

**Local Name:** {soil_info['local']} (commonly called in rural areas)"""

    # Helper methods
    def get_maturity_signs(self, crop):
        signs = {
            "wheat": "Grains become hard, straw turns golden yellow, moisture content 20-25%",
            "rice": "80-85% grains turn golden, panicles bend downward",
            "cotton": "Bolls split open showing white lint",
            "sugarcane": "Leaves turn yellow, juice has maximum sucrose (20-22%)",
            "maize": "Husk turns brown, grains are hard with black layer at tip",
            "potato": "Haulms (vines) dry and yellow, skin set firmly",
            "tomato": "Color turns red (full ripe) or pink (for transport)",
            "onion": "50-70% tops fall over, necks dry",
            "chili": "Fruits turn red, firm texture"
        }
        return signs.get(crop,
                         "Crop reaches physiological maturity, leaves yellow, fruits/grains develop characteristic color/hardness")

    def get_critical_stages(self, crop):
        stages = {
            "wheat": "Crown root initiation (20-25 days), Tillering (45-50 days), Flowering (75-80 days), Grain filling (100-105 days)",
            "rice": "Tillering, Panicle initiation, Flowering, Grain filling",
            "cotton": "Flowering, Boll formation",
            "sugarcane": "Tillering, Grand growth, Maturity",
            "maize": "Knee-high stage, Tasseling, Silking, Grain filling",
            "potato": "Stolonization, Tuber initiation, Tuber bulking",
            "tomato": "Flowering, Fruit set, Fruit development"
        }
        return stages.get(crop, "Flowering and fruit/grain development stages")

    def get_best_region(self, crop):
        best = {
            "wheat": "Central Punjab (Sahiwal, Faisalabad, Multan) and Sindh (Ghazi, Tandojam)",
            "rice": "Punjab: Gujranwala, Sialkot for Basmati; Sindh: Badin, Thatta for Irri",
            "cotton": "Southern Punjab (Bahawalpur, Rahim Yar Khan) and Sindh (Sanghar, Nawabshah)",
            "sugarcane": "Central Punjab (Faisalabad, Jhang) and Sindh (Badin, Thatta)",
            "maize": "Sahiwal, Okara, Pakpattan in Punjab; Swat in KPK",
            "potato": "Sahiwal, Okara, Pakpattan in Punjab; Swat in KPK",
            "onion": "Sahiwal, Okara, Pakpattan in Punjab; Sukkur, Khairpur in Sindh",
            "chili": "Kunri, Umarkot in Sindh (Chili Capital of Asia)"
        }
        return best.get(crop, f"{crop.title()} is grown across Pakistan with suitable agro-climatic conditions")

    def generate_qa_pairs(self, target_count=10000):
        """Generate large-scale Q&A dataset"""
        print("=" * 70)
        print("🌾 GENERATING LARGE-SCALE PAKISTAN AGRICULTURE DATASET 🌾")
        print("=" * 70)

        dataset = []
        crops_list = list(self.crops.keys())

        # Calculate pairs per crop
        pairs_per_crop = target_count // len(crops_list)
        total_pairs = 0

        # Progress bar
        pbar = tqdm(total=target_count, desc="Generating Q&A pairs")

        # ============ GENERATE CROP Q&A ============
        for crop in crops_list:
            crop_info = self.crops[crop]

            # Generate for each intent
            for intent in self.intents:
                # Skip if intent not applicable
                if intent == "Intercropping" and crop not in ["maize", "cotton", "wheat"]:
                    continue

                # Get templates for this intent
                templates = self.templates.get(intent, [])
                if not templates:
                    continue

                # Generate variations
                for template in templates[:5]:  # Use first 5 templates per intent
                    try:
                        # Basic crop question
                        question = template.format(crop=crop)

                        # Add region variation (30% of questions)
                        if random.random() < 0.3:
                            region = random.choice(crop_info.get('regions', ['Punjab']))
                            question = question.replace(" in Pakistan?", f" in {region}?")
                            question = question.replace("Pakistan", region)

                        # Generate answer
                        answer = self.generate_answer(crop, intent)

                        # Add to dataset
                        dataset.append({
                            "id": f"{crop}_{intent}_{len(dataset)}",
                            "crop": crop,
                            "category": crop_info.get('category', 'general'),
                            "intent": intent,
                            "question": question,
                            "answer": answer,
                            "region": region if 'region' in locals() else random.choice(
                                crop_info.get('regions', ['Pakistan'])),
                            "soil": None,
                            "timestamp": datetime.now().isoformat()
                        })

                        total_pairs += 1
                        pbar.update(1)

                        if total_pairs >= target_count:
                            break

                    except Exception as e:
                        continue

                if total_pairs >= target_count:
                    break

            if total_pairs >= target_count:
                break

        # ============ GENERATE SOIL Q&A ============
        print("\n🌱 Generating soil management questions...")
        soil_pairs = len(dataset)

        for soil in self.soils:
            for template in self.soil_templates[:8]:  # Use first 8 soil templates
                try:
                    question = template.format(soil=soil)
                    answer = self.generate_soil_answer(soil)

                    dataset.append({
                        "id": f"soil_{soil}_{len(dataset)}",
                        "crop": None,
                        "soil": soil,
                        "category": "soil",
                        "intent": "Soil",
                        "question": question,
                        "answer": answer,
                        "region": random.choice(self.soils[soil]['regions']),
                        "timestamp": datetime.now().isoformat()
                    })

                    total_pairs += 1
                    pbar.update(1)

                except Exception as e:
                    continue

        print(f"✅ Added {len(dataset) - soil_pairs} soil Q&A pairs")

        # ============ GENERATE COMPARISON Q&A ============
        print("\n🔄 Generating crop comparison questions...")
        comparison_pairs = len(dataset)
        crop_pairs = list(itertools.combinations(crops_list[:15], 2))
        random.shuffle(crop_pairs)

        for crop1, crop2 in crop_pairs[:200]:  # Generate 200 comparisons
            try:
                question = f"What is the difference between {crop1} and {crop2}?"
                answer = f"""📊 **COMPARISON: {crop1.title()} vs {crop2.title()}** 📊

**Season:** {self.crops[crop1].get('season', 'N/A')} vs {self.crops[crop2].get('season', 'N/A')}
**Duration:** {self.crops[crop1].get('duration', 'N/A')} vs {self.crops[crop2].get('duration', 'N/A')}
**Water Requirement:** {self.crops[crop1].get('water', 'N/A')} vs {self.crops[crop2].get('water', 'N/A')}
**Soil Type:** {self.crops[crop1].get('soil', 'N/A')} vs {self.crops[crop2].get('soil', 'N/A')}
**Yield:** {self.crops[crop1].get('yield', 'N/A')} vs {self.crops[crop2].get('yield', 'N/A')}

**Choice depends on:**
• Your soil type and water availability
• Market demand in your area
• Your farming objectives and resources
• Rotation compatibility with other crops"""

                dataset.append({
                    "id": f"comparison_{crop1}_{crop2}_{len(dataset)}",
                    "crop1": crop1,
                    "crop2": crop2,
                    "category": "comparison",
                    "intent": "Comparison",
                    "question": question,
                    "answer": answer,
                    "timestamp": datetime.now().isoformat()
                })

                total_pairs += 1
                pbar.update(1)

            except Exception as e:
                continue

        print(f"✅ Added {len(dataset) - comparison_pairs} comparison Q&A pairs")

        pbar.close()
        return dataset

    def save_dataset(self, dataset, filename="data/pakistan_agriculture_dataset.json"):
        """Save dataset to JSON and CSV"""
        import os
        os.makedirs("data", exist_ok=True)

        # Save as JSON
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)

        # Save as CSV
        df = pd.DataFrame(dataset)
        csv_filename = filename.replace('.json', '.csv')
        df.to_csv(csv_filename, index=False, encoding='utf-8')

        print("\n" + "=" * 70)
        print(f"✅ DATASET GENERATION COMPLETE!")
        print("=" * 70)
        print(f"📁 JSON: {filename}")
        print(f"📁 CSV: {csv_filename}")
        print(f"📊 Total Q&A Pairs: {len(dataset):,}")

        # Statistics
        print("\n📈 DATASET STATISTICS:")

        # By category
        if 'category' in df.columns:
            print("\n📋 By Category:")
            cat_counts = df['category'].value_counts()
            for cat, count in cat_counts.items():
                print(f"   {cat}: {count:,} ({count / len(dataset) * 100:.1f}%)")

        # By intent
        if 'intent' in df.columns:
            print("\n🎯 By Intent:")
            intent_counts = df['intent'].value_counts().head(10)
            for intent, count in intent_counts.items():
                print(f"   {intent}: {count:,}")

        # Top crops
        if 'crop' in df.columns:
            crop_data = df[df['crop'].notna()]
            if len(crop_data) > 0:
                print("\n🌾 Top 10 Crops:")
                crop_counts = crop_data['crop'].value_counts().head(10)
                for crop, count in crop_counts.items():
                    print(f"   {crop}: {count:,}")

        return df


def main():
    """Generate the large-scale dataset"""
    generator = PakistanAgricultureDatasetGenerator()

    # Generate 10,000+ Q&A pairs
    dataset = generator.generate_qa_pairs(target_count=12000)

    # Save dataset
    generator.save_dataset(dataset)

    print("\n" + "=" * 70)
    print("🚀 READY FOR RAG IMPLEMENTATION!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Use this dataset with your RAG chatbot")
    print("2. Load the CSV file for semantic search")
    print("3. Connect with LLM for paraphrasing")
    print("4. Deploy your agriculture assistant!")


if __name__ == "__main__":
    main()