#!/usr/bin/env python3
import rospy
import sys
import select
import termios
import tty

import leap_motion_noetic.leap_interface as leap_interface

from std_msgs.msg import String

FREQUENCY_ROSTOPIC_DEFAULT = 0.01
NODENAME = 'leap_pub_node'
PARAMNAME_FREQ = 'freq'
PARAMNAME_FREQ_ENTIRE = '/' + NODENAME + '/' + PARAMNAME_FREQ



def get_key():
    tty.setraw(sys.stdin.fileno()) 
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key




def sender():
    '''
    This method publishes the data of leap
    '''
    rospy.loginfo("Parameter set on server: PARAMNAME_FREQ={}".format(rospy.get_param(PARAMNAME_FREQ_ENTIRE, FREQUENCY_ROSTOPIC_DEFAULT)))

    li = leap_interface.Runner()
    li.setDaemon(True)
    li.start()

    global settings
    settings = termios.tcgetattr(sys.stdin)

    pub_human = rospy.Publisher('leapmotion/frame', leap_interface.Frame, queue_size=5)
    pub_right_hand = rospy.Publisher('leapmotion/right_hand', leap_interface.Hand, queue_size=5)
    pub_left_hand = rospy.Publisher('leapmotion/left_hand', leap_interface.Hand, queue_size=5)
    #pub_right_hand_pos = rospy.Publisher('leapmotion/right_hand/position', leap_interface.Point, queue_size=5)
    #pub_left_hand_pos = rospy.Publisher('leapmotion/left_hand/position', leap_interface.Point, queue_size=5)
    pub_key = rospy.Publisher('keyboard/key_pressed', String, queue_size=5)

    rospy.init_node(NODENAME)

    while not rospy.is_shutdown():

        pub_human.publish(li.listener.frame.msg)
        pub_right_hand.publish(li.listener.frame.right_hand.msg)
        pub_left_hand.publish(li.listener.frame.left_hand.msg)
        #pub_right_hand_pos.publish(li.listener.frame.right_hand.msg.palm_center)
        #pub_left_hand_pos.publish(li.listener.frame.left_hand.msg.palm_center)

        key = get_key()
        if key == '\x03':  # Ctrl-C
            break
        elif key :
            rospy.loginfo("Key pressed !")
            pub_key.publish(key)
        
        rospy.sleep(rospy.get_param(PARAMNAME_FREQ_ENTIRE, FREQUENCY_ROSTOPIC_DEFAULT))

    li.stop()
    li.join()


def main():
    try:
        sender()
    except rospy.ROSInterruptException:
        pass


if __name__ == '__main__':
    main()

