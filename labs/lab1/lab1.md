# Lab1 - CTI Report Mapping to MITRE ATT&CK

## Participants
- Itay Fischer

## Link to the Source CTI Report
- https://cloud.google.com/blog/topics/threat-intelligence/recovering-active-adfs-signing-keys-machine-dpapi

## Short Attack Summary
- The report talks about a potential security breach caused by a configuration drift where the attacker can gain access to user's Microsoft account without the need of his credentials and while negading the multi-factor authentication.
- The attacker obtains the private key of an ADFS token-signing certificate and uses it to pass every other identity-based controls.

## Attack Diagram / Sequence
<img width="600 " height="528" alt="image" src="https://github.com/user-attachments/assets/afdb4a2c-89ca-4783-bb3f-ba2284055ac7" />

## MITRE ATT&CK Mapping
| Tactic | Technique Name | Technique ID | How it Applies to this Attack |
| :--- | :--- | :--- | :--- |
| **Execution** | System Services: Service Execution | **T1035** / **T1059** | The attacker executes commands/tools (e.g., `SharpDPAPI /machine`) on the host under the `SYSTEM` context (`S-1-5-18`). |
| **Credential Access** | Private Keys | **T1552.004** | The attacker targets and extracts the ADFS RSA token-signing private key file stored on disk under `C:\ProgramData\Microsoft\Crypto\RSA\MachineKeys\`. |
| **Credential Access** | Credentials from Password Stores: DPAPI | **T1555.004** | The attacker decrypts the host's DPAPI-protected machine master keys using the `DPAPI_SYSTEM` LSA secret, granting access to the encrypted private key material without requiring user credentials. |
| **Credential Access** | Forge Web Credentials: SAML Tokens | **T1606.002** | Using the extracted private key, the attacker signs custom, forged SAML assertions claiming any identity (such as a Global Administrator) — achieving a **Golden SAML** attack. |
| **Defense Evasion** | Subvert Trust Controls | **T1553** | The attacker takes advantage of **configuration drift** (manual certificate rotation leaving stale WID database entries) to obtain valid keys outside standard monitored database stores. |
| **Defense Evasion** | Direct File Access / EDR Evasion | **T1003** | By pulling master keys directly from the file system and Machine DPAPI, the attacker completely avoids targeting process memory (`LSASS.exe`) or interactive service tokens, evading standard credential-dumping detections. |
| **Initial Access / Privilege Escalation** | Use Alternate Authentication Material: Pass the Token | **T1550.004** | The attacker presents the forged SAML token to federated identity providers (like Entra ID / M365) to authenticate as target users, completely bypassing MFA and Conditional Access. |

## Insights
- During this lab I learned about how to approach, classify and process different attack methods,
- I learned about some of the tools and methods that are accessible to everyone and can be used to intercept these types of attacks 
