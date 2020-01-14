from pyglet.gl import *
import math
import argparse
import numpy as np
from numpy.linalg import norm
from pyglet.window import key
import time
import cProfile
file = None
bspline = None
gouraudov = None
window = None 
animIndex = 0
timer = 0
showTangents = True
class Camera:
    def __init__(self,pos=(0,0,0), lookAt=(0,0,0)):
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

    
class BSpline:        
    def __init__(self):
        self.resolution = 20
        self.load_obj(bspline)
        self.interval_postion()
        self.calc_spline()
    
    def load_obj(self,file):

        self.vertex = []
        
        obj_data = open(file, 'r')

        for line in obj_data:
            if line.startswith("v"):
                split = line.split()
                self.vertex.append(list(map(float,split[1:4])))
            if line.startswith('f'):
                continue
            if line.startswith("g"):
                continue
            if line.startswith("#"):
                continue
    def interval_postion(self):
        x_max, x_min = float("-inf"), float("inf")
        y_max, y_min = float("-inf"), float("inf")
        z_max, z_min = float("-inf"), float("inf")

        for v in self.vertex:
            if v[0] < x_min:
                x_min = v[0]
            if v[0] > x_max:
                x_max = v[0]

            if v[1] < y_min:
                y_min = v[1]
            if v[1] > y_max:
                y_max = v[1]

            if v[2] < z_min:
                z_min = v[2]
            if v[2] > z_max:
                z_max = v[2]

        self.center_x = (x_max + x_min) / 2
        self.center_y = (y_max + y_min) / 2
        self.center_z = (z_max + z_min) / 2

        scale_x = x_max - x_min
        scale_y = y_max - y_min
        scale_z = z_max - z_min

        self.scale = max([scale_x, scale_y, scale_z])
   
    def get_center(self):
        return self.center_x, self.center_y, self.center_z

    def get_scale(self):
        return self.scale
    
    def curve_diff2(self, i_segment, t):
            
        T = [2*t, 1]
        
        B = 1/2 * np.array([[-1, 3, -3, 1],
                            [2, -4, 2, 0]])
        
        control_points = self.vertex
        R = np.array([control_points[i_segment-1],
                    control_points[i_segment],
                    control_points[i_segment+1],
                    control_points[i_segment+2]])
        
        TB = np.dot(T, B)
        TBR = np.dot(TB, R)
        
        return TBR

 
    def calc_segment_t(self, i_segment, t):
        T = np.array([t * t * t, t * t, t, 1])
        
        B = 1/6 * np.array([[-1, 3, -3, 1],[3, -6, 3, 0],  [-3, 0, 3, 0],  [1, 4, 1, 0]])

        control_points = self.vertex
        R = np.array([control_points[i_segment-1],
                    control_points[i_segment],
                    control_points[i_segment+1],
                    control_points[i_segment+2]])
        TB = np.dot(T,B)
        TBR = np.dot(TB, R)
        
        Tt = [t*t, t, 1]
        Bt = 1/2 * np.array([[-1, 3, -3, 1], 
                            [2, -4, 2, 0],
                            [-1, 0, 1, 0]])
        
        Rt = np.array([control_points[i_segment-1],
                    control_points[i_segment],
                    control_points[i_segment+1],
                    control_points[i_segment+2]])
        TBt = np.dot(Tt, Bt)
        TBRt = np.dot(TBt, Rt)
        
        return TBR, TBRt

    def calc_spline(self):
        self.segments = []
        self.tangets = []
        for index in range(1, self.vertex.__len__() - 3 + 1):
            for t in np.linspace(0,1, self.resolution):
                points, tangents =  self.calc_segment_t(index, t)
                self.segments.append(points)
                self.tangets.append(tangents) 
            
    def getTangentData(self, point, index):
        data = [ (point[0])/self.scale,
                 (point[1])/self.scale,
                 (point[2])/self.scale, 
                 (point[0] + self.tangets[index][0])/self.scale, 
                 (point[1] + self.tangets[index][1])/self.scale, 
                 (point[2] + self.tangets[index][2])/self.scale]
        return data
         
    def define_drawing(self):
        global animIndex, showTangents
        self.batch = pyglet.graphics.Batch()
        
        line_points = []
        line_color = []
        index = 0
        for iIndex, point in enumerate(self.segments):        
            line_points.append((point[0])/self.scale)
            line_points.append((point[1])/self.scale)
            line_points.append((point[2])/self.scale)
            line_color.append(0.8)
            line_color.append(0.8)
            line_color.append(0.8)
            if(showTangents):
                self.batch.add(2, 
                        GL_LINES, 
                        None,
                            ('v3f', self.getTangentData(point, index)),
                            ('c3d', [0.7, 0.7, 0.8, 0.1, 0.7, 0.8]))   
                
            index += 1
        self.batch.add(int(line_points.__len__()/3), 
                       GL_LINE_STRIP, 
                       None,
                        ('v3f', line_points), ('c3d', line_color))  

    def draw(self):
        self.batch.draw()


class Model:  
    def load_obj(self,file):

        self.vertex = []
        self.polygons = []
        
        obj_data = open(file, 'r')

        for line in obj_data:
            if line.startswith("v"):
                split = line.split()
                self.vertex.append(list(map(float,split[1:4])))
            if line.startswith('f'):
                split = line.split()
                self.polygons.append(list(map(int, split[1:4])))
            if line.startswith("g"):
                continue
            if line.startswith("#"):
                continue

    def interval_postion(self):
        x_max, x_min = float("-inf"), float("inf")
        y_max, y_min = float("-inf"), float("inf")
        z_max, z_min = float("-inf"), float("inf")

        for v in self.vertex:
            if v[0] < x_min:
                x_min = v[0]
            if v[0] > x_max:
                x_max = v[0]

            if v[1] < y_min:
                y_min = v[1]
            if v[1] > y_max:
                y_max = v[1]

            if v[2] < z_min:
                z_min = v[2]
            if v[2] > z_max:
                z_max = v[2]

        self.center_x = (x_max + x_min) / 2
        self.center_y = (y_max + y_min) / 2
        self.center_z = (z_max + z_min) / 2

        scale_x = x_max - x_min
        scale_y = y_max - y_min
        scale_z = z_max - z_min

        self.scale = max([scale_x, scale_y, scale_z])

    def hide_polygons(self, camera):
        self.norm = {}
        self.pol_centers = {}
        camera_positon = np.array(camera.get_postion())

        for pol in self.polygons:
            V1 = np.array(self.vertex[pol[0] - 1])
            V2 = np.array(self.vertex[pol[1] - 1])
            V3 = np.array(self.vertex[pol[2] - 1])

            a = V2 - V1
            b = V3 - V1

            n = np.cross(a,b)

            self.norm[repr(pol)] = n

            c_x = (V1[0] + V2[0] + V3[0]) / 3
            c_y = (V1[1] + V2[1] + V3[1]) / 3
            c_z = (V1[2] + V2[2] + V3[2]) / 3

            pol_center = np.array([c_x, c_y, c_z])
            self.pol_centers[repr(pol)] = pol_center

    def constant_color(self, source):
        self.pol_color = {}
        s = np.array(source)

        for pol in self.polygons:
            N = self.norm[repr(pol)]
            N = N/norm(N)

            center = self.pol_centers[repr(pol)]
            L = center - s
            L = L/norm(L)

            Id = self.It * self.kd * np.dot(N,L)
            if Id < 0:
                Id = 0

            I = self.Ia * self.ka + Id
            if I > 1:
                I = 1

            self.pol_color[repr(pol)] = I

    def vertex_colors(self, source):
        self.vertex_color = {}
        s = np.array(source)

        for v in self.vertex:
            N = self.vertex_norm[repr(v)]
            N = N/norm(N)

            L = np.array(v) - s
            L = L/norm(L)

            Id = self.It * self.kd * np.dot(N,L)
            if Id < 0:
                Id = 0

            I = self.Ia * self.ka + Id
            if I > 1:
                I = 1

            self.vertex_color[repr(v)] = I

    def norm_in_vertex(self):
        self.vertex_norm = {}

        for i, v in enumerate(self.vertex):
            sum = np.array([0.0, 0.0, 0.0])
            count = 0
            for pol in self.polygons:
                if (i + 1) in pol:
                    n = self.norm[repr(pol)]
                    n = n/norm(n)
                    sum += n
                    count +=1
            
            self.vertex_norm[repr(v)] = sum/count

    def get_center(self):
        return self.center_x, self.center_y, self.center_z

    def get_scale(self):
        return self.scale

    def __init__(self):
        self.load_obj(file)
        self.interval_postion()

        self.Ia = 0.5
        self.ka = 1.0

        self.It = 1.0
        self.kd = 0.4
        
        self.location = [0,0,0]
    
    def define_drawing(self):
        self.batch = pyglet.graphics.Batch()

        for pol in self.polygons:
            V1 = self.vertex[pol[0] - 1]
            V2 = self.vertex[pol[1] - 1]
            V3 = self.vertex[pol[2] - 1]
            
            #glPolygonMode( GL_FRONT_AND_BACK, GL_LINE );
            #if self.show_pol[repr(pol)]:
            if gouraudov:
                self.batch.add(3, GL_TRIANGLES, None, ('v3f', (V1[0] , V1[1] , V1[2], V2[0] , V2[1], V2[2] ,V3[0] , V3[1], V3[2])),
                                                        ('c3f', (0, self.vertex_color[repr(V1)], 0, 0, self.vertex_color[repr(V2)], 0, 0, self.vertex_color[repr(V3)] ,0)))
            else:
                color = self.pol_color[repr(pol)]
                self.batch.add(3, GL_TRIANGLES, None, ('v3f', (V1[0] , V1[1] , V1[2], V2[0] , V2[1], V2[2] ,V3[0] , V3[1], V3[2])),
                                                        ('c3f', (0, color, 0, 0, color, 0, 0, color ,0)))

    def draw(self):
        self.batch.draw()

class Window(pyglet.window.Window):
    global pyglet
    
    def __init__(self,*args,**kwargs):
        global animIndex, timer
        super().__init__(*args,**kwargs)
        start = time.time()
        self.set_minimum_size(600,400)
        self.POV = 75
        self.source = [0,0,0]
        pyglet.clock.schedule(self.update)
        end = time.time()
        print(f'Load time : {end - start}')
        self.model = Model()
        self.spline = BSpline()
        self.camera = Camera((1,1,1))
        
        self.model.hide_polygons(self.camera) 
        end = time.time()
        print(f'Load time : {end - start}')
        if gouraudov:
            self.model.norm_in_vertex()
            self.model.vertex_colors(self.source)
        else:
            self.model.constant_color(self.source)
        end = time.time()
        print(f'Load time : {end - start}')

        self.model.define_drawing()
        end = time.time()
        print(f'Load time : {end - start}')
        self.spline.define_drawing()
        end = time.time()
        print(f'Load time : {end - start}')

    def on_key_press(self, key, modifiers):
        global showTangents
        if modifiers == 18:
            if key == pyglet.window.key.UP:
                self.camera.lookAt[1] += 0.1;
            elif key == pyglet.window.key.DOWN:
                self.camera.lookAt[1] -= 0.1;
            elif key == pyglet.window.key.RIGHT:
                self.camera.lookAt[0] += 0.1;
            elif key == pyglet.window.key.LEFT:
                self.camera.lookAt[0] -= 0.1;
            elif key == pyglet.window.key.W:
                self.camera.lookAt[2] += 0.1;
            elif key == pyglet.window.key.S:
                self.camera.lookAt[2] -= 0.1;
        elif modifiers == 17:
            if key == pyglet.window.key.UP:
                self.camera.pos[2] -= 0.1;
            elif key == pyglet.window.key.DOWN:
                self.camera.pos[2] += 0.1;
        
        elif key == pyglet.window.key.UP:
            self.camera.pos[1] += 0.1;
        elif key == pyglet.window.key.DOWN:
            self.camera.pos[1] -= 0.1;
        elif key == pyglet.window.key.RIGHT:
            self.camera.pos[0] += 0.1;
        elif key == pyglet.window.key.LEFT:
            self.camera.pos[0] -= 0.1;
        elif key == pyglet.window.key.T:
            showTangents = not showTangents
            
    def update(self,dt): 
        
        global animIndex,timer
        self.spline.define_drawing()
        timer = timer + 1 / 50
        if timer > 1:
            timer = 0
            animIndex += 1
            if animIndex >= self.spline.vertex.__len__() -3  + 1:
                animIndex = 1
            

    
    def animate(self, i_seg):
        global animIndex, timer
        curr_orient = np.array([0,0,1])
        
        segment_point, segment_tangents = self.spline.calc_segment_t(animIndex, timer)
        
        rot_axis, rot_angle = self.camera.rotationPars(curr_orient, segment_tangents)
        curr_orient = segment_tangents
        
        glPushMatrix()
        dEF = self.spline.get_scale() 
        glTranslatef(segment_point[0]/dEF, segment_point[1]/dEF, segment_point[2]/dEF)
        glScalef(1/15, 1/15, 1/15)
        glRotatef(rot_angle, rot_axis[0], rot_axis[1], rot_axis[2])
        self.model.draw()
        glPopMatrix()

    def animate_DCM(self, i_seg):
        global animIndex, timer
        
        curr_point, curr_point_tangent = self.spline.calc_segment_t(animIndex, timer)
        curr_point_diff2 = self.spline.curve_diff2(animIndex, timer)

        R = self.camera.rotationPars(curr_point, curr_point_tangent)
        
        glPushMatrix()
        dEF = self.spline.get_scale() 
        glTranslatef(curr_point[0]/dEF, curr_point[1]/dEF, curr_point[2]/dEF)
        glScalef(1/15, 1/15, 1/15)
        glRotatef(R[1], R[0][0], R[0][1], R[0][2])
        self.model.draw()
        glPopMatrix()


    def drawOrigin(self):
        glPushMatrix()
        glBegin(GL_LINES);
        glVertex3f(0, 0, 0);
        glVertex3f(0.3, 0, 0);
        glVertex3f(0, 0, 0);
        glVertex3f(0, 0.2, 0);
        glVertex3f(0, 0, 0);
        glVertex3f(0, 0, 0.1);
        glEnd();
        glPopMatrix()
         
    def drawLookAt(self, lookAt, camera_positon):
        glPushMatrix()
        glBegin(GL_LINES);
        glVertex3f(lookAt[0], lookAt[1], lookAt[2]);
        glVertex3f(camera_positon[0], camera_positon[1], camera_positon[2]);
        glEnd();
        glBegin(GL_POINTS);
        glVertex3f(lookAt[0], lookAt[1], lookAt[2]);
        glEnd();
        glPopMatrix()     
            
    def on_draw(self):
        global animIndex
        start = time.time()
        self.clear()
        self.drawOrigin()
        camera_positon = self.camera.get_postion()
        lookAt = self.camera.get_lookAt()
        self.drawLookAt(lookAt,  camera_positon)
       
        glPushMatrix()
        self.animate(animIndex)
        glPopMatrix()
        
        glPushMatrix()
        splineC = self.spline.get_center()
        self.spline.draw()
        glPopMatrix()
        
        glPushMatrix()
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.POV,self.width/self.height,0.05,1000)
        gluLookAt(camera_positon[0], camera_positon[1], camera_positon[2], 
                  lookAt[0], lookAt[1], lookAt[2], 
                  0.0, 1.0, 0.0)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        glFrontFace(GL_CCW)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glPopMatrix()
        end = time.time()
        #print(f'Frame time : {end - start}')
        


if __name__ == '__main__':
    # parsiranje komandne linije
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str, required=True)
    parser.add_argument("-s", "--bspline", type=str, required=True)

    args = parser.parse_args()
    file = args.file
    bspline = args.bspline
    gouraudov = False

    window = Window(width=640,height=480,caption='Sjenćanje',resizable=True)
    keys = key.KeyStateHandler()
    window.push_handlers(keys)
    
    glClearColor(0.0, 0.0, 0.0 ,1) 

    glFrontFace(GL_CCW)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    pyglet.app.run()
    