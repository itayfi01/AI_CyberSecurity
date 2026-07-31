Student name: Itay Fischer \
Student ID: 323103317 \
Date: 31.07.26

Finding 1
---------
Activity:
Source IP:   **172.18.0.5** \
Evidence:  **3 sequential Failed password for root logs within 7 seconds** \
MITRE ATT&CK technique:  **Brute Force: Password Guessing (T1110.001)** \
Tactic: **Credential Access** \
Why is this finding suspicious? \
**Rapid repeated login failures targeting the root user from incremental ports, indicating automated password guessing.**

Finding 2
---------
Activity:
Source IP: **172.18.0.7** \
Evidence: **Network scan detected against ports 22,80,443,3306** \
MITRE ATT&CK technique: **Network Service Discovery (T1046)** \
Tactic: **Discovery** \ 
Why is this finding suspicious? \ 
**Port scanning activity checking for common exposed services** \ 

Containerization
----------------
Explain briefly why Docker was used even though the laboratory did not use cloud services:

A docker was used in this lab to demonstrate the same principles found in cloud-native environments:

Reflection
----------
1. Why is a detection finding not proof of an attack?
   
   Since the actions can potentially be innocent (for example a user mistook his password multiple times) the findings are considered "suspicious" and might require additional investigation, but them alone are not enough to be considered proof of attack.
2. What additional logs would help confirm the findings?

    Detailed SSH daemon events for 172.18.0.5
   
4. What could cause a false positive?

   For example a user that entered wrong passwords multiple times before eventually entering using the real password
