1. Put the 'move_bot' directory into the 'src' folder of a catkin workspace along with the 'stage' directory.

2. move_bot.py may require executable permissions so navigate to the directory containing move_bot.py and use the command 'chmod +x move_bot.py'

3. Navigate back to the catkin workspace and use command 'catkin_make'

4. May have to use 'source devel/setup.bash'

5. In one terminal, run 'roscore', and in another boot up bug-test.world

5. You can then run 'rosrun move_bot move_bot.py', as long as roscore and bug-test.world are also up and running in
other terminals

6. This should prompt for a x,y coordinates and a theta value for pose. 
	If, for instance, you wanted to go to position 24, 3, and finish in pose at 3 radians, you can type '24, 3, 3'