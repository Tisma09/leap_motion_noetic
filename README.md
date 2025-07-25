# ROS LEAP MOTION FOR NOETIC

ROS driver for the Leap Motion Controller based on [leap_motion](https://github.com/ros-drivers/leap_motion) but has been almost completely rewritten to support Noetic and improve functionality.

## REQUIREMENTS

This code is valid only for [ROS Noetic](http://wiki.ros.org/noetic). For previous ROS distributions, please refer to the original repository: [leap_motion](https://github.com/ros-drivers/leap_motion).

On ROS Noetic, the `libLeap` package is not compatible with `rocpp`. Therefore, this package uses a Python wrapper that has been recompiled with SWIG to ensure compatibility with Python 3.

You should also have the Leap Motion SDK for Linux installed on your device.


## INSTALLATION

### Python API installation

The Python API is now mandatory for this package. It has been recompiled with SWIG to ensure compatibility with Python 3. You need to append the location of your LeapSDK to your environment variables. This step differs depending on where you saved the SDK. The LeapSDK folder should contain the following : `lib/Leap.py`, `lib/LeapPython.so`, `lib/libLeap.so`.

Example:

```bash
# 64-bit operating system
export PYTHONPATH=$PYTHONPATH:$HOME/LeapSDK/lib:$HOME/LeapSDK/lib
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/LeapSDK/lib:$HOME/LeapSDK/lib
```


### Usage

**1.** Just go to the src folder of your catkin workspace.

```bash
    cd ~/catkin_ws/src
    git clone https://github.com/ros-drivers/leap_motion.git
    cd ~/catkin_ws
    catkin_make
```

**2.** Start the Leap control panel in another terminal.

```bash
LeapControlPanel
```

**3.** (OPTIONAL) If it gives you an error about the leap daemon not running, stop the LeapControlPanel have a look [here](https://forums.leapmotion.com/t/error-in-leapd-malloc/4271/13) and use the following command:

```bash
sudo service leapd restart
```

**4.** Source your current catkin workspace.

```bash
source ~/catkin_ws/devel/setup.bash
```

**5.** Launch the visualizer_data.launch file to see if you have set everything up correctly. 

```bash
roslaunch leap_motion visualizer_data.launch
```

**6.** You are done! You should see an RViz window opening up displaying the detected hands from the controller.

