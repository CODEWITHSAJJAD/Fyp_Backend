# dataset_generator.py - Enhanced Pakistan Agriculture Dataset Generator
import json
import random
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime
import os


class AgricultureDatasetGenerator:
    def __init__(self):
        self.crop_types = {
            "wheat": {
                "season": ["rabi", "winter"],
                "soil": ["loamy", "clay loam", "alluvial", "well-drained"],
                "ph": ["6.0-7.5"],
                "temp": ["10-25°C"],
                "water": ["moderate", "450-650mm annually"],
                "regions": ["Punjab", "Sindh", "KPK", "Balochistan", "Gilgit-Baltistan"],
                "varieties": ["Sehar-2006", "Faisalabad-2008", "Galaxy-2013", "Inqalab-91", "Bhakkar-2002", "LASANI-2008", "Pakistan-2013"],
                "diseases": ["rust (yellow, brown, stem)", "loose smut", "powdery mildew", "septoria leaf blotch", "karnal bunt"],
                "pests": ["aphids", "armyworm", "termites", "pink borer", "wheat thrips"],
                "fertilizers": ["NPK 120:60:40", "urea", "DAP", "SSP", "zinc sulphate"],
                "duration": ["110-130 days"],
                "yield_per_acre": ["25-35 maunds", "3000-4000 kg"],
                "planting_time": ["November 15 - December 15"],
                "irrigation": ["3-4 irrigation", "crown root, tillering, booting, grain filling"],
                "harvest_time": ["April 15 - May 15"]
            },
            "rice": {
                "season": ["kharif"],
                "soil": ["clay", "clay loam", "alluvial", "water-retentive"],
                "ph": ["5.5-7.0"],
                "temp": ["20-35°C"],
                "water": ["high", "1200-2000mm"],
                "regions": ["Punjab", "Sindh"],
                "varieties": ["Super Basmati", "Basmati-385", "IRRI-6", "KS-282", "Kainat-2012", "Shaheen Basmati"],
                "diseases": ["blast", "bacterial blight", "sheath blight", "brown leaf spot"],
                "pests": ["stem borer", "brown plant hopper", "leaf folder", "gall midge"],
                "fertilizers": ["NPK 100:50:50", "urea", "MOP", "zinc sulphate"],
                "duration": ["90-150 days"],
                "yield_per_acre": ["40-60 maunds", "2500-3500 kg (Basmati)"],
                "planting_time": ["June 15 - July 30"],
                "irrigation": ["continuous flooding", "5-7cm water depth"],
                "harvest_time": ["October 15 - November 30"]
            },
            "maize": {
                "season": ["kharif", "spring"],
                "soil": ["well-drained loamy", "sandy loam", "alluvial"],
                "ph": ["5.8-7.5"],
                "temp": ["18-27°C"],
                "water": ["moderate", "500-800mm"],
                "regions": ["Punjab", "KPK", "Balochistan"],
                "varieties": ["Azam", "Jalal", "Pioneer hybrids", "NK hybrids", "30-B-90", "FH-1046"],
                "diseases": ["northern corn leaf blight", "stalk rot", "common rust", "gray leaf spot"],
                "pests": ["stem borer", "armyworm", "shoot fly", "cob borer"],
                "fertilizers": ["NPK 150:75:75", "urea", "SSP", "zinc sulphate"],
                "duration": ["90-110 days"],
                "yield_per_acre": ["60-100 maunds", "3500-5000 kg"],
                "planting_time": ["June 1 - July 15 (kharif)"],
                "irrigation": ["5-6 irrigation", "V6, V12, tasseling, silking stages critical"],
                "harvest_time": ["September 15 - October 30"]
            },
            "cotton": {
                "season": ["kharif"],
                "soil": ["well-drained loamy", "black soil", "alluvial"],
                "ph": ["6.0-8.0"],
                "temp": ["21-35°C"],
                "water": ["moderate", "600-1200mm"],
                "regions": ["Punjab", "Sindh"],
                "varieties": ["BT-121", "MNH-886", "CIM-602", "CIM-599", "CIM-496", "IR-NIBGE-3701"],
                "diseases": ["cotton leaf curl virus (CLCuV)", "bacterial blight", "verticillium wilt", "alternaria leaf spot"],
                "pests": ["bollworm", "whitefly", "aphids", "jassids", "thrips", "mealybug"],
                "fertilizers": ["NPK 80:40:40", "urea", "DAP", "zinc sulphate"],
                "duration": ["150-180 days"],
                "yield_per_acre": ["20-35 maunds lint", "800-1200 kg seed cotton"],
                "planting_time": ["April 15 - May 31"],
                "irrigation": ["6-8 irrigation", "30, 60, 90, 120 DAP critical"],
                "harvest_time": ["October 15 - December 31"]
            },
            "sugarcane": {
                "season": ["spring", "autumn"],
                "soil": ["deep fertile loamy", "well-drained alluvial", "black cotton soil"],
                "ph": ["6.5-7.5"],
                "temp": ["20-35°C"],
                "water": ["high", "1500-2500mm"],
                "regions": ["Punjab", "Sindh", "KPK"],
                "varieties": ["CPF-248", "CPF-247", "HSF-240", "S2006-US-633", "NIA-2012", "SAGRI-11"],
                "diseases": ["red rot", "whip smut", "rust", "mosaic virus", "sett rot"],
                "pests": ["top borer", "root borer", "scale insect", "whitefly"],
                "fertilizers": ["NPK 250:115:115", "urea", "DAP", "MOP", "farmyard manure"],
                "duration": ["10-16 months"],
                "yield_per_acre": ["600-800 maunds"],
                "planting_time": ["February 1 - March 31 (spring)"],
                "irrigation": ["10-15 irrigation", "monthly basis"],
                "harvest_time": ["November 15 - March 31"]
            },
            "gram (chickpea)": {
                "season": ["rabi"],
                "soil": ["sandy loam", "well-drained loamy"],
                "ph": ["6.0-8.0"],
                "temp": ["15-25°C"],
                "water": ["low", "300-500mm", "rainfed preferred"],
                "regions": ["Punjab", "Sindh", "Balochistan", "KPK"],
                "varieties": ["Desi (ICC-4958)", "Kabuli (BENA)", "Noor-91", "Thal-2006", "Punjab-2008", "Karak-1"],
                "diseases": ["ascochyta blight", "wilt", "botrytis gray mold", "powdery mildew"],
                "pests": ["pod borer", "cutworm", "aphids", "leaf miner"],
                "fertilizers": ["DAP 50-100 kg/acre", "organic manure", "NPK 20:40:0"],
                "duration": ["90-120 days"],
                "yield_per_acre": ["15-25 maunds", "600-1000 kg"],
                "planting_time": ["October 15 - November 30"],
                "irrigation": ["1-2 irrigation", "pre-flowering and pod filling"],
                "harvest_time": ["February 15 - March 31"]
            },
            "potato": {
                "season": ["rabi", "autumn"],
                "soil": ["sandy loam", "loamy sand", "well-drained"],
                "ph": ["5.5-6.5"],
                "temp": ["15-20°C"],
                "water": ["moderate", "500-700mm"],
                "regions": ["Punjab", "KPK (Hazara)", "Balochistan (Quetta)"],
                "varieties": ["Desiree", "Cardinal", "Sante", "Lady Rosetta", "Diamant", "Mona Lisa"],
                "diseases": ["late blight", "early blight", "bacterial wilt", "black scurf", "common scab"],
                "pests": ["potato tuber moth", "aphids", "white grub", "cutworms"],
                "fertilizers": ["NPK 200:100:100", "urea", "DAP", "MOP", "FYM 15-20 tons/acre"],
                "duration": ["90-120 days"],
                "yield_per_acre": ["200-300 maunds", "12000-18000 kg"],
                "planting_time": ["October 15 - November 30"],
                "irrigation": ["5-6 irrigation", "tuber initiation critical"],
                "harvest_time": ["January 15 - March 31"]
            },
            "tomato": {
                "season": ["rabi", "kharif"],
                "soil": ["sandy loam", "loamy", "well-drained"],
                "ph": ["6.0-6.8"],
                "temp": ["18-30°C"],
                "water": ["moderate", "400-600mm"],
                "regions": ["Punjab", "Sindh", "KPK", "Balochistan"],
                "varieties": ["Roma", "Money Maker", "Rio Grande", "NAB-500", "Punjab Chhuhara", "Hybrid varieties"],
                "diseases": ["early blight", "late blight", "tomato leaf curl virus (TLCV)", "bacterial wilt", "fusarium wilt"],
                "pests": ["whitefly (TLCV vector)", "fruit borer", "aphids", "thrips", "mites"],
                "fertilizers": ["NPK 120:60:60", "urea", "DAP", "MOP", "FYM 10-15 tons/acre"],
                "duration": ["70-90 days"],
                "yield_per_acre": ["150-250 maunds", "8000-15000 kg"],
                "planting_time": ["August 15 - September 30"],
                "irrigation": ["7-10 days interval", "flowering and fruit set critical"],
                "harvest_time": ["December 15 - February 15"]
            },
            "onion": {
                "season": ["rabi"],
                "soil": ["sandy loam", "loamy", "well-drained"],
                "ph": ["6.0-7.0"],
                "temp": ["13-24°C"],
                "water": ["moderate", "350-550mm"],
                "regions": ["Punjab", "Sindh", "Balochistan (Kalat)", "KPK"],
                "varieties": ["Phulkara", "Swat-1", "Sialkot Local", "Red Pinoy", "NAB-501"],
                "diseases": ["purple blotch", "downy mildew", "stemphylium leaf blight", "bacterial soft rot"],
                "pests": ["thrips", "onion fly", "cutworms", "maggots"],
                "fertilizers": ["NPK 100:50:50", "urea", "DAP", "FYM 15-20 tons/acre", "sulphur"],
                "duration": ["100-150 days"],
                "yield_per_acre": ["100-180 maunds", "5000-9000 kg"],
                "planting_time": ["September 15 - November 15"],
                "irrigation": ["8-10 irrigation", "bulb formation critical"],
                "harvest_time": ["March 15 - May 31"]
            },
            "sugarcane": {
                "season": ["spring", "autumn", "ratoon"],
                "soil": ["deep fertile loamy", "well-drained alluvial"],
                "ph": ["6.5-7.5"],
                "temp": ["20-35°C"],
                "water": ["high", "1500-2500mm"],
                "regions": ["Punjab", "Sindh", "KPK"],
                "varieties": ["CPF-248", "CPF-247", "HSF-240", "S2006-US-633", "NIA-2012"],
                "diseases": ["red rot", "whip smut", "rust", "mosaic virus"],
                "pests": ["top borer", "root borer", "scale insect"],
                "fertilizers": ["NPK 250:115:115", "urea", "DAP", "MOP"],
                "duration": ["10-16 months"],
                "yield_per_acre": ["600-800 maunds"],
                "planting_time": ["February 1 - March 31"],
                "irrigation": ["10-15 irrigation"],
                "harvest_time": ["November 15 - March 31"]
            },
            "mustard": {
                "season": ["rabi"],
                "soil": ["loamy", "sandy loam", "clay loam"],
                "ph": ["6.0-7.5"],
                "temp": ["10-25°C"],
                "water": ["low to moderate", "250-400mm"],
                "regions": ["Punjab", "Sindh", "KPK", "Balochistan"],
                "varieties": ["Raya Anmol", "Punjab Sarson", "Con-ola", "Hyola-401", "Rainbow"],
                "diseases": ["white rust", "downy mildew", "alternaria leaf spot", "stem rot"],
                "pests": ["aphids", "painted bug", "mustard sawfly", "leaf miner"],
                "fertilizers": ["NPK 60:40:40", "urea", "DAP", "sulphur (20-30 kg/acre)"],
                "duration": ["110-130 days"],
                "yield_per_acre": ["20-35 maunds", "900-1500 kg"],
                "planting_time": ["October 15 - November 30"],
                "irrigation": ["2-3 irrigation", "vegetative and pod filling stages"],
                "harvest_time": ["March 15 - April 15"]
            },
            "groundnut": {
                "season": ["kharif"],
                "soil": ["well-drained sandy loam", "loamy sand"],
                "ph": ["5.5-7.0"],
                "temp": ["25-30°C"],
                "water": ["moderate", "500-700mm"],
                "regions": ["Punjab", "Sindh", "KPK (Peshawar valley)"],
                "varieties": ["BARD-482", "Golden", "Jumber-95", "M-522", "Saini-2008"],
                "diseases": ["early leaf spot", "late leaf spot", "rust", "collar rot"],
                "pests": ["termites", "white grub", "leaf miner", "thrips"],
                "fertilizers": ["NPK 40:60:40", "DAP", "gypsum (200-300 kg/acre)", "boron"],
                "duration": ["120-140 days"],
                "yield_per_acre": ["25-40 maunds (pods)", "1000-1600 kg"],
                "planting_time": ["June 15 - July 15"],
                "irrigation": ["4-5 irrigation", "pegging and pod development critical"],
                "harvest_time": ["October 15 - November 30"]
            },
            "sunflower": {
                "season": ["rabi", "spring"],
                "soil": ["well-drained loamy", "sandy loam", "alluvial"],
                "ph": ["6.0-7.5"],
                "temp": ["20-30°C"],
                "water": ["moderate", "400-600mm"],
                "regions": ["Punjab", "Sindh", "KPK"],
                "varieties": ["Hysun-33", "Hysun-39", "SF-187", "S-278", "Parsun-2"],
                "diseases": ["downy mildew", "alternaria leaf spot", "powdery mildew", "charcoal rot"],
                "pests": ["head borer", "jassids", "thrips", "whitefly"],
                "fertilizers": ["NPK 60:40:20", "urea", "DAP", "boron", "zinc sulphate"],
                "duration": ["90-110 days"],
                "yield_per_acre": ["25-40 maunds", "1000-1500 kg"],
                "planting_time": ["March 1 - April 15"],
                "irrigation": ["4-5 irrigation", "head development and flowering critical"],
                "harvest_time": ["June 15 - July 15"]
            },
            "mungbean": {
                "season": ["kharif", "summer"],
                "soil": ["well-drained loamy", "sandy loam"],
                "ph": ["6.0-7.5"],
                "temp": ["25-35°C"],
                "water": ["moderate", "300-500mm"],
                "regions": ["Punjab", "Sindh", "KPK"],
                "varieties": ["NM-2011", "AZRI-mung-2006", "Punjab-2008", "Satharia", "MH-97-15"],
                "diseases": ["mungbean yellow mosaic virus (MYMV)", "powdery mildew", "leaf spot", "root rot"],
                "pests": ["whitefly (vector of MYMV)", "pod borer", "jassids", "thrips"],
                "fertilizers": ["NPK 20:40:20", "urea", "DAP", "zinc sulphate"],
                "duration": ["55-70 days"],
                "yield_per_acre": ["10-18 maunds", "400-700 kg"],
                "planting_time": ["June 15 - August 15"],
                "irrigation": ["2-3 irrigation", "flowering and pod filling critical"],
                "harvest_time": ["August 15 - October 15"]
            },
            "barley": {
                "season": ["rabi"],
                "soil": ["loamy", "clay loam", "alluvial"],
                "ph": ["6.0-8.0"],
                "temp": ["10-25°C"],
                "water": ["low to moderate", "350-500mm"],
                "regions": ["Punjab", "Sindh", "KPK", "Balochistan"],
                "varieties": ["Jau-95", "B-600", "Ac barley", "Haritaki"],
                "diseases": ["rust", "loose smut", "covered smut", "powdery mildew"],
                "pests": ["aphids", "armyworm", "termites", "cutworms"],
                "fertilizers": ["NPK 60:30:20", "urea", "DAP", "zinc sulphate"],
                "duration": ["90-110 days"],
                "yield_per_acre": ["20-35 maunds", "800-1400 kg"],
                "planting_time": ["November 1 - December 15"],
                "irrigation": ["2-3 irrigation", "tillering and grain filling"],
                "harvest_time": ["March 15 - April 30"]
            },
            "sorghum": {
                "season": ["kharif"],
                "soil": ["well-drained loamy", "sandy loam"],
                "ph": ["5.5-8.0"],
                "temp": ["25-35°C"],
                "water": ["moderate", "450-650mm"],
                "regions": ["Punjab", "Sindh", "KPK", "Balochistan"],
                "varieties": ["YSS-39", "SSG-59", "CSV-15", "SPV-1411", "BJ-278"],
                "diseases": ["anthracnose", "grain mold", "striga", "leaf blight"],
                "pests": ["stem borer", "shoot fly", "midge", "aphids"],
                "fertilizers": ["NPK 80:40:20", "urea", "DAP"],
                "duration": ["90-120 days"],
                "yield_per_acre": ["35-55 maunds", "1500-2500 kg"],
                "planting_time": ["June 15 - July 31"],
                "irrigation": ["3-4 irrigation", "flowering critical"],
                "harvest_time": ["September 15 - November 15"]
            },
            "millet": {
                "season": ["kharif"],
                "soil": ["sandy loam", "light textured"],
                "ph": ["5.5-7.5"],
                "temp": ["25-35°C"],
                "water": ["low", "300-450mm", "drought tolerant"],
                "regions": ["Punjab", "Sindh", "Balochistan"],
                "varieties": ["Bajra-2003", "ICMV-221", "ICMV-93934", "WCC-75"],
                "diseases": ["downy mildew", "ergot", "rust", "leaf spot"],
                "pests": ["shoot fly", "stem borer", "midge", "aphids"],
                "fertilizers": ["NPK 40:20:20", "urea", "DAP", "organic manure"],
                "duration": ["65-90 days"],
                "yield_per_acre": ["15-30 maunds", "600-1200 kg"],
                "planting_time": ["June 15 - July 31"],
                "irrigation": ["2-3 irrigation"],
                "harvest_time": ["September 15 - October 31"]
            },
            "cabbage": {
                "season": ["rabi"],
                "soil": ["loamy", "clay loam", "well-drained"],
                "ph": ["6.0-7.5"],
                "temp": ["15-20°C"],
                "water": ["moderate", "380-500mm"],
                "regions": ["Punjab", "KPK", "Balochistan (Quetta)"],
                "varieties": ["Golden Acre", "Copenhagen Market", "Punjab-2012", "NAB-505"],
                "diseases": ["black rot", "downy mildew", "club root", "alternaria leaf spot"],
                "pests": ["cabbage worm", "aphids", "diamondback moth", "cutworms"],
                "fertilizers": ["NPK 120:80:60", "urea", "DAP", "MOP", "FYM 15-20 tons/acre"],
                "duration": ["90-120 days"],
                "yield_per_acre": ["150-250 maunds", "8000-13000 kg"],
                "planting_time": ["October 1 - November 30"],
                "irrigation": ["7-10 days interval", "head formation critical"],
                "harvest_time": ["January 15 - March 31"]
            },
            "cauliflower": {
                "season": ["rabi"],
                "soil": ["loamy", "clay loam", "well-drained"],
                "ph": ["6.0-7.0"],
                "temp": ["15-20°C"],
                "water": ["moderate", "400-500mm"],
                "regions": ["Punjab", "KPK", "Balochistan (Quetta)"],
                "varieties": ["Snowball", "Early Kunwari", "Punjab-2013", "NAB-506"],
                "diseases": ["black rot", "club root", "downy mildew", "alternaria leaf spot"],
                "pests": ["diamondback moth", "cabbage worm", "aphids", "cutworms"],
                "fertilizers": ["NPK 100:60:60", "urea", "DAP", "MOK", "boron (foliar)"],
                "duration": ["90-120 days"],
                "yield_per_acre": ["120-200 maunds", "6000-10000 kg"],
                "planting_time": ["September 15 - November 15"],
                "irrigation": ["7-10 days interval", "curd formation critical"],
                "harvest_time": ["December 15 - February 28"]
            },
            "carrot": {
                "season": ["rabi"],
                "soil": ["sandy loam", "loamy sand", "deep loose"],
                "ph": ["6.0-7.0"],
                "temp": ["16-20°C"],
                "water": ["moderate", "350-450mm"],
                "regions": ["Punjab", "KPK", "Sindh"],
                "varieties": ["T-29", "Nantes", "Red Core", "Chantenay", "Punjab Black"],
                "diseases": ["leaf blight", "alternaria leaf spot", "powdery mildew", "root rot"],
                "pests": ["aphids", "carrot fly", "wireworms", "cutworms"],
                "fertilizers": ["NPK 60:40:40", "urea", "DAP", "MOK", "FYM 10-15 tons/acre"],
                "duration": ["90-110 days"],
                "yield_per_acre": ["80-150 maunds", "4000-7500 kg"],
                "planting_time": ["September 15 - November 30"],
                "irrigation": ["7-10 days interval", "root enlargement critical"],
                "harvest_time": ["December 15 - March 31"]
            },
            "spinach": {
                "season": ["rabi"],
                "soil": ["loamy", "sandy loam", "well-drained"],
                "ph": ["6.0-7.5"],
                "temp": ["15-20°C"],
                "water": ["moderate", "300-400mm"],
                "regions": ["All Pakistan"],
                "varieties": ["Local Green", "Punjab Green", "All Green"],
                "diseases": ["downy mildew", "powdery mildew", "alternaria leaf spot"],
                "pests": ["leaf miner", "aphids", "spider mites", "caterpillars"],
                "fertilizers": ["NPK 60:40:40", "urea", "DAP", "FYM 8-10 tons/acre"],
                "duration": ["30-45 days"],
                "yield_per_acre": ["40-70 maunds", "2000-3500 kg"],
                "planting_time": ["October 1 - December 31"],
                "irrigation": ["7-10 days interval"],
                "harvest_time": ["November 15 - March 31", "multiple cuttings possible"]
            },
            "okra": {
                "season": ["kharif"],
                "soil": ["loamy", "sandy loam", "well-drained"],
                "ph": ["6.0-7.5"],
                "temp": ["25-35°C"],
                "water": ["moderate", "400-500mm"],
                "regions": ["Punjab", "Sindh", "KPK"],
                "varieties": ["Sabz Pari", "Green Star", "Punjab-8", "NAB-504"],
                "diseases": ["yellow vein mosaic virus", "powdery mildew", "alternaria leaf spot"],
                "pests": ["jassids", "whitefly", "aphids", "fruit borer"],
                "fertilizers": ["NPK 80:40:40", "urea", "DAP", "FYM 8-10 tons/acre"],
                "duration": ["50-60 days"],
                "yield_per_acre": ["40-70 maunds", "2000-3500 kg"],
                "planting_time": ["June 15 - July 31"],
                "irrigation": ["7-10 days interval", "flowering and pod development critical"],
                "harvest_time": ["August 15 - October 15"]
            },
            "brinjal": {
                "season": ["kharif"],
                "soil": ["loamy", "sandy loam", "well-drained"],
                "ph": ["5.5-7.5"],
                "temp": ["22-30°C"],
                "water": ["moderate", "400-600mm"],
                "regions": ["Punjab", "Sindh", "KPK"],
                "varieties": ["Black Beauty", "Purple Long", "Faisalabad Long", "NAB-502"],
                "diseases": ["bacterial wilt", "phomopsis blight", "alternaria leaf spot", "verticillium wilt"],
                "pests": ["shoot borer", "whitefly", "aphids", "jassids"],
                "fertilizers": ["NPK 100:60:60", "urea", "DAP", "MOP", "FYM 10-15 tons/acre"],
                "duration": ["100-120 days"],
                "yield_per_acre": ["120-200 maunds", "6000-10000 kg"],
                "planting_time": ["June 15 - July 31"],
                "irrigation": ["7-10 days interval", "flowering and fruiting critical"],
                "harvest_time": ["September 30 - November 30"]
            },
            "chili": {
                "season": ["kharif"],
                "soil": ["sandy loam", "loamy", "well-drained"],
                "ph": ["6.0-7.0"],
                "temp": ["20-30°C"],
                "water": ["moderate", "400-600mm"],
                "regions": ["Punjab", "Sindh", "KPK"],
                "varieties": ["Longi", "Mirch-444", "NAB-503", "Kashmiri (for red)", "Dundicut"],
                "diseases": ["anthracnose", "leaf curl", "powdery mildew", "bacterial wilt"],
                "pests": ["thrips", "mites", "whitefly", "aphids", "fruit borer"],
                "fertilizers": ["NPK 120:60:60", "urea", "DAP", "MOP", "calcium nitrate"],
                "duration": ["90-120 days"],
                "yield_per_acre": ["30-50 maunds (green)", "15-25 maunds (dry red)"],
                "planting_time": ["June 1 - July 15"],
                "irrigation": ["7-10 days interval", "fruit development critical"],
                "harvest_time": ["September 15 - November 30"]
            },
            "watermelon": {
                "season": ["kharif"],
                "soil": ["sandy loam", "loamy sand", "well-drained"],
                "ph": ["6.0-7.5"],
                "temp": ["25-35°C"],
                "water": ["moderate", "400-600mm"],
                "regions": ["Punjab", "Sindh", "KPK", "Balochistan"],
                "varieties": ["Sugar Baby", "Crimson Sweet", "Charleston Gray", "Qasmi", "Gul-e-Bakht"],
                "diseases": ["fusarium wilt", "anthracnose", "alternaria leaf spot", "powdery mildew"],
                "pests": ["fruit fly", "aphids", "whitefly", "thrips"],
                "fertilizers": ["NPK 80:40:40", "urea", "DAP", "MOK", "FYM 10-15 tons/acre"],
                "duration": ["75-90 days"],
                "yield_per_acre": ["100-180 maunds", "5000-9000 kg"],
                "planting_time": ["April 15 - June 15"],
                "irrigation": ["5-7 irrigation", "flowering and fruit enlargement critical"],
                "harvest_time": ["July 15 - September 15"]
            },
            "mango": {
                "season": ["summer"],
                "soil": ["well-drained loamy", "sandy loam", "alluvial"],
                "ph": ["5.5-7.5"],
                "temp": ["25-40°C"],
                "water": ["moderate", "900-1100mm annually"],
                "regions": ["Punjab (Multan, Bahawalpur)", "Sindh", "KPK"],
                "varieties": ["Sindhri", "Langra", "Chaunsa", "Dusehri", "Anwar Ratole", "Saroli"],
                "diseases": ["anthracnose", "powdery mildew", "mango malformation", "die-back", "black tip"],
                "pests": ["mango mealybug", "fruit fly", "powdery mildew bug", "stem borer", "thrips"],
                "fertilizers": ["NPK 100:50:100", "urea", "DAP", "MOK", "FYM 20-30 kg/tree", "zinc, boron"],
                "duration": ["perennial", "4-6 years to bearing"],
                "yield_per_acre": ["40-100 maunds", "2000-5000 kg"],
                "planting_time": ["February 15 - March 31"],
                "irrigation": ["regular for young trees", "critical at flowering and fruit set"],
                "harvest_time": ["May 15 - August 31"]
            },
            "citrus": {
                "season": ["winter"],
                "soil": ["well-drained loamy", "sandy loam", "alluvial"],
                "ph": ["5.5-6.5"],
                "temp": ["13-35°C"],
                "water": ["moderate", "800-1200mm annually"],
                "regions": ["Punjab (Sahiwal, Sargodha)", "Sindh", "KPK"],
                "varieties": ["Kinnow", "Fasl-a", "Blood Red", "Succari", "Lemon (Lisbon, Eureka)"],
                "diseases": ["citrus canker", "huanglongbing (HLB)", "tristeza virus", "melanose", "root rot"],
                "pests": ["citrus psylla", "fruit fly", "whitefly", "scale insects", "mites"],
                "fertilizers": ["NPK 200:100:100", "urea", "DAP", "MOK", "FYM 20-30 kg/tree", "iron, zinc"],
                "duration": ["perennial", "3-4 years to bearing"],
                "yield_per_acre": ["80-150 maunds", "4000-7500 kg"],
                "planting_time": ["February 15 - March 31"],
                "irrigation": ["regular", "weekly in dry season"],
                "harvest_time": ["November 15 - March 31"]
            },
            "banana": {
                "season": ["year-round"],
                "soil": ["deep loamy", "alluvial", "well-drained"],
                "ph": ["6.0-7.0"],
                "temp": ["25-30°C"],
                "water": ["high", "1200-2200mm annually"],
                "regions": ["Sindh (lower)", "Punjab (Multan)", "KPK"],
                "varieties": ["Cavendish (Dwarf, Giant)", "Basrai", "Monte Carlo", "Williams"],
                "diseases": ["banana bunchy top virus (BBTV)", "panama disease", "sigatoka leaf spot", "bacterial wilt"],
                "pests": ["banana weevil", "aphids", "nematodes", "fruit scarring beetle"],
                "fertilizers": ["NPK 200:100:200", "urea", "DAP", "MOK", "FYM 10-15 kg/plant"],
                "duration": ["10-15 months"],
                "yield_per_acre": ["150-250 dozens", "18000-30000 kg"],
                "planting_time": ["March 15 - May 31"],
                "irrigation": ["regular", "weekly in dry season"],
                "harvest_time": ["year-round"]
            },
            "apple": {
                "season": ["autumn"],
                "soil": ["well-drained loamy", "sandy loam", "mountain soil"],
                "ph": ["5.5-7.0"],
                "temp": ["15-28°C"],
                "water": ["moderate", "800-1200mm annually"],
                "regions": ["KPK (Swat, Hazara)", "Gilgit-Baltistan", "Balochistan (Quetta)"],
                "varieties": ["Kashmiri (Delicious)", "Red Delicious", "Golden Delicious", "Gala", "Fuji"],
                "diseases": ["apple scab", "powdery mildew", "fire blight", "canker", "alternaria leaf spot"],
                "pests": ["codling moth", "apple maggot", "aphids", "scale insects", "mites"],
                "fertilizers": ["NPK 150:75:75", "urea", "DAP", "MOK", "FYM 15-20 kg/tree", "zinc, boron"],
                "duration": ["perennial", "4-5 years to bearing"],
                "yield_per_acre": ["80-150 maunds", "4000-7500 kg"],
                "planting_time": ["December 15 - February 28"],
                "irrigation": ["regular", "critical at flowering and fruit development"],
                "harvest_time": ["July 15 - October 15"]
            },
            "date palm": {
                "season": ["summer"],
                "soil": ["well-drained sandy", "loamy", "saline tolerant"],
                "ph": ["7.0-9.0"],
                "temp": ["25-40°C"],
                "water": ["low to moderate", "600-800mm annually"],
                "regions": ["Balochistan (Makran)", "Sindh (Thar)", "Punjab (south)"],
                "varieties": ["Aseel", "Begum Jangi", "Khadrawi", "Zahidi", "Medjool", "Halawi"],
                "diseases": ["date palm decline", "bayoud disease", "black scorch", "leaf spot"],
                "pests": ["red palm weevil", "date palm scale", "sap beetle", "carob moth"],
                "fertilizers": ["NPK 50:30:50", "urea", "DAP", "MOK", "FYM 15-20 kg/tree", "boron, zinc"],
                "duration": ["perennial", "4-6 years to bearing"],
                "yield_per_acre": ["40-80 maunds", "2000-4000 kg"],
                "planting_time": ["February 15 - April 30"],
                "irrigation": ["regular", "deep irrigation"],
                "harvest_time": ["July 15 - October 31"]
            }
        }

        self.soil_types = {
            "sandy": {
                "texture": "coarse",
                "drainage": "excellent",
                "nutrients": "low to medium",
                "water_holding": "poor",
                "ph": ["6.0-8.0"],
                "suitable_crops": ["groundnut", "watermelon", "carrot", "potato", "sunflower", "millet", "sorghum", "onion", "tomato"],
                "improvement": ["add organic matter", "use mulch", "frequent irrigation", "green manure", "clay addition"],
                "problems": ["nutrient leaching", "dries quickly", "low fertility", "erosion prone"]
            },
            "clay": {
                "texture": "fine",
                "drainage": "poor to moderate",
                "nutrients": "high",
                "water_holding": "excellent",
                "ph": ["5.5-7.5"],
                "suitable_crops": ["rice", "wheat", "sugarcane", "cotton", "soybean", "cabbage", "spinach"],
                "improvement": ["add sand or coarse organic matter", "gypsum application", "deep ploughing", "add lime"],
                "problems": ["compaction", "poor aeration", "slow drainage", "waterlogging"]
            },
            "loamy": {
                "texture": "medium",
                "drainage": "good",
                "nutrients": "moderate to high",
                "water_holding": "good",
                "ph": ["6.0-7.5"],
                "suitable_crops": ["most crops", "vegetables", "fruits", "cereals", "pulses", "oilseeds", "cotton"],
                "improvement": ["maintain organic content", "practice crop rotation", "balanced fertilization"],
                "problems": ["erosion if not managed", "requires regular organic addition"]
            },
            "sandy loam": {
                "texture": "medium coarse",
                "drainage": "good to excellent",
                "nutrients": "low to moderate",
                "water_holding": "moderate",
                "ph": ["6.0-7.5"],
                "suitable_crops": ["maize", "cotton", "tomato", "onion", "potato", "groundnut", "sunflower"],
                "improvement": ["add organic matter", "frequent irrigation", "mulching", "green manure"],
                "problems": ["nutrient leaching", "requires more fertilizer"]
            },
            "clay loam": {
                "texture": "medium fine",
                "drainage": "moderate",
                "nutrients": "moderate to high",
                "water_holding": "good to high",
                "ph": ["6.0-7.5"],
                "suitable_crops": ["wheat", "rice", "cotton", "sugarcane", "pulses", "vegetables"],
                "improvement": ["organic matter addition", "gypsum if sodic", "proper drainage"],
                "problems": ["compaction", "slow drainage", "difficult tilth"]
            },
            "alluvial": {
                "texture": "variable",
                "drainage": "good",
                "nutrients": "high",
                "water_holding": "variable",
                "ph": ["6.0-8.0"],
                "suitable_crops": ["rice", "wheat", "sugarcane", "cotton", "vegetables", "fruits"],
                "improvement": ["maintain organic matter", "proper drainage", "balanced fertilization"],
                "problems": ["flooding risk", "erosion", "possible salinity", "nutrient depletion"]
            },
            "black": {
                "texture": "clayey",
                "drainage": "poor when wet",
                "nutrients": "high in calcium/magnesium",
                "water_holding": "good",
                "ph": ["7.0-8.5"],
                "suitable_crops": ["cotton", "sugarcane", "wheat", "sorghum", "citrus", "pomegranate"],
                "improvement": ["add organic matter", "contour bunding", "subsoiling", "gypsum"],
                "problems": ["cracks when dry", "hard to work when wet", "alkaline nature"]
            },
            "red": {
                "texture": "sandy loam to loamy",
                "drainage": "good",
                "nutrients": "low in organic matter",
                "water_holding": "moderate",
                "ph": ["5.5-6.5"],
                "suitable_crops": ["groundnut", "rice (upland)", "millets", "pigeon pea", "sweet potato", "cassava"],
                "improvement": ["add organic matter", "apply phosphate fertilizers", "lime if acidic", "grow legumes"],
                "problems": ["low fertility", "erosion prone on slopes", "acidic nature", "phosphorus fixation"]
            },
            "mountain": {
                "texture": "variable, often stony",
                "drainage": "excessive",
                "nutrients": "variable",
                "water_holding": "poor",
                "ph": ["5.5-7.5"],
                "suitable_crops": ["maize", "wheat", "potato", "apple", "peach", "plum", "pear", "apricot"],
                "improvement": ["terracing", "contour farming", "add organic matter", "rock phosphate"],
                "problems": ["erosion", "steep slopes", "shallow depth", "leaching"]
            },
            "desert": {
                "texture": "sandy",
                "drainage": "excessive",
                "nutrients": "very low",
                "water_holding": "very poor",
                "ph": ["7.0-9.0"],
                "suitable_crops": ["millet", "sorghum", "pearl millet", "cluster bean", "date palm"],
                "improvement": ["add organic matter", "water harvesting", "mulching", "windbreaks"],
                "problems": ["aridity", "sand movement", "very low fertility", "salinity", "extreme temperatures"]
            }
        }

        self.question_templates = {
            "crop_general": [
                "How do I grow {crop} in Pakistan?",
                "What are the requirements for {crop} cultivation?",
                "Tell me about {crop} farming practices in Pakistan.",
                "Best practices for {crop} cultivation?",
                "{crop} cultivation guide for Pakistani farmers",
                "How to cultivate {crop} successfully?",
                "Complete guide to growing {crop} in Pakistan?"
            ],
            "crop_specific": [
                "What soil is best for {crop} in Pakistan?",
                "Ideal temperature for {crop} cultivation?",
                "Water requirements for {crop} in Pakistan?",
                "Common diseases of {crop} and their control?",
                "Pests affecting {crop} and management?",
                "Which season is best for {crop} in Pakistan?",
                "Popular varieties of {crop} recommended for Pakistan?",
                "Fertilizer recommendation for {crop}?",
                "How long does {crop} take to grow?",
                "In which regions of Pakistan is {crop} grown?",
                "How to increase {crop} yield per acre?",
                "What is the ideal pH for {crop} soil?",
                "Best time to plant {crop} in Pakistan?",
                "How much seed rate for {crop} per acre?",
                "What is the expected yield of {crop} per acre?"
            ],
            "soil_general": [
                "Tell me about {soil} soil characteristics",
                "Properties of {soil} soil for agriculture",
                "How to improve {soil} soil?",
                "Crops suitable for {soil} soil in Pakistan",
                "Problems with {soil} soil and solutions",
                "What is {soil} soil good for?",
                "How to manage {soil} soil effectively?",
                "pH range and management of {soil} soil",
                "Water retention capabilities of {soil} soil"
            ],
            "comparison_crop": [
                "Difference between {crop1} and {crop2} cultivation in Pakistan",
                "Which is better: {crop1} or {crop2}?",
                "Compare {crop1} and {crop2} water requirements",
                "{crop1} vs {crop2}: which is more profitable?",
                "Should I grow {crop1} or {crop2}?",
                "{crop1} vs {crop2}: yield comparison per acre"
            ],
            "comparison_soil": [
                "Difference between {soil1} and {soil2} soil",
                "Compare {soil1} and {soil2} soils for agriculture",
                "Which is better: {soil1} or {soil2} soil?",
                "{soil1} vs {soil2}: which has better drainage?",
                "Water holding capacity comparison: {soil1} vs {soil2}"
            ],
            "practical": [
                "How to test soil quality at home?",
                "When to harvest {crop} for maximum yield?",
                "How much fertilizer for {crop} per acre?",
                "Organic farming methods for {crop} cultivation",
                "How to prepare land for {crop} cultivation?",
                "Best irrigation methods for {crop} in Pakistan",
                "How to store {crop} after harvest?",
                "Cost of cultivating {crop} per acre in Pakistan",
                "How to control pests in {crop} organically?",
                "Integrated pest management for {crop}",
                "Crop rotation benefits for {crop} farming",
                "How to prepare compost for agricultural use?"
            ],
            "pakistan_specific": [
                "What are the major crops grown in Pakistan?",
                "Which crops are suitable for Punjab's climate?",
                "Best crops for Sindh's hot and humid climate?",
                "Agriculture challenges in Balochistan?",
                "Crop suggestions for KPK's mountainous terrain?",
                "Rice cultivation in Pakistan - complete guide?",
                "Wheat production in Pakistan - best practices?",
                "What are the Rabi crops in Pakistan?",
                "What are the Kharif crops in Pakistan?"
            ]
        }

    def generate_crop_answer(self, crop: str, question_type: str) -> str:
        crop_info = self.crop_types.get(crop.lower(), {})
        if not crop_info:
            return f"I don't have specific information about {crop}. Please ask about major crops like wheat, rice, maize, cotton, sugarcane, or vegetables."

        q_lower = question_type.lower()
        
        if "soil" in q_lower:
            soil_list = ', '.join(crop_info.get('soil', ['well-drained soil']))
            ph = ', '.join(crop_info.get('ph', ['6.0-7.5']))
            return f"🌱 {crop.title()} SOIL REQUIREMENTS IN PAKISTAN\n\nBest Soil Type: {soil_list}\nIdeal pH Range: {ph}\n\nSoil Preparation Tips:\n• Ensure proper drainage\n• Add organic matter (FYM/compost) 10-15 tons/acre\n• Perform deep ploughing 2-3 weeks before planting\n• Level the field properly\n• Conduct soil test before preparation"
        
        elif "disease" in q_lower:
            diseases = crop_info.get('diseases', ['Various diseases'])
            return f"🦠 COMMON DISEASES OF {crop.upper()}\n\nMajor Diseases:\n• {', '.join(diseases)}\n\nPrevention and Control:\n1. Use certified seeds\n2. Practice crop rotation (3-4 years)\n3. Maintain field hygiene\n4. Remove infected plant debris\n5. Use resistant varieties\n6. Apply fungicides as recommended\n7. Monitor fields regularly"
        
        elif "pest" in q_lower:
            pests = crop_info.get('pests', ['Various pests'])
            return f"🐛 MAJOR PESTS OF {crop.upper()}\n\nKey Pests:\n• {', '.join(pests)}\n\nIPM Strategies:\n1. Regular monitoring and scouting\n2. Use pest-resistant varieties\n3. Install traps (pheromone, yellow sticky)\n4. Conserve natural enemies\n5. Apply pesticides only when threshold reached\n6. Follow pre-harvest interval"
        
        elif "season" in q_lower or "time" in q_lower or "planting" in q_lower:
            seasons = ', '.join(crop_info.get('season', ['Depends on region']))
            planting = ', '.join(crop_info.get('planting_time', ['Varies']))
            regions = ', '.join(crop_info.get('regions', ['All regions']))
            return f"📅 SEASON AND PLANTING FOR {crop.upper()}\n\nGrowing Seasons: {seasons}\nOptimal Planting Time: {planting}\nMajor Growing Regions: {regions}\nDuration to Harvest: {', '.join(crop_info.get('duration', ['110-130 days']))}"
        
        elif "variety" in q_lower or "seed" in q_lower:
            varieties = ', '.join(crop_info.get('varieties', ['Available varieties']))
            return f"🌾 RECOMMENDED VARIETIES OF {crop.upper()}\n\nPopular Varieties:\n• {varieties}\n\nSeed Guidelines:\n1. Purchase certified seeds\n2. Select varieties for your region\n3. Check germination rate (>85%)\n4. Use disease-free seeds"
        
        elif "fertilizer" in q_lower:
            fertilizers = ', '.join(crop_info.get('fertilizers', ['NPK']))
            return f"💊 FERTILIZER FOR {crop.upper()}\n\nRecommended Fertilizers:\n• {fertilizers}\n\nApplication:\n1. Soil test for precise recommendation\n2. Basal: At planting time\n3. Top-dressing: Split applications\n4. Avoid excessive nitrogen\n5. Include micronutrients if deficient"
        
        elif "water" in q_lower or "irrigation" in q_lower:
            water = crop_info.get('water', ['Moderate'])
            irrigation = crop_info.get('irrigation', ['Regular'])
            return f"💧 WATER REQUIREMENTS FOR {crop.upper()}\n\nWater Need: {', '.join(water)}\nCritical Stages: {', '.join(irrigation)}\n\nTips:\n1. Apply first irrigation after sowing\n2. Maintain optimal soil moisture\n3. Avoid water stress at critical stages\n4. Ensure good drainage\n5. Use drip/sprinkler for efficiency"
        
        elif "yield" in q_lower or "production" in q_lower:
            yield_per = ', '.join(crop_info.get('yield_per_acre', ['Variable']))
            varieties = ', '.join(crop_info.get('varieties', ['High-yielding'])[:2])
            return f"📈 YIELD IMPROVEMENT FOR {crop.upper()}\n\nAverage Yield Potential: {yield_per}\n\nStrategies:\n1. Use high-yielding varieties: {varieties}\n2. Follow recommended practices\n3. Timely sowing\n4. Balanced fertilization\n5. Adequate irrigation\n6. IPM implementation\n7. Proper spacing\n8. Crop rotation"
        
        elif "harvest" in q_lower:
            harvest = crop_info.get('harvest_time', ['Varies'])
            return f"🌾 HARVESTING {crop.upper()}\n\nHarvest Time: {', '.join(harvest)}\n\nSigns:\n• Color change\n• Hardness of grains/fruits\n• Moisture content (12-14% for grains)\n\nMethods:\n• Manual: Small areas\n• Mechanical: Large scale\n\nPost-Harvest:\n• Dry to safe moisture\n• Clean and grade\n• Proper storage"
        
        elif "cost" in q_lower or "profit" in q_lower:
            return f"💰 ECONOMICS OF {crop.upper()} FARMING\n\nEstimated Costs per Acre:\n• Land Preparation: PKR 5,000-8,000\n• Seeds: PKR {random.randint(2000, 5000)}\n• Fertilizers: PKR {random.randint(3000, 6000)}\n• Pesticides: PKR {random.randint(1500, 4000)}\n• Irrigation: PKR {random.randint(2000, 4000)}\n• Labor: PKR {random.randint(5000, 10000)}\n• Total: PKR {random.randint(20000, 35000)}\n\nExpected Returns:\n• Yield: {', '.join(crop_info.get('yield_per_acre', ['Variable']))}\n• Net Profit: PKR {random.randint(15000, 50000)}/acre"
        
        elif "region" in q_lower or "where" in q_lower:
            regions = ', '.join(crop_info.get('regions', ['Suitable']))
            return f"📍 SUITABLE REGIONS FOR {crop.upper()}\n\nMajor Growing Areas:\n• {regions}\n\nFor specific recommendations, contact:\n• Provincial Agriculture Departments\n• District Agriculture Extension Offices\n• Nearest Research Station"
        
        else:
            varieties = ', '.join(crop_info.get('varieties', ['Recommended'])[:4])
            seasons = ', '.join(crop_info.get('season', ['Season']))
            soil = ', '.join(crop_info.get('soil', ['Soil'])[:2])
            water = ', '.join(crop_info.get('water', ['Moderate']))
            yield_range = ', '.join(crop_info.get('yield_per_acre', ['Variable']))
            regions = ', '.join(crop_info.get('regions', ['Regions'])[:2])
            
            return f"🌾 COMPLETE GUIDE: {crop.upper()} IN PAKISTAN\n\n📅 Season: {seasons}\n🌱 Soil: {soil}\n🌡️ Temperature: {', '.join(crop_info.get('temp', ['15-25°C']))}\n💧 Water: {water}\n📍 Regions: {regions}\n\n🎯 Varieties: {varieties}\n💊 Fertilizer: {', '.join(crop_info.get('fertilizers', ['NPK'])[:2])}\n🐛 Pests: {', '.join(crop_info.get('pests', ['Pests'])[:2])}\n🦠 Diseases: {', '.join(crop_info.get('diseases', ['Diseases'])[:2])}\n📈 Yield: {yield_range}\n\n⏱️ Duration: {', '.join(crop_info.get('duration', ['Days']))}\n🌾 Harvest: {', '.join(crop_info.get('harvest_time', ['Time']))}\n\nKey Tips:\n1. Certified seeds\n2. Soil preparation\n3. Balanced fertilization\n4. IPM practices\n5. Timely irrigation"
    
    def generate_soil_answer(self, soil: str, question_type: str) -> str:
        soil_info = self.soil_types.get(soil.lower(), {})
        if not soil_info:
            soil_list = ', '.join(self.soil_types.keys())
            return f"I don't have detailed info about {soil}. Common soils: {soil_list}."

        q_lower = question_type.lower()
        
        if "improve" in q_lower:
            improvement = soil_info.get('improvement', ['Methods'])[:3]
            problems = soil_info.get('problems', ['Issues'])[:2]
            return f"🔧 IMPROVE {soil.upper()} SOIL\n\nProperties:\n• Texture: {soil_info['texture']}\n• Drainage: {soil_info['drainage']}\n• Water Holding: {soil_info['water_holding']}\n• pH: {', '.join(soil_info.get('ph', ['6.0-8.0']))}\n\nImprovement Methods:\n1. {improvement[0]}\n2. {improvement[1] if len(improvement) > 1 else improvement[0]}\n3. {improvement[2] if len(improvement) > 2 else 'Regular testing'}\n\nProblems Addressed: {', '.join(problems)}"
        
        elif "crop" in q_lower or "suitable" in q_lower:
            crops = ', '.join(soil_info.get('suitable_crops', ['Various'])[:6])
            return f"🌱 CROPS FOR {soil.upper()} SOIL\n\nSoil Properties:\n• Texture: {soil_info['texture']}\n• Drainage: {soil_info['drainage']}\n• Water Holding: {soil_info['water_holding']}\n• Nutrients: {soil_info['nutrients']}\n\nRecommended Crops:\n• {crops}\n\nTips:\n• Match crops to water-holding capacity\n• Consider pH tolerance\n• Plan for soil improvement"
        
        elif "water" in q_lower or "drainage" in q_lower:
            return f"💧 WATER IN {soil.upper()} SOIL\n\nProperties:\n• Water Holding: {soil_info['water_holding']}\n• Drainage: {soil_info['drainage']}\n• Texture: {soil_info['texture']}\n\nManagement:\n• Irrigation Frequency: {'High' if soil_info['water_holding'] == 'poor' else 'Moderate'}\n• Mulching: {'Essential' if soil_info['water_holding'] == 'poor' else 'Recommended'}\n• Best Method: {'Drip/sprinkler' if soil_info['water_holding'] == 'poor' else 'Any efficient method'}"
        
        elif "ph" in q_lower:
            return f"⚗️ pH OF {soil.upper()} SOIL\n\nTypical pH: {', '.join(soil_info.get('ph', ['6.0-8.0']))}\nTexture: {soil_info['texture']}\n\nMost crops prefer pH 6.0-7.5\nTest soil regularly\nApply amendments as needed"
        
        else:
            texture = soil_info['texture']
            drainage = soil_info['drainage']
            nutrients = soil_info['nutrients']
            water_holding = soil_info['water_holding']
            ph = ', '.join(soil_info.get('ph', ['6.0-8.0']))
            suitable = ', '.join(soil_info.get('suitable_crops', ['Various'])[:4])
            problems = ', '.join(soil_info.get('problems', ['Various'])[:2])
            
            return f"🌍 {soil.upper()} SOIL PROFILE\n\n📊 Properties:\n• Texture: {texture}\n• Drainage: {drainage}\n• Nutrients: {nutrients}\n• Water Holding: {water_holding}\n• pH: {ph}\n\n🌱 Suitable Crops:\n• {suitable}\n\n⚠️ Challenges:\n• {problems}\n\n🔧 Management:\n• Add organic matter\n• Proper drainage\n• Balanced fertilization"

    def generate_comparison_answer(self, item1: str, item2: str, is_soil: bool = False) -> str:
        if is_soil:
            info1 = self.soil_types.get(item1.lower(), {})
            info2 = self.soil_types.get(item2.lower(), {})
            
            if not info1 or not info2:
                return f"I can compare: {', '.join(self.soil_types.keys())}"
            
            return f"📊 COMPARISON: {item1.upper()} vs {item2.upper()} SOIL\n\n┌─────────────┬────────────────┬────────────────┐\n│ Property    │ {item1.title():<14} │ {item2.title():<14} │\n├─────────────┼────────────────┼────────────────┤\n│ Texture     │ {info1.get('texture', 'N/A'):<14} │ {info2.get('texture', 'N/A'):<14} │\n│ Drainage    │ {info1.get('drainage', 'N/A'):<14} │ {info2.get('drainage', 'N/A'):<14} │\n│ Water Hold  │ {info1.get('water_holding', 'N/A'):<14} │ {info2.get('water_holding', 'N/A'):<14} │\n│ Nutrients   │ {info1.get('nutrients', 'N/A'):<14} │ {info2.get('nutrients', 'N/A'):<14} │\n└─────────────┴────────────────┴────────────────┘\n\n{item1.title()} crops: {', '.join(info1.get('suitable_crops', [])[:3])}\n{item2.title()} crops: {', '.join(info2.get('suitable_crops', [])[:3])}"
        
        else:
            info1 = self.crop_types.get(item1.lower(), {})
            info2 = self.crop_types.get(item2.lower(), {})
            
            if not info1 or not info2:
                return f"I can compare major crops. Please ask about: {', '.join(self.crop_types.keys())[:80]}..."
            
            return f"🌾 COMPARISON: {item1.upper()} vs {item2.upper()}\n\n┌──────────────┬────────────────────┬────────────────────┐\n│ Attribute    │ {item1.title():<18} │ {item2.title():<18} │\n├──────────────┼────────────────────┼────────────────────┤\n│ Season       │ {info1.get('season', ['N/A'])[0]:<18} │ {info2.get('season', ['N/A'])[0]:<18} │\n│ Duration     │ {info1.get('duration', ['N/A'])[0]:<18} │ {info2.get('duration', ['N/A'])[0]:<18} │\n│ Soil         │ {info1.get('soil', ['N/A'])[0]:<18} │ {info2.get('soil', ['N/A'])[0]:<18} │\n│ Water        │ {info1.get('water', ['N/A'])[0]:<18} │ {info2.get('water', ['N/A'])[0]:<18} │\n│ Yield/Acre   │ {info1.get('yield_per_acre', ['N/A'])[0]:<18} │ {info2.get('yield_per_acre', ['N/A'])[0]:<18} │\n└──────────────┴────────────────────┴────────────────────┘\n\n{item1.title()}: {', '.join(info1.get('regions', ['Various'])[:2])}\n{item2.title()}: {', '.join(info2.get('regions', ['Various'])[:2])}"

    def generate_practical_answer(self, crop: str, question_type: str) -> str:
        crop_info = self.crop_types.get(crop.lower(), {})
        q_lower = question_type.lower()
        
        if "harvest" in q_lower:
            return f"🌾 HARVESTING {crop.upper()}\n\nTime: {', '.join(crop_info.get('harvest_time', ['Varies']))}\nSigns: Color change, hardness, moisture 12-14%\nMethods: Manual (small), Mechanical (large)\nPost-Harvest: Dry, clean, grade, store properly"
        
        elif "fertilizer" in q_lower or "amount" in q_lower:
            fertilizers = crop_info.get('fertilizers', ['NPK'])
            return f"💊 FERTILIZER FOR {crop.upper()}\n\nBasal: {fertilizers[0] if fertilizers else 'As per test'}\nAdditional: {', '.join(fertilizers[1:]) if len(fertilizers) > 1 else 'By stage'}\n\nTips:\n• Soil test first\n• Split nitrogen applications\n• Apply when soil moist\n• Include micronutrients"
        
        elif "organic" in q_lower:
            return f"🌿 ORGANIC {crop.upper()}\n\nSoil: FYM 15-20 tons/acre, compost\nSeed: Organic sources, biocontrol treatment\nPests: Neem, beneficial insects, traps\nDiseases: Bio-fungicides, resistant varieties\nFertilizer: Vermicompost, jeevamrit\n\nCertification: 3-year conversion period"
        
        elif "land" in q_lower or "prepare" in q_lower:
            soil = ', '.join(crop_info.get('soil', ['Well-drained']))
            return f"🔨 LAND PREPARATION FOR {crop.upper()}\n\nBest Soil: {soil}\n\nSteps:\n1. Clear residues (1 week before)\n2. Deep plough 15-20cm\n3. Second plough after 7-10 days\n4. Harrow for fine tilth\n5. Level properly\n6. Add basal fertilizer\n7. Make irrigation channels"
        
        elif "irrigation" in q_lower or "water" in q_lower:
            water = crop_info.get('water', ['Moderate'])
            irrigation = crop_info.get('irrigation', ['Regular'])
            return f"💧 IRRIGATION FOR {crop.upper()}\n\nNeed: {', '.join(water)}\nCritical: {', '.join(irrigation)}\n\nMethods:\n• Traditional: Flood, furrow\n• Efficient: Drip (saves 30-50%), Sprinkler\n\nTips:\n• Check soil moisture\n• Avoid midday irrigation\n• Mulch to reduce evaporation"
        
        elif "test soil" in q_lower:
            return "🔬 SOIL TESTING GUIDE\n\nWhen: Before each season\nHow:\n• 10-15 samples from field\n• 0-15cm depth\n• Mix, air-dry, label\n\nWhere:\n• Provincial Soil Testing Labs\n• District Agriculture Offices\n• PARC labs\n\nTests: pH, EC, N, P, K, micronutrients\nCost: PKR 500-5000"
        
        elif "ipm" in q_lower or "pest" in q_lower:
            pests = ', '.join(crop_info.get('pests', ['Pests'])[:3])
            diseases = ', '.join(crop_info.get('diseases', ['Diseases'])[:2])
            return f"🐛 IPM FOR {crop.upper()}\n\nPests: {pests}\nDiseases: {diseases}\n\nIPM Strategies:\n1. Cultural: Rotation, sanitation\n2. Mechanical: Traps, hand picking\n3. Biological: Beneficial insects, Bt\n4. Chemical: Last resort\n\nMonitor weekly, act at threshold"
        
        else:
            return f"📋 {crop.upper()} PRACTICAL GUIDE\n\n1. Varieties: {', '.join(crop_info.get('varieties', ['Recommended'])[:2])}\n2. Soil: {', '.join(crop_info.get('soil', ['Suitable'])[:1])}\n3. Season: {', '.join(crop_info.get('season', ['Time']))}\n4. Fertilizer: {', '.join(crop_info.get('fertilizers', ['NPK'])[:1])}\n5. Water: {crop_info.get('water', ['Moderate'])[0]}\n6. Yield: {', '.join(crop_info.get('yield_per_acre', ['Variable']))}\n\nContact Extension Officer for details"

    def generate_pakistan_specific_answer(self, question: str) -> str:
        q_lower = question.lower()
        
        if "major crop" in q_lower or "main crop" in q_lower:
            return "🌾 MAJOR CROPS OF PAKISTAN\n\nFood Grains:\n• Wheat (staple, all provinces)\n• Rice (export, Basmati from Punjab)\n• Maize (Punjab, KPK)\n\nCash Crops:\n• Cotton (textile industry)\n• Sugarcane (sugar industry)\n\nFruits:\n• Mango (Sindhri, Langra, Chaunsa)\n• Citrus (Kinnow major export)\n• Apple, Peach, Plum (temperate)\n• Date Palm (Balochistan)\n\nVegetables:\n• Potato, Onion, Tomato\n• Cabbage, Cauliflower, Carrot\n\nAgriculture employs ~40% labor, ~20% GDP"
        
        elif "rabi" in q_lower:
            return "📅 RABI CROPS (Oct-Dec sowing, Mar-May harvest)\n\nCereals: Wheat, Barley\nPulses: Chickpea, Lentil, Pea\nOilseeds: Mustard, Sunflower\nVegetables: Potato, Onion, Cabbage\nFruits: Citrus, Dates\nFodder: Berseem, Lucerne, Oats\n\nKey: Wheat most important Rabi crop"
        
        elif "kharif" in q_lower:
            return "📅 KHARIF CROPS (Apr-Jul sowing, Sep-Dec harvest)\n\nCereals: Rice, Maize, Sorghum, Millets\nCash: Cotton\nOilseeds: Sunflower, Groundnut\nPulses: Mungbean, Urdbean\nVegetables: Tomato, Chili, Okra, Brinjal\nFruits: Mango, Guava, Melons\n\nKey: Rice and cotton are major Kharif crops"
        
        elif "punjab" in q_lower and ("crop" in q_lower or "agriculture" in q_lower):
            return "🌾 PUNJAB AGRICULTURE\n\nMajor Crops:\n• Wheat (largest producer)\n• Rice (Basmati exports)\n• Cotton, Sugarcane\n• Mangoes (Multan, Bahawalpur)\n• Kinnow citrus\n\nRegions:\n• Central Punjab: Wheat, rice, cotton\n• South Punjab: Mangoes, citrus\n• North Punjab: Vegetables, fruits\n\nIrrigation: Canal and tube wells\nClimate: Subtropical"
        
        elif "sindh" in q_lower:
            return "🌾 SINDH AGRICULTURE\n\nMajor Crops:\n• Rice (IRRI varieties)\n• Cotton, Sugarcane\n• Mangoes (Sindhri)\n• Bananas\n\nChallenges:\n• Water scarcity\n• Salinity\n• Monsoon flooding\n\nHot, humid climate\nIndus River irrigation"
        
        elif "balochistan" in q_lower:
            return "🌾 BALOCHISTAN AGRICULTURE\n\nMajor Crops:\n• Dates (Makran region)\n• Apples, Apricots (Quetta)\n• Vegetables (Quetta)\n• Drought-tolerant crops\n\nChallenges:\n• Water scarcity\n• Arid climate\n• Limited irrigation\n\nFamous for dates and fruits"
        
        else:
            return "Pakistan agriculture: Diverse across provinces. Punjab leads in wheat/rice, Sindh in rice/cotton, Balochistan in dates/fruits, KPK in fruits/vegetables. Contact local extension for specifics."

    def extract_entities(self, text: str) -> List[str]:
        entities = []
        text_lower = text.lower()
        
        for crop in self.crop_types:
            if crop in text_lower:
                entities.append(crop)
        
        for soil in self.soil_types:
            if soil in text_lower:
                entities.append(soil)
        
        return list(set(entities))

    def generate_qna_pair(self) -> Dict[str, str]:
        q_type = random.choice(list(self.question_templates.keys()))
        
        try:
            if q_type in ["crop_general", "crop_specific", "practical"]:
                crop = random.choice(list(self.crop_types.keys()))
                template = random.choice(self.question_templates[q_type])
                
                if "{crop}" in template:
                    question = template.format(crop=crop)
                else:
                    question = template
                
                if q_type == "practical":
                    answer = self.generate_practical_answer(crop, template)
                else:
                    answer = self.generate_crop_answer(crop, q_type)
            
            elif q_type == "soil_general":
                soil = random.choice(list(self.soil_types.keys()))
                template = random.choice(self.question_templates[q_type])
                question = template.format(soil=soil)
                answer = self.generate_soil_answer(soil, q_type)
            
            elif q_type == "comparison_crop":
                crop1, crop2 = random.sample(list(self.crop_types.keys()), 2)
                template = random.choice(self.question_templates[q_type])
                question = template.format(crop1=crop1, crop2=crop2)
                answer = self.generate_comparison_answer(crop1, crop2, is_soil=False)
            
            elif q_type == "comparison_soil":
                soil1, soil2 = random.sample(list(self.soil_types.keys()), 2)
                template = random.choice(self.question_templates[q_type])
                question = template.format(soil1=soil1, soil2=soil2)
                answer = self.generate_comparison_answer(soil1, soil2, is_soil=True)
            
            elif q_type == "pakistan_specific":
                template = random.choice(self.question_templates[q_type])
                question = template
                answer = self.generate_pakistan_specific_answer(question)
            
            return {
                "question": question,
                "answer": answer,
                "type": q_type,
                "entities": self.extract_entities(question),
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            crop = random.choice(list(self.crop_types.keys()))
            question = f"How to grow {crop}?"
            answer = self.generate_crop_answer(crop, "crop_general")
            
            return {
                "question": question,
                "answer": answer,
                "type": "crop_general",
                "entities": [crop],
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    def generate_dataset(self, num_samples: int = 1000) -> List[Dict[str, Any]]:
        dataset = []
        
        print(f"Generating {num_samples} Q&A pairs...")
        for i in range(num_samples):
            if i % 100 == 0:
                print(f"Generated {i}/{num_samples} pairs...")
            
            try:
                qna_pair = self.generate_qna_pair()
                dataset.append(qna_pair)
            except Exception as e:
                print(f"Error at {i}: {e}")
                crop = random.choice(list(self.crop_types.keys()))
                dataset.append({
                    "question": f"How to grow {crop}?",
                    "answer": self.generate_crop_answer(crop, "crop_general"),
                    "type": "crop_general",
                    "entities": [crop],
                    "timestamp": datetime.now().isoformat()
                })
        
        print(f"Successfully generated {len(dataset)} pairs!")
        return dataset

    def save_dataset(self, dataset: List[Dict], filename: str = "data/full_dataset.json"):
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        print(f"Dataset saved to {filename}")
        print(f"Total samples: {len(dataset)}")
        
        try:
            df = pd.DataFrame(dataset)
            csv_filename = filename.replace('.json', '.csv')
            df.to_csv(csv_filename, index=False, encoding='utf-8')
            print(f"CSV saved to {csv_filename}")
            self.print_statistics(df)
            return df
        except Exception as e:
            print(f"Could not save CSV: {e}")
            return None

    def print_statistics(self, df):
        print("\n" + "=" * 50)
        print("DATASET STATISTICS")
        print("=" * 50)
        print(f"Total samples: {len(df)}")
        
        print("\nQuestion Type Distribution:")
        type_counts = df['type'].value_counts()
        for qtype, count in type_counts.items():
            percentage = (count / len(df)) * 100
            print(f"  {qtype}: {count} ({percentage:.1f}%)")
        
        print("\nTop 10 Most Frequent Entities:")
        all_entities = []
        for entities in df['entities']:
            all_entities.extend(entities)
        
        from collections import Counter
        entity_counts = Counter(all_entities)
        for entity, count in entity_counts.most_common(10):
            print(f"  {entity}: {count}")
        
        avg_q_len = df['question'].apply(len).mean()
        avg_a_len = df['answer'].apply(len).mean()
        print(f"\nAvg question length: {avg_q_len:.1f} chars")
        print(f"Avg answer length: {avg_a_len:.1f} chars")
        print("=" * 50)

    def generate_out_of_domain_samples(self, num_samples: int = 100) -> List[Dict]:
        out_domain_questions = [
            "What's the weather today?", "Who won the cricket match?", "Tell me a joke",
            "What is quantum physics?", "Who is the president?", "Best movies to watch?",
            "How to code in Python?", "Stock market news?", "Football results?",
            "Recommend music", "History of Rome", "Cooking recipes",
            "Car maintenance tips", "Travel destinations", "Fashion trends",
            "Gaming news", "Political news", "Celebrity gossip",
            "Medical advice", "Legal advice", "How to learn swimming?",
            "What is AI?", "Space exploration", "Stock market explained",
            "Black holes", "Blockchain", "Mutual funds",
            "Smartphone recommendations", "Weight loss tips", "Yoga for beginners",
            "Global warming", "How to make coffee?", "World War 2",
            "Machine learning", "Baking cakes", "Cryptocurrencies",
            "Meditation", "Indian history", "Climate change",
            "Tie a tie", "Best books", "Starting a business",
            "Photosynthesis", "Painting a room", "Dinosaurs",
            "Internet explained", "Playing chess", "Democracy",
            "Resume writing", "Gravity"
        ]
        
        response = "I specialize only in agriculture-related topics. Please ask about crops, soil types, farming practices, irrigation methods, pest control, harvest techniques, or Pakistan agriculture."
        
        return [
            {
                "question": q,
                "answer": response,
                "type": "out_of_domain",
                "entities": [],
                "timestamp": datetime.now().isoformat()
            }
            for q in random.sample(out_domain_questions, min(num_samples, len(out_domain_questions)))
        ]


def main():
    print("🌾 Agriculture Dataset Generator 🌱")
    print("=" * 50)
    
    import os
    os.makedirs("data", exist_ok=True)
    
    generator = AgricultureDatasetGenerator()
    
    while True:
        try:
            agri_samples = int(input("Agriculture Q&A pairs (500-5000): "))
            if 500 <= agri_samples <= 5000:
                break
            print("Enter 500-5000")
        except ValueError:
            print("Valid number required")
    
    while True:
        try:
            out_domain_samples = int(input("Out-of-domain samples (50-200): "))
            if 50 <= out_domain_samples <= 200:
                break
            print("Enter 50-200")
        except ValueError:
            print("Valid number required")
    
    print("\n" + "=" * 50)
    print("Generating dataset...")
    print("=" * 50)
    
    agriculture_data = generator.generate_dataset(num_samples=agri_samples)
    
    print("\nGenerating out-of-domain samples...")
    out_of_domain_data = generator.generate_out_of_domain_samples(num_samples=out_domain_samples)
    
    full_dataset = agriculture_data + out_of_domain_data
    random.shuffle(full_dataset)
    
    filename = f"data/agriculture_dataset_{len(full_dataset)}.json"
    df = generator.save_dataset(full_dataset, filename)
    
    if len(full_dataset) > 500:
        test_dataset = random.sample(full_dataset, min(500, len(full_dataset)))
        generator.save_dataset(test_dataset, "data/test_dataset.json")
        print("\nTest dataset saved to data/test_dataset.json")
    
    print("\n✅ Dataset generation complete!")
    print(f"📁 Main dataset: {filename}")
    print(f"🌾 Agriculture: {len(agriculture_data)}")
    print(f"🚫 Out-of-domain: {len(out_of_domain_data)}")
    
    return df


if __name__ == "__main__":
    main()
