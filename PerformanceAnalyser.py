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
import math

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
              f"Transmission Delay d3: {msg['TD']}\n"
              f"End-to-End Delay: {msg.get('DBEB', 'N/A')}\n"
              f"Access Delay: {msg.get('DMAC', 'N/A')}\n"
              f"Schedulability Test: {msg.get('Schedulable', 'N/A')}\n"
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
        message['TD'] = transmission_delay

    return messages
#----------------------------------------------------------------------
# Performance analysis in terms of end-to-end delays and access delays
#----------------------------------------------------------------------
def compute_end_to_end_delay(messages):
    #The timing analysis is performed considering non-preemptive RM
    for message in messages:
        current_message_freq = message['Frequency']
        lower_priority_list = [message_n for message_n in messages if message_n['Frequency'] < current_message_freq]
        higher_equal_priority_list = [message_p for message_p in messages if message_p['Frequency'] >= current_message_freq and message_p != message]

        #Computing Max propogation time from list of messages with priority less than current_message
        if len(lower_priority_list) == 0:
            max_lp_messages = 0
        else:
            max_dt_dict = max(lower_priority_list, key=lambda x: x['TD'])
            max_lp_messages = max_dt_dict['TD']
        
        #End to End Delay Bound is represented as W_n_1
        #Initial Condition
        W_n_1 = message['TD']
        W_n = 0
        time_period = (1.0/message['Frequency'])

        #End to End Calculations
        while((W_n != W_n_1) and W_n_1 <= time_period):
            W_n = W_n_1
            C_sum = 0
            if len(higher_equal_priority_list) != 0:
                for message in higher_equal_priority_list:
                    C_sum += message['TD'] * math.ceil(W_n / (1.0 / message['Frequency']))
                
                W_n_1 = message['TD'] + max_lp_messages + C_sum

        message['DBEB'] = W_n_1

        #The access delay is caused as message are queued, as one message is transmitted over the physical layer at a particular instance of time
        #Access Delay d2 = End to End Delay - Transmission Delay 
        message['DMAC'] = message['DBEB'] - message['TD']

        #Schedulability is checked if End-to-End Delay is less than the Time Period
        if(W_n_1 <= time_period) and (W_n == W_n_1):
            message['Schedulable'] = True
        else:
            message['Schedulable'] = False
        
    return messages

#--------------------------------
# Output XML File Generation
#--------------------------------

def messages_to_xml(messages, output_file):
    root = ET.Element("messages", title="MIT STD 1553B Application")
    
    for message in messages:
        message_element = ET.SubElement(root, "message")
        for key, value in message.items():
            sub_element = ET.SubElement(message_element, key.upper())
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
    output_file = "output_messages1.xml"

    messages = parse_messages(file_path)
    messages = compute_transmission_delay(messages)
    messages = compute_end_to_end_delay(messages)
    #messages_to_xml(messages, output_file)
    #print(messages)
    print_message_details(messages)

if __name__ == "__main__":
    main()
