import numpy as np

class Camera:
    def __init__(self,pos=(0,0,-1), lookAt=(0,0,0)):
        self.pos = list(pos)
        self.lookAt= list(lookAt)
    
    def get_postion(self):
        return self.pos
    
    def get_lookAt(self):
        return self.lookAt
    
    def rotationPars(self, cOrient, nOrient):
        rot_axis = np.cross(cOrient, nOrient)
        dot_curr_next = np.dot(cOrient, nOrient)
        curr_mag = np.linalg.norm(cOrient)
        next_mag = np.linalg.norm(nOrient)

        rot_angle = np.rad2deg(np.arccos(dot_curr_next / (curr_mag * next_mag)))

        return rot_axis, rot_angle