import requests
import os
import json
import re
import shutil
import pandas as pd
from autoLibrarySymbols import * #librarySymbols.py
from handmadeLibrarySymbols import * #handmadeLibrarySymbols.py


def download_file(url, filename):
    try:
        # Check if the file already exists
        if os.path.exists(filename):
            # Delete the existing file
            os.remove(filename)
            print(f"Deleted existing file: {filename}")

        response = requests.get(f"{url}/{filename}", stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes
        with open(filename, "wb") as f:
            for chunk in response.iter_content(None):
                f.write(chunk)
        print(f"Downloaded {url}/{filename} to {filename}")
    except requests.RequestException as e:
        print(f"Download {url} failed: {e}")

def extract_value(description, mode, lcsc_id):
    if lcsc_id == 22818: return "16kΩ"
    if lcsc_id == 30274: return "6pF"
    if lcsc_id == 3013473: return "100nF"
    if lcsc_id == 3008298: return "4.7nF"
    
    if mode == "Resistors":
        pattern = r"(\d+(?:\.\d+)?(?:[kMGT]?)(?:Ω|ohm))"  # matches numbers followed by Ω, ohm, Ohm, or OHM
    elif mode == "Capacitors":
        pattern = r"(\d+(?:\.\d+)?(?:[pnu]?)(?:f|farad))"  # matches numbers followed by F, f, Farad, farad, pF, pf, nF, nf, uF, uf
    else:
        raise ValueError("extract_value(): Invalid mode")

    match = re.search(pattern, description, re.IGNORECASE)
    if match:
        return match.group(0)
    else:
        print(f"Error: No value found for https://jlcpcb.com/partdetail/C{lcsc_id}  ({description})")
        return None

def extract_diode_type(description, pins, lcsc_id):
    if lcsc_id == 2990493: return "TVS-Bi"
    if lcsc_id == 2990473: return "TVS-Bi"
    if lcsc_id == 2990416: return "TVS-Bi"
    if lcsc_id == 2990414: return "TVS-Bi"
    if lcsc_id == 2990261: return "TVS-Bi"
    if lcsc_id == 2990124: return "TVS-Bi"
    if lcsc_id == 3019524: return "TVS-Bi"
    if lcsc_id == 1323289: return "TVS-Bi"
    if lcsc_id == 3001945: return "TVS-Uni"
    if lcsc_id == 2833277: return "TVS-Bi"
    if lcsc_id == 2975471: return "TVS-Uni"
    if lcsc_id == 78395: return "TVS-Bi"
    if lcsc_id == 2925443: return "TVS-Uni"
    if lcsc_id == 2936988: return "TVS-Bi"
    if lcsc_id == 2925441: return "TVS-Bi"
    if lcsc_id == 2925451: return "TVS-Bi"
    if lcsc_id == 20617908: return "TVS-Bi"
    if lcsc_id == 20617910: return "TVS-Bi"
    if lcsc_id == 22466368: return "Schottky13"
    if lcsc_id == 22466371: return "Schottky13"
    
    diode_types = {
        "Schottky": {"pins": 2, "type": "Schottky"},
        "Recovery": {"pins": 2, "type": "Recovery"},
        "General": {"pins": 2, "type": "General"},
        "Switching": {"pins": 2, "type": "Switching"},
        "Zener": {"pins": 2, "type": "Zener"},
        "Bidirectional": {"pins": 2, "type": "TVS-Bi"},
        "Unidirectional": {"pins": 2, "type": "TVS-Uni"}
    }
    for keyword, diode_info in diode_types.items():
        if keyword.casefold() in description.casefold():
            if diode_info["pins"] == pins:
                return diode_info["type"]
            elif keyword == "Zener" and pins == 3:
                return "Zener13"
            else:
                # print(f"Error: Number of pins ({pins}) does not match expected ({diode_info['pins']}) for https://jlcpcb.com/partdetail/C{lcsc_id}  ({description})")
                return None
    # print(f"Error: No diode type found for https://jlcpcb.com/partdetail/C{lcsc_id}  ({description})")
    return None

def extract_transistor_type(description, pins, lcsc_id):
    if lcsc_id == 484513: return "NMOS"
    if lcsc_id == 396043: return "NMOS"
    if lcsc_id == 916398: return "NMOS"
    if lcsc_id == 296127: return None
    if lcsc_id == 2907947: return "NPN"
    if lcsc_id == 2991999: return "PNP"
    if lcsc_id == 533008: return "NPN"
    
    transistor_types = {
        "PNP": {"pins": 3, "type": "PNP"},
        "NPN": {"pins": 3, "type": "NPN"},
        "NChannel": {"pins": 3, "type": "NMOS"},
        "PChannel": {"pins": 3, "type": "PMOS"},
        "N-Channel": {"pins": 3, "type": "NMOS"},
        "P-Channel": {"pins": 3, "type": "PMOS"}
    }
    for keyword, transistor_info in transistor_types.items():
        if keyword.casefold() in description.casefold():
            if transistor_info["pins"] == pins:
                return transistor_info["type"]
            else:
                # print(f"Error: Number of pins ({pins}) does not match expected ({transistor_info['pins']}) for https://jlcpcb.com/partdetail/C{lcsc_id}  ({description})")
                return None
    # print(f"Error: No transistor type found for https://jlcpcb.com/partdetail/C{lcsc_id}  ({description})")
    return None

def extract_LED_value(description, lcsc_):
    if lcsc == 2985996:
        return "Red", "LED"
    elif lcsc == 34499:
        return "White", "LED"
    
    color_pattern = r"(Red|Green|Blue|Yellow|White|Emerald)"

    color_match = re.search(color_pattern, description, re.IGNORECASE)
    
    if color_match:
        color = color_match.group(0).replace("Emerald", "Green")
        return color, "LED"
    else:
        print(f"Error: No LED value extracted for https://jlcpcb.com/partdetail/C{lcsc}  ({description})")
        return None, None

def extract_inductor_type_value(description, joints, lcsc):
    current = None
    if lcsc == 2827387: current = "300mA"
    if lcsc == 2827415: current = "900mA"
    if lcsc == 3007708: current = "410mA"
    if lcsc == 2844914: current = "305mA"
    if lcsc == 2827354: current = "5.5A"
    if lcsc == 2827458: current = "400mA"
    if lcsc == 2835403: return "120nH,80mA", "Inductor"
    
    
    # Define patterns to match inductance values
    inductance_patterns = [
        r"\b(\d+\.\d+[u|m|n]H)\b",  # e.g. 10.5uH, 10.5mH, 10.5nH
        r"\b(\d+[u|m|n]H)\b",  # e.g. 10uH, 10mH, 10nH
    ]

    # Define patterns to match current values
    current_patterns = [
        r"(\d+(\.\d+)?)A",  # e.g. 1A, 2A, 4.95A
        r"(\d+)mA",  # e.g. 100mA, 2000mA
    ]

    # Iterate over patterns and search for matches
    for pattern in inductance_patterns:
        inductance_match = re.search(pattern, description, re.IGNORECASE)
        if inductance_match:
            # Extract inductance value
            inductance = inductance_match.group(1)

            # Extract current value
            if current == None:
                for current_pattern in current_patterns:
                    current_match = re.search(current_pattern, description, re.IGNORECASE)
                    if current_match:
                        current = current_match.group(1)
                        if "mA" in current_pattern:
                            current += "mA"
                        else:
                            current += "A"
                        break
                else:
                    current = ""
                    print(f"Error: No current value extracted for https://jlcpcb.com/partdetail/C{lcsc}  ({description})")

            # Return inductance and current values
            return f"{inductance},{current}", "Inductor"
        
    if "Ferrite" in description:
        return "", "Ferrite"

    # If no match is found, print an error message and return None
    print(f"Error: No inductance value extracted for https://jlcpcb.com/partdetail/C{lcsc}  ({description})")
    return None, None

def extract_variable_resistor_type_value(description, lcsc):
    # NTC Thermistors
    if lcsc == 2991699: return "NTC", "47kΩ,4050"
    if "NTC" in description:
        pattern = r"(\d+(?:\.\d+)?Ω)"  # matches numbers followed by Ω
        match = re.search(pattern, description)
        if match:
            return "NTC", match.group(0)
        else:
            print(f"Error: Unknown resistance for https://jlcpcb.com/partdetail/C{lcsc}  ({description})")
            return None, None

    # Varistors (MOV)
    elif "Varistors" in description:
        return "MOV", ""

    # Fuses
    elif "Fuse" or "fuse" in description:
        if lcsc == 2924957: value = "1.5A"
        elif lcsc == 2838983: value = "1.5A"
        else: value = ""
        if "Resettable" in description:
            return "Fuse,Resettable", value
        else:
            return "Fuse", value

    # Unknown
    else:
        print(f"Error: Unknown type for https://jlcpcb.com/partdetail/C{lcsc}  ({description})")
        return None, None

def extract_capacitor_voltage(description, lcsc):
    voltage_pattern = r"\b(\d+(?:\.\d+)?)(V|kV)\b"
    voltage_match = re.search(voltage_pattern, description, re.IGNORECASE)

    if voltage_match:
        return voltage_match.group(0)
    else:
        return None

def get_basic_or_prefered_type(df, index):
    if df.loc[index, "basic"] > 0:
        return "Basic Component"
    elif df.loc[index, "preferred"] > 0:
        return "Preferred Component"
    else:
        print("extended component found")
        return "Extended Component"

def generate_kicad_symbol_libs(symbols):
    for lib_name, symbol_list in symbols.items():
        lib_content = "(kicad_symbol_lib\n"
        lib_content += "\t(version 20231120)\n"
        lib_content += '\t(generator "CDFER")\n'
        lib_content += '\t(generator_version "8.0")\n'
        for symbol in symbol_list:
            lib_content += symbol + "\n"
        lib_content += ")\n"

        lib_content = lib_content.replace("℃", "°C")

        with open(f"JLCPCB-Kicad-Symbols/JLCPCB-{lib_name}.kicad_sym", "w") as f:
            f.write(lib_content)

def check_models():
    exempt_footprints = ["Hole, 3mm","Hole_Tooling_JLCPCB","MouseBites, Cosmetic, JLCPCB, 1.6mm","MouseBites, Mechanical, JLCPCB, 1.6mm","Part_Num_JLCPCB"]

    footprints_folder_path = 'JLCPCB-Kicad-Footprints'
    models_folder_path = os.path.join(footprints_folder_path, "3dModels")
    archived_models_folder_path = os.path.join('Archived-Symbols-Footprints', models_folder_path)

    footprint_names = [os.path.splitext(filename)[0] 
                    for filename in os.listdir(footprints_folder_path) 
                    if filename.endswith('.kicad_mod')]
    archived_model_names = [os.path.splitext(filename)[0] 
                for filename in os.listdir(archived_models_folder_path) 
                if filename.endswith('.step')]
    model_names = [os.path.splitext(filename)[0] 
                for filename in os.listdir(models_folder_path) 
                if filename.endswith('.step')]


    model_names_used = []

    for footprint_name in footprint_names:
        footprint_file_path = os.path.join(footprints_folder_path, f"{footprint_name}.kicad_mod")
        
        with open(footprint_file_path, 'r') as file:
            content = file.read()
            match = re.search(r'\(model "([^"]+)"', content)
            
            if match:
                model_path = match.group(1)
                model = re.search(r'/3dModels/([^"]+).step', model_path)
                if model:
                    model = model.group(1)
                    if model not in model_names:
                        if model in archived_model_names:
                            post_move_file_path = os.path.join(models_folder_path, f"{model}.step")
                            pre_move_file_path = os.path.join(archived_models_folder_path, f"{model}.step")
                            shutil.move(pre_move_file_path, post_move_file_path)
                            print(f"Un-archived needed model: {model}")
                        else: 
                            print(f"Missing 3D Model for Footprint: {footprint_name} ({model_path})")
                    else:
                        model_names_used.append(model)
                else:
                    print(f"Incorrect Model path for Footprint: {footprint_name} ({model_path})")
            elif footprint_name not in exempt_footprints:
                print(f"Empty Model Field for Footprint: {footprint_name}")
                
    for model in model_names:
        if model not in model_names_used:
            pre_move_file_path = os.path.join(models_folder_path, f"{model}.step")
            post_move_file_path = os.path.join(archived_models_folder_path, f"{model}.step")
            shutil.move(pre_move_file_path, post_move_file_path)
            print(f"Archived unused model: {model}")

def check_footprints():
    symbols_folder_path = 'JLCPCB-Kicad-Symbols'
    footprints_folder_path = 'JLCPCB-Kicad-Footprints'
    archived_footprints_folder_path = os.path.join('Archived-Symbols-Footprints', footprints_folder_path)

    archived_footprint_names = [os.path.splitext(filename)[0] 
                    for filename in os.listdir(archived_footprints_folder_path) 
                    if filename.endswith('.kicad_mod')]
    footprint_names = [os.path.splitext(filename)[0] 
                    for filename in os.listdir(footprints_folder_path) 
                    if filename.endswith('.kicad_mod')]
    footprint_names_used = []

    for symbol_lib_filename in os.listdir(symbols_folder_path):
        footprint_file_path = os.path.join(symbols_folder_path, symbol_lib_filename)
        
        if os.path.isfile(footprint_file_path) and symbol_lib_filename.endswith('.kicad_sym'):
            with open(footprint_file_path, 'r') as file:
                symbol_name = None
                footprint_name = None
                
                for line in file:
                    # Search for symbol name
                    match = re.search(r'\(symbol "([^"]+)"', line)
                    if match:
                        symbol_name = match.group(1)
                        footprint_name = None
                        
                    # Search for footprint
                    match = re.search(r'\(property "Footprint" "([^"]+)"', line)
                    if match:
                        footprint_name = match.group(1)
                        footprint_lib_match = re.search(r'JLCPCB-Kicad-Footprints:([^"]+)', footprint_name)
                        if footprint_lib_match:
                            footprint_name = footprint_lib_match.group(1)
                            if footprint_name not in footprint_names:
                                if footprint_name in archived_footprint_names:
                                    post_move_file_path = os.path.join(footprints_folder_path, f"{footprint_name}.kicad_mod")
                                    pre_move_file_path = os.path.join(archived_footprints_folder_path, f"{footprint_name}.kicad_mod")
                                    shutil.move(pre_move_file_path, post_move_file_path)
                                    print(f"Un-archived needed footprint: {footprint_name}")
                                else:
                                    print(f"Missing Footprint For Symbol: {symbol_name} -> {footprint_name} ({footprint_file_path})")
                            else:
                                footprint_names_used.append(footprint_name)
                        else:
                            print(f"Incorrect Symbol Footprint Library For Symbol: {symbol_name} -> {footprint_name} ({footprint_file_path})")
                            
    for footprint in footprint_names:
        if footprint not in footprint_names_used:
            pre_move_file_path = os.path.join(footprints_folder_path, f"{footprint}.kicad_mod")
            post_move_file_path = os.path.join(archived_footprints_folder_path, f"{footprint}.kicad_mod")
            shutil.move(pre_move_file_path, post_move_file_path)
            print(f"Archived unused footprint: {footprint}")


# Download the latest basic/preferred csv file
download_file("https://cdfer.github.io/jlcpcb-parts-database", "jlcpcb-components-basic-preferred.csv")

df = pd.read_csv("jlcpcb-components-basic-preferred.csv")

footprints_dir = "JLCPCB-Kicad-Footprints"
footprints_lookup = {os.path.splitext(file)[0] for file in os.listdir(footprints_dir)}

symbols = {"Resistors": [], "Capacitors": [], "Diodes":[], "Transistors":[], "Inductors":[], "Variable-Resistors": []}
smt_joint_cost = 0.0017
hand_solder_joint_cost = 0.0173

componentList = []
names_lookup = []

for index in range(0, len(df)):
    # lcsc,category_id,category,subcategory,mfr,package,joints,manufacturer,basic,preferred,description,datasheet,stock,last_on_stock,price,extra
    lcsc = df.loc[index, "lcsc"]
    category = f'{df.loc[index,"category"]},{df.loc[index,"subcategory"]}'
    manufacturer = df.loc[index,"manufacturer"]
    manufacturerPartID = df.loc[index,"mfr"]
    footprint_name = df.loc[index, "package"]
    description = df.loc[index, "description"]
    joints = df.loc[index, "joints"]
    units = 1
    secondary_mode = ""
    subcategory = str(df.loc[index,"subcategory"])

    if "Plugin" in footprint_name:
        joint_cost = hand_solder_joint_cost
    else:
        joint_cost = smt_joint_cost

    price_json = json.loads(df.loc[index, "price"])
    price = float(price_json[0]["price"] + (joints * joint_cost))
    price = round(price, 3)
    price_str = f"{price:.3f}USD"
    
    if price > 3.0 or footprint_name == "0201" or lcsc == 882967:
        df.drop(index = index, inplace= True)
    else:
        component_class = get_basic_or_prefered_type(df, index)
        stock = df.loc[index, "stock"]
        keywords = ""
        value = None

        try:
            extra_json = json.loads(df.loc[index, "extra"])
            datasheet = extra_json["datasheet"]["pdf"]
            attributes = extra_json["attributes"]
        except:
            datasheet = df.loc[index, "datasheet"]
            attributes = []

        if df.loc[index, "category"] == "Resistors" and lcsc != 2909989:
            value = extract_value(description, "Resistors", lcsc)
            if "x4" in footprint_name:
                units = 4
            lib_name = "Resistors"
            
        elif df.loc[index, "category"] == "Capacitors":
            value = extract_value(description, "Capacitors", lcsc)
            lib_name = "Capacitors"
            if lcsc == 360353:
                footprint_name =  "Plugin,P=5mm"
            if attributes == []:
                # {'Voltage Rated': '50V', 'Tolerance': '±5%', 'Capacitance': '15pF', 'Temperature Coefficient': 'NP0'}
                capacitor_voltage = extract_capacitor_voltage(description, lcsc)
                if capacitor_voltage != None:
                    attributes = {'Voltage Rated': capacitor_voltage}
            
        elif df.loc[index, "category"] == "Diodes" or ("TVS" in subcategory) or ("ESD" in subcategory):
            value= extract_diode_type(description, joints, lcsc)
            secondary_mode = value
            lib_name = "Diodes"
            if value == None:
                if update_component_inplace(lcsc, "Diode-Packages", price, stock, datasheet, description) == True:
                    df.drop(index = index, inplace= True)
            
        elif subcategory == "Light Emitting Diodes (LED)":
            if lcsc == 2895565 or lcsc == 2835341:
                if update_component_inplace(lcsc, "Diode-Packages", price, stock, datasheet, description) == True:
                    df.drop(index = index, inplace= True)
            else:
                value, secondary_mode = extract_LED_value(description,lcsc)
                lib_name = "Diodes"
            
        elif subcategory == "MOSFETs" or (subcategory == "Bipolar Transistors - BJT") or (subcategory == "Bipolar (BJT)") or (df.loc[index, "category"] == "Triode/MOS Tube/Transistor") or (df.loc[index, "category"] == "Transistors")  or (df.loc[index, "category"] == "Transistors/Thyristors"):
            value= extract_transistor_type(description, joints, lcsc)
            secondary_mode = value
            lib_name = "Transistors"
            if lcsc == 20917:
                footprint_name = "SOT-23"
            if value == None:
                if update_component_inplace(lcsc, "Transistor-Packages", price, stock) == True:
                    df.drop(index = index, inplace= True)
            
        elif subcategory == "Inductors (SMD)" or (subcategory == "Ferrite Beads") or (subcategory == "Power Inductors"):
            value, secondary_mode= extract_inductor_type_value(description, joints, lcsc)
            lib_name = "Inductors"
            
        elif subcategory == "Crystals" or subcategory == "Oscillators":
            if update_component_inplace(lcsc, "Crystals", price, stock, datasheet, description) == True:
                df.drop(index = index, inplace= True)
            
        elif subcategory == "NTC Thermistors" or (subcategory == "Varistors") or (subcategory == "Fuses") or (subcategory == "Resettable Fuses"):
            secondary_mode, value= extract_variable_resistor_type_value(description, lcsc)
            lib_name = "Variable-Resistors"
            if lcsc == 210465:
                footprint_name = "Plugin,P=5mm"
            
        elif df.loc[index, "category"] == "Embedded Processors & Controllers" or (df.loc[index, "category"] == "Single Chip Microcomputer/Microcontroller"):
            if update_component_inplace(lcsc, "MCUs", price, stock) == True:
                df.drop(index = index, inplace= True)
                
        elif df.loc[index, "category"] == "Connectors" or (df.loc[index, "category"] == "Key/Switch") or (df.loc[index, "category"] == "Switches") or (lcsc == 2909989):
            if update_component_inplace(lcsc, "Connectors_Buttons", price, stock, datasheet) == True:
                df.drop(index = index, inplace= True)
                
        elif df.loc[index, "category"] == "Power Management" or (df.loc[index, "category"] == "Power Management ICs") or (lcsc == 394180):
            if update_component_inplace(lcsc, "Power", price, stock, datasheet, description) == True:
                df.drop(index = index, inplace= True)
                
        elif df.loc[index, "category"] == "Amplifiers" or (df.loc[index, "category"] == "Operational Amplifier/Comparator") or subcategory == "Analog Switches / Multiplexers" or subcategory == "Digital Potentiometers":
            if update_component_inplace(lcsc, "Analog", price, stock, datasheet, description) == True:
                df.drop(index = index, inplace= True)
                
        elif df.loc[index, "category"] == "Memory":
            if update_component_inplace(lcsc, "Memory", price, stock, datasheet, description) == True:
                df.drop(index = index, inplace= True)
                
        elif df.loc[index, "category"] == "Communication Interface Chip" or (df.loc[index, "category"] == "Communication Interface Chip/UART/485/232") or (df.loc[index, "category"] == "Interface ICs") or (df.loc[index, "category"] == "Signal Isolation Devices"):
            if update_component_inplace(lcsc, "Interface", price, stock, datasheet, description) == True:
                df.drop(index = index, inplace= True)
                
        elif df.loc[index, "category"] == "Nixie Tube Driver/LED Driver" or (subcategory == "LCD Drivers"):
            if update_component_inplace(lcsc, "Display-Drivers", price, stock) == True:
                df.drop(index = index, inplace= True)
            
        elif subcategory == "Current Transformers" or (subcategory == "Common Mode Filters"):
            if update_component_inplace(lcsc, "Transformers", price, stock) == True:
                df.drop(index = index, inplace= True)
            
        elif df.loc[index, "category"] == "Optocoupler" or (subcategory == "Optocouplers") or (subcategory == "Optocouplers - Phototransistor Output") or (subcategory == "Reflective Optical Interrupters"):
            if update_component_inplace(lcsc, "Optocouplers", price, stock) == True:
                df.drop(index = index, inplace= True)
                
        elif df.loc[index, "category"] == "Logic ICs" or (subcategory == "Real-time Clocks (RTC)") or (subcategory == "Timers / Clock Oscillators") or (subcategory == "Real-Time Clocks(RTC)") or (subcategory == "Clock Buffers/Drivers/Distributions") or (subcategory == "Hall Sensor"):
            # print(f"{lcsc},")
            if update_component_inplace(lcsc, "ICs", price, stock) == True:
                df.drop(index = index, inplace= True)
            
        if value != None:
            df.drop(index = index, inplace= True)
            symbol = generate_kicad_symbol(
                    lib_name,
                    secondary_mode,
                    lcsc,
                    datasheet,
                    description,
                    footprint_name,
                    value,
                    keywords,
                    price_str,
                    component_class,
                    stock,
                    category,
                    manufacturer,
                    manufacturerPartID,
                    attributes,
                    units,
                    footprints_lookup,
                    names_lookup
                )
            symbols[lib_name].append(symbol)

generate_kicad_symbol_libs(symbols)

update_library_stock_inplace("Analog")
update_library_stock_inplace("Connectors_Buttons")
update_library_stock_inplace("Crystals")
update_library_stock_inplace("Diode-Packages")
update_library_stock_inplace("Display-Drivers")
update_library_stock_inplace("ICs")
update_library_stock_inplace("Interface")
update_library_stock_inplace("Memory")
update_library_stock_inplace("MCUs")
update_library_stock_inplace("Optocouplers")
update_library_stock_inplace("Power")
update_library_stock_inplace("Transformers")
update_library_stock_inplace("Transistor-Packages")

check_footprints()
check_models()