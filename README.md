# Quick Setup

The following is a quick setup guide to install and run the main application. A basic working knowledge of Windows command prompt is assumed for this guide.

1. Clone the following github repository to your windows machine: [REPO](https://github.com/josephDglennon/MDEgroup37.git)
2. Install Anaconda for windows at the following link: [Anaconda Download](https://www.anaconda.com/download)
3. Using the installed Anaconda prompt, navigate to the MDEgroup37 directory on your machine.
4. Run the following commands from powershell to generate the Anaconda environment, install the required dependencies, and activate the new environment. You will need to navigate to this directory and run the activate command each time you open a new terminal in order to run the application.
`$ conda env create -f environment.yml`
`$ conda activate dmg-env`
5. To run the application, from the same directory in powershell, run the following command:
`$ python ./src/main.py`
6. To set up the measurement apparatus, plug an Arduino with standard Firmata installed into a USB port on your machine as well as the desired audio input device. 
   - Arduino IDE can be installed at the following link:
     [Arduino IDE](https://support.arduino.cc/hc/en-us/articles/360019833020-Download-and-install-Arduino-IDE)
   - Firmata can be installed directly from your Arduino IDE via the toolbar:
     Files >> Examples >> Firmata >> StandardFirmata
   - Take Note of the COM port which the Arduino board is detected at in your IDE
7. Open the settings menu in the UAS Damage Assessment GUI window and ensure that the COM port field matches the value you discovered in step 6. The application will need to be restarted for this setting to take effect.
8. Select the audio device you plugged in via the Audio Device Recording drop down menu.
9. Test entries may now be gathered through the ‘New Test’ menu option.
