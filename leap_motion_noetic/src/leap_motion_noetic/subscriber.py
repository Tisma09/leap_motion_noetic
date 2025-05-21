#!/usr/bin/env python3
import rospy
from leap_motion_msgs.msg import Hand
from geometry_msgs.msg import Vector3, Point



class Subscriber:
    def __init__(self):
        # Initialize the ROS node
        rospy.init_node('leap_sub_node', anonymous=True)

        # Subscriber
        self.sub_right_hand = rospy.Subscriber('leapmotion/right_hand', Hand, self.callback_hand)



    # Callback function for the subscriber
    def callback_hand(self, data):
        position = data.palm_center
        rospy.loginfo(rospy.get_name() + ": Leap ROS Position %s" % position)




def main():
    listener = Subscriber()
    rospy.spin()


if __name__ == '__main__':
    main()

    