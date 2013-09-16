import numpy as np

def create_animation():

    animation_Nframes = 100
    animation_domain = [5.0, 95.0]


    ## Increase this to increase the running speed relative to
    ## everything else
    person_position = animation_domain[0]
    person_speed = 1.0
    person_acceleration = -0.03

    running_image_id = 0
    standing_image_id = 0
    
    ## Specify the initial person data.
    plane_position = 45.0
    plane_speed = 0.0
    plane_acceleration = 0.2
    plane_elevation = 0.0
    plane_degree = 0


    
    ## The number of frames (Nframes) is determined by
    ## person_speed. The person always runs at a speed that
    ## would cover the entire domain in one animation cycle.    
    Nframes = int( (animation_domain[1] - animation_domain[0]) / person_speed ) + 1

    ## Specify the time (i.e. frame number) at which the plane starts
    ## rolling, and at which it starts taking off.
    frame_plane_start = int(0.2 * Nframes)
    frame_plane_takeoff = int(0.35 * Nframes)


    ## Derived quantities
    plane_rolling_Nframes = frame_plane_takeoff - frame_plane_start
    plane_flying_Nframes = Nframes - frame_plane_takeoff

    
    f = open('../app/static/css/animation.css','w')
    
    f.write("@-webkit-keyframes myanim {\n")
    for i in xrange(Nframes):
        frame_percentage = 100.0*i/(Nframes-1)

        running_image_id = i % 7
    
        if i < frame_plane_start:
            ## plane has not yet started to roll

            person_position += person_speed
            
        elif i < frame_plane_takeoff:
            ## plane is rolling
            
            person_speed += person_acceleration
            if person_speed < 0.0:
                person_speed = 0.0
                running_image_id = -1
            person_position += person_speed
            
            plane_speed += plane_acceleration
            plane_position += plane_speed  ## dx = v * dt and dt = 1
            
        else:
            ## plane is taking off

            ip = i - frame_plane_takeoff

            person_speed += person_acceleration
            if person_speed < 0.0:
                person_speed = 0.0
                running_image_id = -1
            person_position += person_speed

            ## no more plane acceleration
            plane_position += plane_speed
            plane_degree = int( 30.0 * 2*ip / (plane_flying_Nframes-1) )
            if plane_degree > 30: plane_degree = 30
            plane_elevation += 3*plane_speed * np.tan(plane_degree*np.pi/180.0)

        print '%d (%.1f): person_position = %.1f%%   plane_position = %.1f%%  plane_degree = %d plane_elevation = %.1f' % (i,frame_percentage,person_position,plane_position,plane_degree,plane_elevation)
            
        f.write("    %.1f%% {\n" % frame_percentage)

        if running_image_id >= 0:
            f.write("    background-image:url('/static/anim/running_%02d.png'), url('/static/anim/airplane_%02d.png');\n" % (running_image_id, plane_degree))
        else:
            Nplay=3
            
            f.write("    background-image:url('/static/anim/standing_%02d.png'), url('/static/anim/airplane_%02d.png');\n" % (standing_image_id/Nplay, plane_degree))
            standing_image_id += 1
            if standing_image_id > Nplay*4: standing_image_id=Nplay*4
            
        f.write("    background-position: %.1f%% 95%%, %.1f%% %.1f%%;\n" % (person_position,plane_position,95.0-plane_elevation))
        f.write("    }\n")

    f.write("}\n")
    f.close()
    
        
