
from abstract import AbstractRobotInterface

import gym; from gym import spaces
import numpy as np
import os
import pybullet as pb
import rospkg
import subprocess


class Ur5RobotiqInterface(AbstractRobotInterface):

    '''
    Defines action space for the ur5 with a robotiq 85 gripper. This is the
    standard "costar" robot used for many of our experiments.
    '''

    xacro_filename = 'robot/ur5_joint_limited_robot.xacro'
    urdf_filename = 'ur5_joint_limited_robot.urdf'

    arm_name = "ur5"
    gripper_name = "robotiq_2_finger"
    base_name = None

    left_knuckle = 8
    left_finger = 9
    left_inner_knuckle = 12
    left_fingertip = 13

    right_knuckle = 10
    right_finger = 11
    right_inner_knuckle = 14
    right_fingertip = 15

    dof = 6
    arm_joint_indices = xrange(dof)
    gripper_indices = [left_knuckle, left_finger, left_inner_knuckle,
                       left_fingertip, right_knuckle, right_finger, right_inner_knuckle,
                       right_fingertip]

    def __init__(self, *args, **kwargs):
        super(Ur5RobotiqInterface, self).__init__(*args, **kwargs)

    def load(self):
        '''
        This is an example of a function that allows you to load a robot from
        file based on command line arguments. It just needs to find the
        appropriate directory, use xacro to create a temporary robot urdf,
        and then load that urdf with PyBullet.
        '''

        rospack = rospkg.RosPack()
        path = rospack.get_path('costar_simulation')
        filename = os.path.join(path, self.xacro_filename)
        urdf_filename = os.path.join(path, 'robot', self.urdf_filename)
        urdf = open(urdf_filename, "w")

        # Recompile the URDF to make sure it's up to date
        subprocess.call(['rosrun', 'xacro', 'xacro.py', filename], stdout=urdf)

        self.handle = pb.loadURDF(urdf_filename)
        self.grasp_idx = self.findGraspFrame()
        self.loadKinematicsFromURDF(urdf_filename, "base_link")

        return self.handle

    def place(self, pos, rot, joints):
        pb.resetBasePositionAndOrientation(self.handle, pos, rot)
        pb.createConstraint(
            self.handle, -1, -1, -1, pb.JOINT_FIXED, pos, [0, 0, 0], rot)
        for i, q in enumerate(joints):
            pb.resetJointState(self.handle, i, q)

        # gripper
        pb.resetJointState(self.handle, self.left_knuckle, 0)
        pb.resetJointState(self.handle, self.right_knuckle, 0)

        pb.resetJointState(self.handle, self.left_finger, 0)
        pb.resetJointState(self.handle, self.right_finger, 0)

        pb.resetJointState(self.handle, self.left_fingertip, 0)
        pb.resetJointState(self.handle, self.right_fingertip, 0)

        self.arm(joints,)
        self.gripper(0)

    def gripperCloseCommand(cls):
        '''
        Return the closed position for this gripper.
        '''
        return -0.8

    def gripperOpenCommand(cls):
        '''
        Return the open command for this gripper
        '''
        return 0.0

    def arm(self, cmd, mode=pb.POSITION_CONTROL):
        '''
        Set joint commands for the robot arm.
        '''
        if len(cmd) > self.dof:
            raise RuntimeError('too many joint positions')

        pb.setJointMotorControlArray(self.handle, self.arm_joint_indices, mode,
                                     cmd, forces=[1000.] * self.dof)

    def gripper(self, cmd, mode=pb.POSITION_CONTROL):
        '''
        Gripper commands need to be mirrored to simulate behavior of the actual
        UR5.
        '''

        # This is actually only a 1-DOF gripper
        cmd_array = [-cmd, cmd, -cmd, cmd, -cmd, cmd, -cmd, cmd]
        pb.setJointMotorControlArray(self.handle, self.gripper_indices, mode,
                                     cmd_array)

    def getActionSpace(self):
        return spaces.Tuple((spaces.Box(-np.pi, np.pi, self.dof),
                spaces.Box(-0.8, 0.0, 1)))

    def _getArmPosition(self):
        q = [0.] * 6
        for i in xrange(6):
            q[i] = pb.getJointState(self.handle, i)[0]
        return q

    def _getGripper(self):
        return pb.getJointState(self.handle, self.left_finger)
