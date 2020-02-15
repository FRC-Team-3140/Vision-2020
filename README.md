# Vision-2020
Our 2020 vision code (in Python)

## Components
We are using a Raspberry Pi coprocessor and a networking switch to run our vision code. We are also using a USB Camera.

## How to use 
Our strategy is quite similar to the one described here: https://docs.wpilib.org/en/latest/docs/software/vision-processing/raspberry-pi/using-a-coprocessor-for-vision-processing.html
However, instead of connecting the switch directly to the roboRIO, we connect it to the radio instead. Then, we use the radio's second ethernet port to connect to the roboRIO.

Follow the documentation here to install the necessary components onto the rPi: https://docs.wpilib.org/en/latest/docs/software/vision-processing/raspberry-pi/index.html

Finally, simply deploy this code as a python file in the Application tab of the pi's webdashboard.
