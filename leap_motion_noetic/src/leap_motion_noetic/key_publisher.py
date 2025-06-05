#!/usr/bin/env python3

import sys, termios, tty, select
import rospy
from std_msgs.msg import String



def get_key_non_blocking(timeout=0.01):
    dr, _, _ = select.select([sys.stdin], [], [], timeout)
    if dr:
        return sys.stdin.read(1)
    return None



def main():
    """
    Main function to initialize the ROS node and publish key presses.
    """
    settings = termios.tcgetattr(sys.stdin)
    rospy.init_node('keyboard_node')
    pub = rospy.Publisher('keyboard/key_pressed', String, queue_size=1)

    try:
        tty.setcbreak(sys.stdin.fileno()) 
        while not rospy.is_shutdown():
            key = get_key_non_blocking()

            if key == '\x03':  # Ctrl-C
                break
            elif key:
                pub.publish(key)
                rospy.loginfo(f"Key pressed: {repr(key)}")

            rospy.sleep(0.01)

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        print("\n🛑 Keyboard node exited cleanly.")


        
if __name__ == '__main__':
    main()
