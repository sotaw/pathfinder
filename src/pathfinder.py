#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
import tf
import mecbot
from geometry_msgs.msg import Twist

g_vcx_val = 0.0
g_vcr_val = 0.0


def cmd_vel_callback(msg):
    global g_vcx_val
    global g_vcr_val
    g_vcx_val = msg.linear.x
    g_vcr_val = msg.angular.z


def main():
    rospy.init_node("pathfinder")
    cmd_vel_sub = rospy.Subscriber("cmd_vel", Twist, cmd_vel_callback)
    rate = rospy.Rate(30)
    mb = mecbot.Mecbot("/dev/ttyUSB1", 57600)
    br = tf.TransformBroadcaster()

    vcx_last = 0.0
    vcr_last = 0.0

    last_x = 0.0
    last_y = 0.0
    last_theta = 0.0

    while not rospy.is_shutdown():
        pulse_count = None
        try:
            pulse_count = mb.measure_pulse()
        except mecbot.MecbotMeasureError:
            pass
        else:
            calc_result = mb.calc_pos(last_x, last_y, last_theta, pulse_count[2], pulse_count[3])
            last_x = calc_result[0]
            last_y = calc_result[1]
            last_theta = calc_result[2]
            br.sendTransform((last_x, last_y, 0),
                             tf.transformations.quaternion_from_euler(0, 0, last_theta),
                             rospy.Time.now(),
                             "pathfinder",
                             "map")

        vcx_buf = g_vcx_val
        vcr_buf = g_vcr_val

        if vcx_buf != vcx_last:
            mb.control_forward_speed(vcx_buf)
            vcx_last = vcx_buf
        if vcr_buf != vcr_last:
            mb.control_turning_speed(vcr_buf)
            vcr_last = vcr_buf

        rate.sleep()
    rospy.spin()


if __name__ == "__main__":
    main()