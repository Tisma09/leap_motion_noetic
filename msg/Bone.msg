std_msgs/Header header

# The name of this bone. 
uint8 type

# The estimated length of the bone in meters.
float32 length

# The estimated with of the bone in meters.
float32 width

# A string containing a brief, human readable description of the Bone object. 
string to_string

# The base of the bone, closest to the wrist. 
geometry_msgs/Point bone_start

# The end of the bone, closest to the finger tip. 
geometry_msgs/Point bone_end

# The midpoint of the bone. 
geometry_msgs/Point center
