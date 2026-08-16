# Real-Time-Networks

## MIL-STD-1553B Avionics Network Performance Analysis

A real-time network analysis project focused on evaluating the performance and schedulability of a MIL-STD-1553B avionics communication network.

The project models a representative aircraft communication architecture and provides a Python-based tool for analyzing message transmission timing and schedulability.

## Overview

The network architecture consists of six MIL-STD-1553B buses interconnected through a high-speed SCI core mesh network.

The analysis focuses on periodic avionics messages exchanged across the network and evaluates whether the communication workload can satisfy its timing requirements.

The project automates the extraction of message parameters from XML and calculates communication delays and schedulability results.

## Delay Analysis

The Python analyzer evaluates several timing components.

### Transmission Delay

Transmission delay is calculated based on the message size, transmission rate, and communication overhead.

### Access Delay

The analyzer accounts for the time required for a message to gain access to the communication medium.

### End-to-End Delay

The communication delay is evaluated across the network to determine the overall timing experienced by a message between its sender and receiver.

These timing values are used as inputs to the schedulability analysis.

## Schedulability Analysis

The project applies non-preemptive Rate Monotonic scheduling to evaluate whether periodic network messages can meet their timing requirements.

The analysis considers the relative timing requirements of the messages and determines whether the communication workload is schedulable.
