#!/usr/bin/env python3


import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from geometry_msgs.msg import Point
from nav_msgs.msg import Odometry
import tf
from math import atan2
from math import degrees
from math import sqrt
import message_filters
from sensor_msgs.msg import LaserScan





oriented = False
obstacle_flag = 0
turn = False
rdis = 0
corner = False
count = 0
blockd = False
right = False
left = False
adjust = False
stuck = False
msg = None
dt = None






def callback():
    print('IN CALLBACK')
    global oriented, obstacle_flag, rdis, turn, corner, count, blocked, left, right, adjust, stuck, dt, msg
    # if not input_gathered:
    #     input_gather()
    #     input_gathered = True

    print('-------------------------------------------')
    print ('Range data at straight ahead:   {}'.format(dt.ranges[0]))
    print ('Range data at right:  {}'.format(dt.ranges[90])) 
    print ('Range data at left: {}'.format(dt.ranges[270])) #was 878



    

    # Publisher object that decides what kind of topic to publish and how fast.
    cmd_vel_pub = rospy.Publisher("/cmd_vel", Twist, queue_size=100)

    # We will be sending commands of type "twist"
    com = Twist();
    thr = 1.5
    thr2 = 0.4
    rate = rospy.Rate(50)
    # # The main loop will run at a rate of 50Hz, i.e., 50 times per second.
    x = msg.pose.pose.position.x #current x position
    y = msg.pose.pose.position.y #current y position

    #finding correct pose




    goal = Point()
    goal.x = 3
    goal.y = 1.5
    desired_pose = 0
    (roll, pitch, yaw) = tf.transformations.euler_from_quaternion([msg.pose.pose.orientation.x, msg.pose.pose.orientation.y, msg.pose.pose.orientation.z, msg.pose.pose.orientation.w])

    inc_x = goal.x - x
    inc_y = goal.y - y
    angle_to_goal = atan2(inc_y, inc_x)
    distance_to_goal = sqrt((inc_x * inc_x) + (inc_y * inc_y))
    print("Distance to goal: {}".format(distance_to_goal))
    print("angle to goal: " + str(angle_to_goal))
    print("yaw: " + str(yaw))

    if not oriented:
        if abs(angle_to_goal - yaw) < 0.2:
            oriented = True
        else:
            com.linear.x = 0
            com.angular.z = 0.4  
    
    
    


    else:

        if dt.ranges[0] < 10 and dt.ranges[0] < distance_to_goal and oriented:
            blocked = True
        else:
            blocked = False

        #if (dt.ranges[540] < thr or dt.ranges[191] < thr) and dt.ranges[540] < distance_to_goal: #obstacle ahead
        if (dt.ranges[0] < thr) and dt.ranges[0] < distance_to_goal: #obstacle ahead

            obs = True
        else:
            obs = False

        if not obs and obstacle_flag == 0 and oriented and not corner and not adjust and not stuck:
            
            if blocked and dt.ranges[45] < thr: #obstacle approaching on right side
                obstacle_flag = 1
                turn = True
                right = True
                print('blocked_turn')
                count = 0
            if blocked and dt.ranges[315] < thr: #obstacle approaching on left side
                obstacle_flag = 1
                turn = True
                left = True
                count = 0
                print('blocked left')

            if abs(angle_to_goal - yaw) > 0.2:
                oriented = False
                print("1")
            else:
                com.linear.x = 0.2
                com.angular.z = 0.0
                print("2")

        elif adjust:
            if left:
                if count < 20: #turn left
                    com.angular.z = -0.3
                    com.linear.x = 0.0
                elif count >= 20 and count < 40: #head straight
                    com.linear.x = 0.2
                    com.angular.z = 0.0
                else: #turn back right
                    com.angular.z = 0.3
                    com.linear.x = 0.0
                count +=1
                if count == 60:
                    adjust = False
                print('adjust')

            else:
                if count < 20: #turn left
                    com.angular.z = 0.3
                    com.linear.x = 0.0
                elif count >= 20 and count < 40: #head straight
                    com.linear.x = 0.2
                    com.angular.z = 0.0
                else: #turn back right
                    com.angular.z = -0.3
                    com.linear.x = 0.0
                count +=1
                if count == 60:
                    adjust = False
                print('adjust')
                

        elif corner:
            if(dt.ranges[0] < thr): #obstacle ahead, we're done here
                oriented = False
                corner = False
            else:
                if left:
                    if count < 20: #go straight past corner
                        com.linear.x = 0.2
                        com.angular.z = 0.0 

                    elif count >= 20 and count < 70: #turn left
                        com.linear.x = 0.0
                        com.angular.z = 0.3

                    else: #head straight for a little bit
                        com.linear.x = 0.2
                        com.angular.z = 0.0

                    count += 1
                    if count == 110:
                        corner = False
                        oriented = False
                        left = False
                    print("5 left")
                
                else:
                    if count < 20: #go straight past corner
                        com.linear.x = 0.2
                        com.angular.z = 0.0 

                    elif count >= 20 and count < 70: #turn right
                        com.linear.x = 0.0
                        com.angular.z = -0.3

                    else: #head straight for a little bit
                        com.linear.x = 0.2
                        com.angular.z = 0.0

                    count += 1
                    if count == 110:
                        corner = False
                        oriented = False
                        right = False
                    print("5 right")


        elif stuck: 
            if count < 25: #turn left
                com.angular.z = -0.3
                com.linear.x = 0.0
            elif count >= 25:  #head straight
                com.angular.z = 0.0
                com.linear.x = 0.2
            count+=1
            if count == 50:
                stuck = False
                oriented = False
            print('adjusting since stuck')
            


        else: #obstacle avoidance
            obstacle_flag = 1
            if not turn: 
                if dt.ranges[348] < dt.ranges[12] and dt.ranges[348] < thr:
                    left = True
                    print("just made it left")
                else:
                    right = True

            print("rdis: " + str(rdis))
            if dt.ranges[0] < thr or dt.ranges[90] < thr2 or turn: #obstacle ahead
                if turn and count == 400:
                    stuck = True
                    count = 0
                    obstacle_flag = 0
                if not left: #obstacle ahead or approaching on right, turn left
                    if not turn:
                        turn = True
                        com.angular.z = 0.2
                        count = 0
                    elif(abs(dt.ranges[88] - dt.ranges[92]) < 0.002 ): #done turning
                        turn = False
                        rdis = dt.ranges[90]
                        if rdis > 2:
                            turn = True
                            com.angular.z = 0.2
                        print('stuck')
                    else:
                        com.linear.x = 0
                        com.angular.z = 0.2
                        print("3, obs on right")
                    count+=1
                    print(count)

                else: #obstacle approaching on left, turn right
                    if not turn:
                        turn = True
                        com.angular.z = -0.2
                        count = 0
                    elif(abs(dt.ranges[268] - dt.ranges[272]) < 0.002 ): #done turning
                        turn = False
                        rdis = dt.ranges[270]
                        if rdis > 2:
                            turn = True
                            com.angular.z = -0.2
                        print('stuck')
                    else:
                        com.linear.x = 0
                        com.angular.z = -0.2
                        print("3, obs on left")
                    count +=1
                    print(count)

            

            elif dt.ranges[0] > thr and dt.ranges[90] <= rdis + 0.75 or dt.ranges[270] <= rdis + 0.75: #obstacle is on the right of the robot               
                if dt.ranges[90] < 0.75 or dt.ranges[270] < 0.75: #too close to obstacle
                    adjust = True
                    count = 0
                else:
                    com.linear.x = 0.2
                    com.angular.z = 0.0
                print("4")

            else:# dt.ranges[540] > thr and dt.ranges[191] > thr: #obstacle is no longer on right of robot, head right
                corner = True
                count = 0    
                obstacle_flag = 0
                print("5")

        
        
        
        


    if abs(inc_x) < 0.25 and abs(inc_y) < 0.25: #we are at the target
        if abs(desired_pose - yaw) > 0.1:
            com.linear.x = 0
            com.angular.z = 0.3
        else:
            com.linear.x = 0
            com.angular.z = 0
        print("based")
            #set pose

    print(com)
    cmd_vel_pub.publish(com)

    rate.sleep()

def demo(msg):
    com = Twist();
    cmd_vel_pub = rospy.Publisher("/cmd_vel", Twist, queue_size=100)
    rate = rospy.Rate(50)
    # # The main loop will run at a rate of 50Hz, i.e., 50 times per second.
    x = msg.pose.pose.position.x #current x position
    y = msg.pose.pose.position.y #current y position

    #finding correct pose


    goal = Point()
    goal.x = 0
    goal.y = 0
    desired_pose = 0
    (roll, pitch, yaw) = tf.transformations.euler_from_quaternion([msg.pose.pose.orientation.x, msg.pose.pose.orientation.y, msg.pose.pose.orientation.z, msg.pose.pose.orientation.w])

    inc_x = goal.x - x
    inc_y = goal.y - y
    angle_to_goal = atan2(inc_y, inc_x)
    distance_to_goal = sqrt((inc_x * inc_x) + (inc_y * inc_y))

    if abs(angle_to_goal - yaw) > 0.15:
        com.linear.x = 0
        com.angular.z = 0.2
    else:
        com.linear.x = 0.2
        com.angular.z = 0.0


    if abs(inc_x) < 0.25 and abs(inc_y) < 0.25: #we are at the target
        if abs(desired_pose - yaw) > 0.1:
            com.linear.x = 0
            com.angular.z = 0.3
        else:
            com.linear.x = 0
            com.angular.z = 0
        print("based")
            #set pose
    print(com)
    cmd_vel_pub.publish(com)


def odom_callback(odom): #store odom data
    global msg
    msg = odom


def scan_callback(scan):
    global dt 
    dt = scan
    
    if msg is not None and dt is not None:
        callback()


if __name__ == "__main__":
    print('hello')
    
    rospy.init_node("move_bot", anonymous=True)
    rospy.Subscriber('odom',Odometry, odom_callback)
    rospy.Subscriber('scan', LaserScan, scan_callback)
    # rospy.spin()

    print(dt)
    if dt is not None and msg is not None:
        callback()
    
    # odom_sub = message_filters.Subscriber('odom', Odometry)
    # scan_sub = message_filters.Subscriber('scan', LaserScan)
    # ts = message_filters.TimeSynchronizer([odom_sub, scan_sub], 1)
    # ts.registerCallback(callback)

    rospy.spin()