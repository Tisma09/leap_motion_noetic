#!/usr/bin/env python3

__author__ = 'Igor Zubrycki, upadate by Tismo'

import leap_interface

import rospy
import tf
import math
import rospy
import PyKDL
from visualization_msgs.msg import Marker, MarkerArray


finger_names=["thumb","index","middle","ring","pinky"]
bones_names=["metacarpal","proximal","intermediate","distal"]
hand_ground_tf=PyKDL.Frame(PyKDL.Rotation.EulerZYX(0, 0, math.pi/2.0),PyKDL.Vector(0,0,0))


def make_kdl_frame(leap_basis_matrix,leap_position_vector,is_left=False):
    # Makes kdl frame from Leap Motion matrix and vector formats
    
    if is_left:
       basis=([-el for el in leap_basis_matrix.x_basis.to_float_array()]+
       leap_basis_matrix.y_basis.to_float_array()+
       leap_basis_matrix.z_basis.to_float_array())
       
    else:
       basis=leap_basis_matrix.to_array_3x3() 
    rotation_mat=PyKDL.Rotation(*basis).Inverse()
    placement=PyKDL.Vector(*leap_position_vector.to_float_array())/1000.0 #to m
    return PyKDL.Frame(rotation_mat,placement)
    
def relative_frame(frame_A,frame_B):

    return (frame_A.Inverse())*frame_B





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





def make_tf_marker_dict(hand, hand_name, marker_ns):
    
    hand_dict={}
    hand_dict["hand_ground"]=["ground",hand_ground_tf]
    marker_array = MarkerArray()
    
            
    hand_tf=make_kdl_frame(hand.basis,hand.palm_position,hand.is_left)
    hand_dict[hand_name]=["hand_ground",hand_tf]
    id_bones=0
    for finger in hand.fingers:
        finger_name=hand_name+"_"+finger_names[finger.type]
        
        prev_bone_name=hand_name
        for num in range(0,4):
            
            bone=finger.bone(num)

            bone_absolute=make_kdl_frame(bone.basis,bone.prev_joint,hand.is_left)
            if num==0:
                bone_tf=relative_frame(hand_tf,bone_absolute)
            else:
                bone_tf=relative_frame(prev_bone_absolute,bone_absolute)

            bone_name=finger_name+"_"+bones_names[num]
            hand_dict[bone_name]=[prev_bone_name,bone_tf]

            # Markers for visualization
            marker_id = id_bones
            marker = create_marker(
                bone_tf, marker_id, marker_ns, Marker.CYLINDER, 
                scale=[20/1000, 20/1000, bone.length/1000], color=[0.0, 1.0, 0.0, 1.0], parent_frame=prev_bone_name
            )
            marker_array.markers.append(marker)
            
            # Update previous bone
            prev_bone_name=bone_name
            prev_bone_absolute=bone_absolute
            id_bones +=1

            
            
        tip=PyKDL.Frame(PyKDL.Rotation(1,0,0, 0,1,0, 0,0,1),PyKDL.Vector(0,0,-bone.length/1000.0))
        hand_dict[finger_name+"_tip"]=[prev_bone_name,tip]    
    return hand_dict, marker_array
     # now sending to ROS       
        



def broadcast_hand(hand, hand_name, timenow, marker_pub, br):
    try:
        hand_dict, marker_array = make_tf_marker_dict(hand, hand_name, hand_name)
    except Exception as e:
        rospy.logerr(f"Error in make_tf_marker_dict: {e}")
        return
    

    for i, (tf_name, tf_array) in enumerate(hand_dict.items()):
        tf_matrix = tf_array[1]
        tf_prev_name = tf_array[0]
        br.sendTransform(tf_matrix.p, tf_matrix.M.GetQuaternion(), timenow, tf_name, tf_prev_name)

    marker_pub.publish(marker_array)




def sender():
    li = leap_interface.Runner()
    li.setDaemon(True)
    li.start()
    rospy.init_node('leap_skeleton_pub')

    marker_pub_left = rospy.Publisher('leapmotion/markers_left', MarkerArray, queue_size=1)
    marker_pub_right = rospy.Publisher('leapmotion/markers_right', MarkerArray, queue_size=1)
    br = tf.TransformBroadcaster()

    while not rospy.is_shutdown():
        timenow = rospy.Time.now()
        if li.listener.left_hand:
            try:
                broadcast_hand(li.listener.left_hand, "left_hand", timenow, marker_pub_left, br)
            except Exception as e:
                rospy.logerr(f"Error in broadcast left: {e}")
                return
            
        if li.listener.right_hand:
            try:
                broadcast_hand(li.listener.right_hand, "right_hand", timenow, marker_pub_right, br)
            except Exception as e:
                rospy.logerr(f"Error in broadcast right: {e}")
                return

        # save some CPU time, circa 100Hz publishing.
        rospy.sleep(0.01)


if __name__ == '__main__':
    try:
        sender()
    except rospy.ROSInterruptException:
        pass
