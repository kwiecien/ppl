#!/usr/bin/env python

import rospy
from geometry_msgs.msg import PointStamped
from people_msgs.msg import People
from tf import ExtrapolationException, LookupException, TransformListener


def callback_face_point_stamped(people_msg):
    publisher = rospy.Publisher(
        "face_point_stamped",
        PointStamped,
        queue_size=1
    )
    global transform_listener
    point = PointStamped()
    point.header = people_msg.header
    people = people_msg.people
    for person in people:
        point.point = person.position
        #point.point.z = 0
        print point
        #publisher.publish(point)
        print "transform: camera_rgb_optical_frame -> base_link"
        try:
            base_link_point = transform_listener.transformPoint("base_link", point)
            publisher.publish(base_link_point)
            print base_link_point
        except (LookupException, ExtrapolationException):
            continue


def listener():
    rospy.init_node('face_point_stamped', anonymous=False)
    global transform_listener
    transform_listener = TransformListener()
    rospy.Subscriber(
        "/face_people",
        People,
        callback_face_point_stamped,
        queue_size=1)
    rospy.spin()


if __name__ == '__main__':
    listener()
