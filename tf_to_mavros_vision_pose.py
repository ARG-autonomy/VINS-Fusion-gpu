#!/usr/bin/env python
import rospy
import tf
from geometry_msgs.msg import PoseStamped

def main():
    rospy.init_node('tf_to_vision_pose_publisher')

    listener = tf.TransformListener()
    pub = rospy.Publisher('/mavros/vision_pose/pose', PoseStamped, queue_size=10)

    rate = rospy.Rate(10.0)  # Match VINS rate

    target_frame = "world"
    source_frame = "body"

    rospy.loginfo("Waiting for transform from '%s' to '%s'...", target_frame, source_frame)
    try:
        listener.waitForTransform(target_frame, source_frame, rospy.Time(0), rospy.Duration(10.0))
        rospy.loginfo("Transform available. Starting publishing loop.")
    except tf.Exception as e:
        rospy.logerr("Transform unavailable: %s", str(e))
        return

    while not rospy.is_shutdown():
        try:
            now = rospy.Time.now()
            listener.waitForTransform(target_frame, source_frame, now, rospy.Duration(0.5))
            (trans, rot) = listener.lookupTransform(target_frame, source_frame, now)

            pose_msg = PoseStamped()
            pose_msg.header.stamp = now
            pose_msg.header.frame_id = target_frame

            pose_msg.pose.position.x = trans[0]
            pose_msg.pose.position.y = trans[1]
            pose_msg.pose.position.z = trans[2]

            pose_msg.pose.orientation.x = rot[0]
            pose_msg.pose.orientation.y = rot[1]
            pose_msg.pose.orientation.z = rot[2]
            pose_msg.pose.orientation.w = rot[3]

            pub.publish(pose_msg)

        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException) as e:
            rospy.logwarn_throttle(5.0, "TF lookup failed: %s", str(e))

        rate.sleep()

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass
