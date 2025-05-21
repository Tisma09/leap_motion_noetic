#!/usr/bin/env python3

# Set (append) your PYTHONPATH properly, or just fill in the location of your LEAP
# SDK folder, e.g., $HOME/LeapSDK/lib where the Leap.py lives and /LeapSDK/lib/x64 or
# x86 where the *.so files reside.

import threading
import time
import Leap
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

from leap_motion_msgs.msg import Frame, Finger, Bone, Hand, Arm, Gesture
from geometry_msgs.msg import Vector3, Point
from std_msgs.msg import Float64MultiArray




class LeapBone():
    def __init__(self):

        # For Skeleton sender :
        self.basis = Leap.Matrix()
        self.prev_joint = Leap.Vector()

        self.msg = Bone()
        self.msg.type = 9
        self.msg.length = 0.0
        self.msg.width = 0.0
        self.msg.basis = Float64MultiArray()
        self.msg.bone_start = Point(0,0,0)
        self.msg.bone_end = Point(0,0,0)
        self.msg.center = Point(0,0,0)
        self.msg.to_string = "Bone"
                


    def update(self, bone):

        # For Skeleton sender :
        self.basis = bone.basis
        self.prev_joint = bone.prev_joint

        self.msg.type = bone.type
        self.msg.width = bone.width
        self.msg.length = bone.length
        self.msg.basis.data = bone.basis.to_array_3x3()
        self.msg.bone_start = Point(bone.prev_joint.x, bone.prev_joint.y, bone.prev_joint.z)
        self.msg.bone_end = Point(bone.next_joint.x, bone.next_joint.y, bone.next_joint.z)
        self.msg.center = Point(bone.center.x, bone.center.y, bone.center.z)





class LeapFinger():
    def __init__(self):
        self.boneNames = ['metacarpal', 'proximal', 'intermediate', 'distal']
        for boneName in self.boneNames:
            setattr(self, boneName, LeapBone())
        self.tip = [0.0, 0.0, 0.0]

        self.msg = Finger()
        self.msg.lmc_finger_id = 9999
        self.msg.type = 9
        self.msg.length = 0.0
        self.msg.width = 0.0
        self.msg.to_string = "Finger"

        self.msg.bone_list = [getattr(self, name).msg for name in self.boneNames]
                


    def update(self, finger):
        for boneName in self.boneNames:
            # Get the base of each bone
            bone = finger.bone(getattr(Leap.Bone, 'TYPE_%s' % boneName.upper()))
            getattr(self, boneName).update(bone)
        # For the tip, get the end of the distal bone
        self.tip = finger.bone(Leap.Bone.TYPE_DISTAL).next_joint.to_float_array()


        self.msg.lmc_finger_id = finger.id
        self.msg.type = finger.type
        self.msg.length = finger.length
        self.msg.width = finger.width

        self.msg.bone_list = [getattr(self, name).msg for name in self.boneNames]











class LeapHand():
    def __init__(self):
        self.fingerNames = ['thumb', 'index', 'middle', 'ring', 'pinky']
        for fingerName in self.fingerNames:
            setattr(self, fingerName, LeapFinger())

        # For Skeleton sender :
        self.basis = Leap.Matrix()
        self.palm_position = Leap.Vector()

        #self.arm = LeapArm()

        self.msg = Hand()
        self.msg.lmc_hand_id = 9999
        self.msg.is_present = False
        self.msg.time_visible = 0.0
        self.msg.confidence = 0.0
        self.msg.roll = 0.0
        self.msg.pitch = 0.0
        self.msg.yaw = 0.0
        self.msg.direction = Vector3(0,0,0)
        self.msg.normal = Vector3(0,0,0)
        self.msg.grab_strength = 0.0
        self.msg.pinch_strength = 0.0
        self.msg.basis = Float64MultiArray()
        self.msg.palm_velocity = Vector3(0,0,0)
        self.msg.palm_center = Point(0,0,0)
        self.msg.palm_width = 0.0
        self.msg.sphere_radius = 0.0
        self.msg.sphere_center = Point(0,0,0)
        self.msg.to_string = "Hand"

        self.msg.finger_list = [getattr(self, name).msg for name in self.fingerNames]
        #self.msg.arm = self.arm.msg



    def update(self, hand):
        if not hand.fingers.is_empty:
            for fingerName in self.fingerNames:
                finger = hand.fingers.finger_type(getattr(Leap.Finger, 'TYPE_%s' % fingerName.upper()))[0]
                getattr(self, fingerName).update(finger)

        # For Skeleton sender :
        self.basis = hand.basis
        self.palm_position = hand.palm_position

        #self.arm.update(hand.arm)

        self.msg.lmc_hand_id = hand.id
        self.msg.is_present = True
        self.msg.time_visible = hand.time_visible
        self.msg.confidence = hand.confidence
        self.msg.roll = hand.palm_normal.roll * Leap.RAD_TO_DEG
        self.msg.pitch = hand.palm_normal.pitch * Leap.RAD_TO_DEG
        self.msg.yaw = hand.palm_normal.yaw * Leap.RAD_TO_DEG
        self.msg.direction = Vector3(hand.direction.x, hand.direction.y, hand.direction.z)
        self.msg.normal = Vector3(hand.palm_normal.x, hand.palm_normal.y, hand.palm_normal.z)
        self.msg.grab_strength = hand.grab_strength
        self.msg.pinch_strength = hand.pinch_strength
        self.msg.basis.data = hand.basis.to_array_3x3()
        self.msg.palm_velocity = Vector3(hand.palm_velocity.x, hand.palm_velocity.y, hand.palm_velocity.z)
        self.msg.palm_center = Point(hand.palm_position.x, hand.palm_position.y, hand.palm_position.z)
        self.msg.palm_width = hand.palm_width
        self.msg.sphere_radius = hand.sphere_radius
        self.msg.sphere_center = Point(hand.sphere_center.x, hand.sphere_center.y, hand.sphere_center.z)
        
        self.msg.finger_list = [getattr(self, name).msg for name in self.fingerNames]
        #self.msg.arm = self.arm.msg









class LeapFrame():
    def __init__(self):
        self.right_hand = LeapHand()
        self.left_hand = LeapHand()
        self.gestures = None

        self.msg = Frame()
        self.msg.lmc_frame_id = 9999
        self.msg.nr_of_fingers = 0
        self.msg.nr_of_hands = 0
        self.msg.nr_of_gestures = 0
        self.msg.current_frames_per_second = 0.0
        self.msg.to_string = "Frame"
        #self.msg.right_hand = self.right_hand.msg
        #self.msg.left_hand = self.right_hand.msg

    def update(self, controller):
        _frame = controller.frame() # Local Object
        there_is_right_hand, there_is_left_hand = False, False
        for hand in _frame.hands:
            if hand.is_right:
                there_is_right_hand=True
                self.right_hand.update(hand)
            elif hand.is_left:
                there_is_left_hand=True
                self.left_hand.update(hand)
        
        self.right_hand.msg.is_present = there_is_right_hand
        self.left_hand.msg.is_present = there_is_left_hand
        self.gestures = _frame.gestures()

        self.msg.lmc_frame_id = _frame.id
        self.msg.nr_of_fingers = len(_frame.fingers)
        self.msg.nr_of_hands = len(_frame.hands)
        self.msg.nr_of_gestures = len(_frame.gestures())
        self.msg.current_frames_per_second = _frame.current_frames_per_second

        #self.msg.right_hand = self.right_hand.msg
        #self.msg.left_hand = self.right_hand.msg


    def gesture_type(self, controller):
        # Gestures
        for gesture in self.gestures():
            if gesture.type == Leap.Gesture.TYPE_CIRCLE:
                circle = CircleGesture(gesture)

                # Determine clock direction using the angle between the pointable and the circle normal
                if circle.pointable.direction.angle_to(circle.normal) <= Leap.PI/4:
                    clockwiseness = "clockwise"
                else:
                    clockwiseness = "counterclockwise"

                # Calculate the angle swept since the last frame
                swept_angle = 0
                if circle.state != Leap.Gesture.STATE_START:
                    previous_update = CircleGesture(controller.frame(1).gesture(circle.id))
                    swept_angle =  (circle.progress - previous_update.progress) * 2 * Leap.PI

                print("Circle id: %d, %s, progress: %f, radius: %f, angle: %f degrees, %s" % (
                        gesture.id, self.state_string(gesture.state),
                        circle.progress, circle.radius, swept_angle * Leap.RAD_TO_DEG, clockwiseness))

            if gesture.type == Leap.Gesture.TYPE_SWIPE:
                swipe = SwipeGesture(gesture)
                print("Swipe id: %d, state: %s, position: %s, direction: %s, speed: %f" % (
                        gesture.id, self.state_string(gesture.state),
                        swipe.position, swipe.direction, swipe.speed))

            if gesture.type == Leap.Gesture.TYPE_KEY_TAP:
                keytap = KeyTapGesture(gesture)
                print("Key Tap id: %d, %s, position: %s, direction: %s" % (
                        gesture.id, self.state_string(gesture.state),
                        keytap.position, keytap.direction ))

            if gesture.type == Leap.Gesture.TYPE_SCREEN_TAP:
                screentap = ScreenTapGesture(gesture)
                print("Screen Tap id: %d, %s, position: %s, direction: %s" % (
                        gesture.id, self.state_string(gesture.state),
                        screentap.position, screentap.direction ))


    def state_string(state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"







class LeapInterface(Leap.Listener):
    def on_init(self, controller):
        self.frame = LeapFrame()
        print("Initialized Leap Motion Device")

    def on_connect(self, controller):
        print("Connected to Leap Motion Controller")

        # Enable gestures
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);

    def on_disconnect(self, controller):
        print("Disconnected Leap Motion")

    def on_exit(self, controller):
        print("Exited Leap Motion Controller")

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        self.frame.update(controller)



class Runner(threading.Thread):

    def __init__(self,arg=None):
        threading.Thread.__init__(self)
        self.arg=arg
        self.running = True
        self.listener = LeapInterface()
        self.controller = Leap.Controller()
        self.controller.add_listener(self.listener)

    def stop(self):
        self.running = False
        self.controller.remove_listener(self.listener)

    def run (self):
        while self.running :
            # Save some CPU time
            time.sleep(0.001)

