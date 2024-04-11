#!/usr/bin/env python3

import rospy
from std_msgs.msg import Float64MultiArray
import smbus

DCA = 0
DCB = 0
X = 0
Y = 0
address = 0x48
bus = smbus.SMBus(1)
cmd = 0x40


def analogRead(chn):
    bus.write_byte(address, cmd + chn)
    value = bus.read_byte(address)
    return value


def analogWrite(value):
    bus.write_byte_data(address, cmd, value)


def map_value(value, fromlow, fromhigh, tolow, tohigh):
    scale = (tohigh - tolow) / (fromhigh - fromlow)
    mapped_value = (value - fromlow) * scale + tolow
    return mapped_value


def talker():
    pub = rospy.Publisher('motor_speed', Float64MultiArray, queue_size=10)
    rospy.init_node('rasp_talker', anonymous=True)
    rate = rospy.Rate(10)  # Tần số gửi dữ liệu (10Hz)
    while not rospy.is_shutdown():

        # # Lấy tín hiệu từ joystick
        Y = analogRead(0)
        X = analogRead(1)

        if Y < 37:
            Y=37
        elif Y>251:
            Y = 251

        if X < 33:
            X = 33
        elif X > 235:
            X = 235

        val_Y = map_value(Y, 37, 251, 0, 255)
        val_X = map_value(X, 33, 235, 0, 255)
        print("Y = %d, X = %d" % (val_Y, val_X))


        if val_Y > 210: #tien
            DCA = 0.15
            DCB = -0.15
            if val_X > 220:
                DCA = 0.05
                DCB = 0.05
            elif val_X < 190:
                DCA = -0.05
                DCB = -0.05
        elif val_Y < 185: #lui
            DCA = -0.15
            DCB = 0.15
            if val_X > 220:
                DCA = 0.05
                DCB = 0.05
            elif val_X < 190:
                DCA = -0.05
                DCB = -0.05
        if val_X > 220:
            DCA = 0.05
            DCB = 0.05
        elif val_X < 190:
            DCA = -0.05
            DCB = -0.05

        if (val_Y < 210 and val_Y > 185) and (val_X < 220 and val_X > 190):
            DCA = 0
            DCB = 0

        # Tạo message Float64MultiArray
        motor_speed_msg = Float64MultiArray()

        # Gán giá trị vận tốc cho 2 động cơ
        motor_speed_msg.data = [DCA, DCB]

        # In giá trị vận tốc ra màn hình
        rospy.loginfo("Motor speeds: {}".format(motor_speed_msg.data))

        # Gửi message tới topic "motor_speed"
        pub.publish(motor_speed_msg)

        rate.sleep()


if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
