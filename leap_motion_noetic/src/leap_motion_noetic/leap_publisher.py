#!/usr/bin/env python3
import rospy
import sys
import select
import termios
import tty

import leap_motion_noetic.leap_interface as leap_interface

from std_msgs.msg import String
FREQUENCY_ROSTOPIC_DEFAULT = 100.0
NODENAME = 'leap_pub_node'
PARAMNAME_FREQ = 'freq'
PARAMNAME_FREQ_ENTIRE = '/' + NODENAME + '/' + PARAMNAME_FREQ



def sender():
    '''
    This method publishes the data of leap
    '''
    rospy.init_node(NODENAME)
    rospy.loginfo("Parameter set on server: PARAMNAME_FREQ={}".format(rospy.get_param(PARAMNAME_FREQ_ENTIRE, FREQUENCY_ROSTOPIC_DEFAULT)))

    li = leap_interface.Runner()
    li.setDaemon(True)
    li.start()

    global settings
    settings = termios.tcgetattr(sys.stdin)

    pub_human = rospy.Publisher('leapmotion/frame', leap_interface.Frame, queue_size=1)
    pub_right_hand = rospy.Publisher('leapmotion/right_hand', leap_interface.Hand, queue_size=1)
    pub_left_hand = rospy.Publisher('leapmotion/left_hand', leap_interface.Hand, queue_size=1)

    rate = rospy.Rate(rospy.get_param(PARAMNAME_FREQ_ENTIRE, FREQUENCY_ROSTOPIC_DEFAULT))

    while not rospy.is_shutdown():

        pub_human.publish(li.listener.frame.msg)
        pub_right_hand.publish(li.listener.frame.right_hand.msg)
        pub_left_hand.publish(li.listener.frame.left_hand.msg)

        rate.sleep()

    li.stop()
    li.join()


def main():
    try:
        sender()
    except rospy.ROSInterruptException:
        pass


if __name__ == '__main__':
    main()

