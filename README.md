# iCafe Automation Tool
## Overview
iCafe Automation tool is an automative game test tool developed by iCafe team.   
This tool enables test engineers design, edit and run game test script for mulitple scenarios like performance test, long-time stress test, GFX sanity test and etc.   
**`This tool is ONLY FOR game test purpose use.`**  
**`Any cheat behavior in game is not recommmaned and may cause property lost`**

## Setup Development Environment
### Prerequests:
* Operating systems:  
    * Windows 10 (21H1 or newer)  
    * Windows 11 (21H2 or newer) 

* Python Development Environment:  
    * Python 3.7 or newer
    * Anaconda3 for windows 64bit
    * Pycharm 2022 Community

* 3rd Party Libraries:  
    * PyQt5  
    * OpenCV  
### Getting Started
* Step 1: Download the source code and put them in one folder
* Step 2: Create and activate a conda environment in cmd prompt.
    ```
    conda create --name yourEnvName python=3.7.0
    activate yourEnvName 
    ```
* Step 3: Install required 3rd Libraries.
    ```
    pip install PyQt5  
    pip install pyqt5-tools
    pip install opencv-python==4.5.3.56(Recommended) 
    ```   
* Step 4: Run Pycharm **as administrator** and open source code folder as a project.
* Step 5: Select the conda environment your created earlier as the project interpreter.
* Step 6: Run gui.py and your will see the tool window.

## Release Notes
### Version 1.0
`Release date: 2022/7/15`
| **Category** | **Contributor** | **Changed item** |
| :------- | :---------- | :----------- |
|GUI design|[Junda Li](https://github.com/JundaLi07)| Designed v1.0 GUI|
|GUI logic|[Junda Li](https://github.com/JundaLi07)| Implemented logic funcions for v1.0 GUI|
|Input Simulator|[Junda Li](https://github.com/JundaLi07)|Implemented `post_message` SW input method|
|Image Quality Assessment|[Zhuangzhuang Liang](https://github.com/liangzhuangzhuang)|Implemented `real-time edge detection` method|  

**Known issues & limitations:**
* Currently can only support Genshin Impact game test
* SW Mouse movement is not working in Genshin Impact game
* Setting different language between OS and game will cause target window not found issue.
* This project can only run on windows platform.







