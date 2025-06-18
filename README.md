# Sleep Apnea Detection System
## General Description
This project is a comprehensive desktop application developed in Python 3 for use on the Linux operating system, featuring a graphical interface based on CustomTkinter.

The purpose of this product is to detect risk factors associated with Obstructive Sleep Apnea (OSA) through the analysis of respiratory audio signals using Artificial Intelligence models, generation of personalized reports, and analysis of biomedical signals such as snoring, to determine or diagnose if the user suffers from OSA during sleep. This solution aims to offer a reliable and accessible alternative for people experiencing severe snoring problems during sleep, thus mitigating the difficulties associated with obtaining a traditional medical diagnosis, such as long waiting times in public health institutions or high costs in the private sector. The application will take into account aspects related to the patient's anatomy and recommend various preventive actions before visiting a specialist. Its purpose is to improve the users' quality of life by providing early detection and timely recommendations to avoid serious complications related to sleep apnea, which in some cases can lead to death, as well as serving as an option for early OSA diagnosis, allowing the patient to become aware of their condition and seek medical attention if necessary.

## Problem Description
Obstructive Sleep Apnea represents a public health issue due to its high impact on overall health. In many cases, affected individuals are unaware of their condition, which can lead to health deterioration and decreased daily performance.

Access to an otorhinolaryngological diagnosis within Costa Rica's public health system often involves prolonged waiting times, which can delay the identification of conditions like OSA. On the other hand, in the private healthcare sector, while diagnosis access is much quicker, the costs can be high, thus limiting its accessibility for most patients.

OSA is a common respiratory disorder that affects a large part of the population, especially individuals with obesity, hypertension, and older age. Many people remain undiagnosed due to lack of access to the necessary evaluations, which typically require visits to specialized centers. Given the significant health impact of this condition and the existing barriers to its diagnosis, the development of innovative tools that enable the identification of risk factors associated with this disorder in an accessible and simple way is beneficial. This AI-based solution, which uses biomedical signal analysis, allows for quick assessments from the comfort of one's home, reduces the burden on specialized health services, and facilitates the identification of patients who require advanced studies. This system is capable of providing a quick and simple sleep assessment, benefiting especially those who experience symptoms such as intense snoring and breathing pauses during sleep, thereby improving their access to timely diagnosis and the possibility of receiving recommendations to improve their nighttime rest, as well as appropriate forms of treatment while awaiting professional care.

The development of this application aligns with the goals of preventive medicine, remote monitoring, and empowering patients in managing their health.

![image](https://github.com/user-attachments/assets/14e10b4c-3964-41e1-8965-379f6b16163f)

Figure 1. Graphical representation of Obstructive Sleep Apnea condition.

## Project Scope
The application allows users to monitor their sleep and detect possible apnea episodes through the collection and analysis of sound signals. It will implement artificial intelligence algorithms and signal processing to identify patterns associated with obstructive sleep apnea. Additionally, it will provide personalized recommendations based on the detected risk factors and enable the generation of detailed reports for the user. The software will initially be compatible with desktop devices (Linux), utilizing the device's integrated hardware, such as the microphone, for audio data collection. The application will be available for anyone who suffers or suspects they suffer from apnea or severe snoring during sleep.

## Project Features Description
* A module is used for the acquisition of respiratory signals using a microphone. The following audio features are extracted from this audio:
  - RMS (Root Mean Square) — Snoring energy
  - ZCR (Zero Crossing Rate) — Nasal airflow
  - Spectral Centroid — Energy distribution in frequency
  - FFT / STFT — Full spectral analysis
* AI classification models are also used:
  - Apnea/No Apnea Detection: This model uses RandomForestClassifier to identify patterns of positive OSA cases by combining parameters such as age, BMI, snoring signals, etc.
  - Treatment Need Prediction: This model uses RandomForestClassifier to estimate if treatment is required for the patient. Like the previously described model, it relies on parameters such as age, BMI, and others, as well as whether positive or negative OSA cases exist.

* A patient profile form is used to determine their physical condition and habits and to identify personalized recommendations based on the parameters provided by the user.
* A sleep session history is available, which allows visualization of processed data, playback of recorded audio, and report generation with data related to the sleep session, in addition to the option to delete a specific session and generate a complete report covering all sleep sessions.
* For each sleep session, it is possible to set alarms at a specific time and select the tone to be played as the alarm.

* A screen is used to display the terms and conditions of use, which must be accepted before using the app.

## Application Appendices

![image](https://github.com/mjcarranza/Apnea-Detector/blob/main/assets/App%20Images/Screenshot%20from%202025-06-18%2010-28-47.png)

Fig 2. Main window.

![image](https://github.com/mjcarranza/Apnea-Detector/blob/main/assets/App%20Images/Screenshot%20from%202025-06-18%2010-28-54.png)

Fig 3. Recording window.

![image](https://github.com/mjcarranza/Apnea-Detector/blob/main/assets/App%20Images/Screenshot%20from%202025-06-18%2010-44-52.png)

Fig 4. Profile.

![image](https://github.com/mjcarranza/Apnea-Detector/blob/main/assets/App%20Images/Screenshot%20from%202025-06-18%2011-02-59.png)

Fig 5. Sleep history.
