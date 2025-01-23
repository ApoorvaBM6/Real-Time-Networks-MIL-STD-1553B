# -----------------------------------------------------------------------------
# Author: Apoorva Busunur Mallikarjuna
# Date Created: 2025-01-19
# Project: MIL STD 1553B Network Performance Analysis
# Description: This script analyzes the performance of a MIL STD 1553B network,focusing on
#              end-to-end communication delays for a representative architecture of the Rafale aircraft. 
#              The network consists of 6 MIL STD 1553B buses and a high-speed SCI core mesh network. 
#
# The script performs the following steps:
#    1. Parses the input XML file to extract message characteristics.
#    2. Computes transmission delays (d3) based on message size and link speed.
#    3. Analyzes performance in terms of access delays (d2) and end-to-end delays.
#    4. Generates an output XML file with computed delay metrics and schedulability tests.
#
# Objective: To evaluate the performance and schedulability of the 1553B network 
#            in terms of communication delays, ensuring reliable message delivery.
#
# This code is part of a exercise in avionics and real-time networks.
# -----------------------------------------------------------------------------


import xml.etree.ElementTree as ET
from xml.dom import minidom

#--------------------------------------------------
# Parsing the XML file to receiving message info
#--------------------------------------------------

def parse_messages(filePath):
    tree = ET.parse(filePath)
    root = tree.getroot()
    messages_list = []

    for message in root.findall('message'):
        message_details = {
        'Name': message.find('nom').text,
        'Type': message.find('type').text,
        'Frequency': float(message.find('frequence').text),
        'MessageSize': message.find('taille_mes').text,
        'Sender': message.find('emetteur').text,
        'Receiver': message.find('recepteur').text,
    }
        messages_list.append(message_details)
        # Messages are sorted based on their frequency
    messages_list = sorted(messages_list, key=lambda x: x['Frequency'], reverse=False)
    return messages_list


def print_message_details(messages_list):
    for msg in messages_list:
        print(f"Message Name: {msg['Name']}\n"
              f"Type: {msg['Type']}\n"
              f"Frequency: {msg['Frequency']} MHz\n"
              f"MessageSize: {msg['MessageSize']}\n"
              f"Sender: {msg['Sender']}\n"
              f"Receiver: {msg['Receiver']}\n"
              f"Transmission Delay d3: {msg['TransmissionDelay']}\n"
              f"{'-' * 40}")

#--------------------------------
# Transmission Delay Computation
#--------------------------------
def compute_transmission_delay(messages):
    #Overhead for timing analysis
    overhead_BC_RT = 56
    overhead_RT_BC = 56
    overhead_RT_RT = 106

    TransmissionRate = 1000000

    #The Transmission delay is computed using message message size and transmission rate of the physical layer
    for message in messages:
        message_size_bits = int(message['MessageSize']) * 20  # 20 bits per word
        
        # Determine total size including overhead, considering SXJJ as Master
        if message['Sender'] == "SXJJ": 
            message_size_bits += overhead_BC_RT
        elif message['Receiver'] == "SXJJ":
            message_size_bits += overhead_RT_BC
        else:
            message_size_bits += overhead_RT_RT
        
        # Calculate the transmission delay
        transmission_delay = message_size_bits / TransmissionRate 
        message['TransmissionDelay'] = transmission_delay

    return messages

#--------------------------------
# Output XML File Generation
#--------------------------------

def messages_to_xml(messages, output_file):
    root = ET.Element("messages", title="MIT STD 1553B Application")
    
    for message in messages:
        message_element = ET.SubElement(root, "message")
        
        for key, value in message.items():
            sub_element = ET.SubElement(message_element, key.lower())
            sub_element.text = str(value)
    

    #Formatting the xml to represent in readable format
    xml_str = ET.tostring(root, encoding="utf-8").decode()
    parsed_xml = minidom.parseString(xml_str)
    formatted_xml_str = parsed_xml.toprettyxml(indent=" ")

    # Write to the output file
    with open(output_file, "w", encoding="utf-8") as out:
        out.write(formatted_xml_str)
        out.close()
    print("Output XML file generated successfully")


def main():
    file_path = "xmlB1-periodique.xml"
    output_file = "output_messages.xml"

    messages = parse_messages(file_path)
    messages = compute_transmission_delay(messages)
    messages_to_xml(messages, output_file)

    print_message_details(messages)

if __name__ == "__main__":
    main()
