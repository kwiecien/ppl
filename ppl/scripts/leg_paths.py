#!/usr/bin/env python

import datetime

import rospy
from geometry_msgs.msg import PointStamped
from people_msgs.msg import People
from tf import ExtrapolationException, LookupException, TransformListener

FILE = file
RECORDED_PEOPLE = dict()


def listener():
    global transform_listener
    transform_listener = TransformListener()
    rospy.Subscriber(
        "/leg_people",
        People,
        callbackPplPaths,
        queue_size=1)
    rospy.spin()


def callbackPplPaths(people_msg):
    writeToFile(people_msg)


def createFile():
    global FILE
    time = datetime.datetime.now()
    name = "/home/krzysztof/catkin_ws/src/ppl/paths/" + \
           "leg_" + '{:%Y-%m-%d-%H-%M-%S}'.format(time) + ".dat"
    FILE = open(name, 'w')


def writeToFile(people_msg):
    if len(people_msg.people) == 0:
        return
    writeTime(people_msg.header.stamp)
    writeTime(countMeasuredTime(people_msg.header.stamp))
    updatePeoplePositions(people_msg)
    writePeoplePositions()


def writeTime(time):
    FILE.write(str(time))
    FILE.write('\t')


def countMeasuredTime(timestamp):
    time = timestamp.to_sec()
    time = round(time, 2)
    return time


def updatePeoplePositions(people_msg):
    global transform_listener
    for person in RECORDED_PEOPLE:
        RECORDED_PEOPLE[person] = ['"1/0"', '"1/0"']
    for person in people_msg.people:
        point = PointStamped()
        point.header = people_msg.header
        point.point = person.position
        try:
            base_link_point = transform_listener.transformPoint("base_link", point)
            if person.name not in RECORDED_PEOPLE:
                RECORDED_PEOPLE[person.name] = []
            RECORDED_PEOPLE[person.name] = [base_link_point.point.x, base_link_point.point.y]
        except (LookupException, ExtrapolationException):
            continue


def writePeoplePositions():
    i = 1
    for person in RECORDED_PEOPLE:
        writePosition(RECORDED_PEOPLE[person], i)
        i += 1
    FILE.write('\n')
    print "------------------------------------"


def writePosition(position, i):
    x = position[0]
    y = position[1]
    print "Person", i, "[x, y]", x, y
    FILE.write(str(y))
    FILE.write('\t')
    FILE.write(str(x))
    FILE.write('\t')


if __name__ == '__main__':
    rospy.init_node('leg_paths', anonymous=False)
    createFile()
    listener()
