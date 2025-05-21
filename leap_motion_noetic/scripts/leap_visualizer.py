#!/usr/bin/env python3

__author__ = 'Igor Zubrycki, Tismo'

import rospy
import tf
import PyKDL

from leap_motion_noetic.msg import Hand
from visualization_msgs.msg import Marker, MarkerArray

finger_names=["thumb","index","middle","ring","pinky"]
bones_names=["metacarpal","proximal","intermediate","distal"]
hand_ground_tf=PyKDL.Frame(PyKDL.Rotation.EulerZYX(0, 0, 0),PyKDL.Vector(0,0,0))



def make_kdl_frame(leap_basis_matrix,leap_position_vector,marker_ns):
    # Makes kdl frame from Leap Motion matrix and vector formats
    
    if marker_ns=="left_hand":
        leap_basis_matrix=list(leap_basis_matrix)
        leap_basis_matrix[0]=-leap_basis_matrix[0]
        leap_basis_matrix[1]=-leap_basis_matrix[1]
        leap_basis_matrix[2]=-leap_basis_matrix[2]
    leap_position_vector=[leap_position_vector.x, leap_position_vector.y, leap_position_vector.z]

    rotation_mat=PyKDL.Rotation(*leap_basis_matrix).Inverse()
    placement=PyKDL.Vector(*leap_position_vector)/1000.0 
    return PyKDL.Frame(rotation_mat,placement)
    

def relative_frame(frame_A,frame_B):
    return (frame_A.Inverse())*frame_B



class Visualizer:
    def __init__(self):
        # Initialize the ROS node
        rospy.init_node('visu_ctrl_node', anonymous=True)

        # Subscriber
        self.sub_right_hand = rospy.Subscriber('leapmotion/right_hand', Hand, lambda msg: self.callback_hand(msg, "right_hand"))
        self.sub_left_hand = rospy.Subscriber('leapmotion/left_hand', Hand, lambda msg: self.callback_hand(msg, "left_hand"))

        # Publisher
        self.marker_pub_left = rospy.Publisher('leapmotion/markers_left', MarkerArray, queue_size=1)
        self.marker_pub_right = rospy.Publisher('leapmotion/markers_right', MarkerArray, queue_size=1)

        # Param
        self.br = tf.TransformBroadcaster()

        


    def callback_hand(self, hand, hand_name):
        timenow = rospy.Time.now()
        # Create markers and broadcast transforms
        if hand.is_present:
            hand_dict, marker_array = self.make_tf_marker_dict(hand, hand_name, hand_name)

            
            for i, (tf_name, tf_array) in enumerate(hand_dict.items()):
                tf_matrix = tf_array[1]
                tf_prev_name = tf_array[0]

                self.br.sendTransform(tf_matrix.p, tf_matrix.M.GetQuaternion(), timenow, tf_name, tf_prev_name)

            if hand_name == "left_hand":
                self.marker_pub_left.publish(marker_array)
            elif hand_name == "right_hand":
                self.marker_pub_right.publish(marker_array)




    def make_tf_marker_dict(self, hand, hand_name, marker_ns):
        hand_dict={}
        marker_array = MarkerArray()

        hand_ground_name = hand_name + "_ground"
        hand_dict[hand_ground_name]=["ground",hand_ground_tf]
                
        hand_tf=make_kdl_frame(hand.basis.data,hand.palm_center,marker_ns)
        hand_dict[hand_name]=[hand_ground_name,hand_tf]

        id_bones=0
        for finger in hand.finger_list:
            if finger.lmc_finger_id == 9999 :
                continue
            finger_name=hand_name+"_"+finger_names[finger.type]
            
            prev_bone_name=hand_name
            for bone in finger.bone_list:
                if bone.type == 9 :
                    continue
                
                bone_absolute=make_kdl_frame(bone.basis.data,bone.bone_start,marker_ns)
                
                if bone.type==0:
                    bone_tf=relative_frame(hand_tf,bone_absolute)
                else:
                    bone_tf=relative_frame(prev_bone_absolute,bone_absolute)

                bone_name=finger_name+"_"+bones_names[bone.type]
                hand_dict[bone_name]=[prev_bone_name,bone_tf]

                # Markers for visualization
                marker = self.create_marker(
                    bone_tf, id_bones, marker_ns, Marker.CYLINDER, 
                    scale=[bone.width/1000, bone.width/1000, bone.length/1000], color=[0.0, 1.0, 0.0, 1.0], parent_frame=prev_bone_name
                )
                marker_array.markers.append(marker)
                
                # Update previous bone
                prev_bone_name=bone_name
                prev_bone_absolute=bone_absolute
                id_bones +=1

                
                
            tip=PyKDL.Frame(PyKDL.Rotation(1,0,0, 0,1,0, 0,0,1),PyKDL.Vector(0,0,-bone.length/1000))
            hand_dict[finger_name+"_tip"]=[prev_bone_name,tip]    
        return hand_dict, marker_array  


    @staticmethod
    def create_marker(frame, marker_id, marker_ns, marker_type, scale, color, parent_frame):
        marker = Marker()
        marker.header.frame_id = parent_frame
        marker.header.stamp = rospy.Time.now()
        marker.ns = marker_ns
        marker.id = marker_id
        marker.type = marker_type
        marker.action = Marker.ADD
        marker.pose.position.x = frame.p[0]
        marker.pose.position.y = frame.p[1]
        marker.pose.position.z = frame.p[2]
        q = frame.M.GetQuaternion()
        marker.pose.orientation.x = q[0]
        marker.pose.orientation.y = q[1]
        marker.pose.orientation.z = q[2]
        marker.pose.orientation.w = q[3]
        marker.scale.x = scale[0]
        marker.scale.y = scale[1]
        marker.scale.z = scale[2]
        marker.color.r = color[0]
        marker.color.g = color[1]
        marker.color.b = color[2]
        marker.color.a = max(color[3], 0.5)
        marker.lifetime = rospy.Duration(0.5)
        return marker



def main():
    visu = Visualizer()
    rospy.spin()


if __name__ == '__main__':
    main()
