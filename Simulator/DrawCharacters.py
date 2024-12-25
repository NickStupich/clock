
def draw_digit(n, angles):
    if n == 0:
        angles[0,0,0] = 0
        angles[0,0,1] = 270
        angles[0,1,0] = 180
        angles[0,1,1] = 270

        angles[1,0,0] = 90
        angles[1,0,1] = 270
        angles[1,1,0] = 90
        angles[1,1,1] = 270

        angles[2,0,0] = 90
        angles[2,0,1] = 0
        angles[2,1,0] = 180
        angles[2,1,1] = 90

    elif n == 1: #TODO: should the vertical line be on the left if it's the 2nd digit?
        angles[0,0,0] = 225
        angles[0,0,1] = 225
        angles[0,1,0] = 270
        angles[0,1,1] = 270

        angles[1,0,0] = 225
        angles[1,0,1] = 225
        angles[1,1,0] = 90
        angles[1,1,1] = 270

        angles[2,0,0] = 225
        angles[2,0,1] = 225
        angles[2,1,0] = 90
        angles[2,1,1] = 90

    elif n == 2: 
        angles[0,0,0] = 0
        angles[0,0,1] = 0
        angles[0,1,0] = 180
        angles[0,1,1] = 270

        angles[1,0,0] = 0
        angles[1,0,1] = 270
        angles[1,1,0] = 180
        angles[1,1,1] = 90

        angles[2,0,0] = 90
        angles[2,0,1] = 0
        angles[2,1,0] = 180
        angles[2,1,1] = 180

    elif n == 3: 
        angles[0,0,0] = 0
        angles[0,0,1] = 0
        angles[0,1,0] = 180
        angles[0,1,1] = 270

        angles[1,0,0] = 0
        angles[1,0,1] = 0
        angles[1,1,0] = 180
        angles[1,1,1] = 90

        angles[2,0,0] = 0
        angles[2,0,1] = 0
        angles[2,1,0] = 90
        angles[2,1,1] = 180

    elif n == 4: 
        angles[0,0,0] = 270
        angles[0,0,1] = 270
        angles[0,1,0] = 270
        angles[0,1,1] = 270

        angles[1,0,0] = 90
        angles[1,0,1] = 0
        angles[1,1,0] = 270
        angles[1,1,1] = 90

        angles[2,0,0] = 225
        angles[2,0,1] = 225
        angles[2,1,0] = 90
        angles[2,1,1] = 90

    elif n == 5: 
        angles[0,0,0] = 0
        angles[0,0,1] = 270
        angles[0,1,0] = 180
        angles[0,1,1] = 180

        angles[1,0,0] = 90
        angles[1,0,1] = 0
        angles[1,1,0] = 180
        angles[1,1,1] = 270

        angles[2,0,0] = 0
        angles[2,0,1] = 0
        angles[2,1,0] = 180
        angles[2,1,1] = 90

    elif n == 6: 
        angles[0,0,0] = 0
        angles[0,0,1] = 270
        angles[0,1,0] = 180
        angles[0,1,1] = 180

        angles[1,0,0] = 90
        angles[1,0,1] = 270
        angles[1,1,0] = 180
        angles[1,1,1] = 270

        angles[2,0,0] = 90
        angles[2,0,1] = 0
        angles[2,1,0] = 180
        angles[2,1,1] = 90

    elif n == 7: 
        angles[0,0,0] = 0
        angles[0,0,1] = 0
        angles[0,1,0] = 180
        angles[0,1,1] = 270

        angles[1,0,0] = 225
        angles[1,0,1] = 225
        angles[1,1,0] = 90
        angles[1,1,1] = 270

        angles[2,0,0] = 225
        angles[2,0,1] = 225
        angles[2,1,0] = 90
        angles[2,1,1] = 90

    elif n == 8: 
        angles[0,0,0] = 0
        angles[0,0,1] = 270
        angles[0,1,0] = 180
        angles[0,1,1] = 270

        angles[1,0,0] = 90
        angles[1,0,1] = 0
        angles[1,1,0] = 90
        angles[1,1,1] = 180

        angles[2,0,0] = 90
        angles[2,0,1] = 0
        angles[2,1,0] = 90
        angles[2,1,1] = 180

    elif n == 9: 
        angles[0,0,0] = 0
        angles[0,0,1] = 270
        angles[0,1,0] = 180
        angles[0,1,1] = 270

        angles[1,0,0] = 90
        angles[1,0,1] = 0
        angles[1,1,0] = 90
        angles[1,1,1] = 270

        angles[2,0,0] = 0
        angles[2,0,1] = 0
        angles[2,1,0] = 90
        angles[2,1,1] = 180


def draw_letter(c, angles):
    c = c.lower()

    if c == 'f':
        angles[0,0,0] = 0
        angles[0,0,1] = 270
        angles[0,1,0] = 180
        angles[0,1,1] = 180

        angles[1,0,0] = 90
        angles[1,0,1] = 270
        angles[1,1,0] = 180
        angles[1,1,1] = 180

        angles[2,0,0] = 90
        angles[2,0,1] = 90
        angles[2,1,0] = 225
        angles[2,1,1] = 225


    elif c == 'u':
        angles[0,0,0] = 270
        angles[0,0,1] = 270
        angles[0,1,0] = 270
        angles[0,1,1] = 270

        angles[1,0,0] = 90
        angles[1,0,1] = 270
        angles[1,1,0] = 90
        angles[1,1,1] = 270

        angles[2,0,0] = 90
        angles[2,0,1] = 0
        angles[2,1,0] = 180
        angles[2,1,1] = 90


    elif c == 'c':
        angles[0,0,0] = 0
        angles[0,0,1] = 270
        angles[0,1,0] = 180
        angles[0,1,1] = 180

        angles[1,0,0] = 90
        angles[1,0,1] = 270
        angles[1,1,0] = 225
        angles[1,1,1] = 225

        angles[2,0,0] = 90
        angles[2,0,1] = 0
        angles[2,1,0] = 180
        angles[2,1,1] = 180


    elif c == 'k':
        angles[0,0,0] = 270
        angles[0,0,1] = 270
        angles[0,1,0] = 225
        angles[0,1,1] = 225

        angles[1,0,0] = 45
        angles[1,0,1] = 315
        angles[1,1,0] = 225
        angles[1,1,1] = 225

        angles[2,0,0] = 90
        angles[2,0,1] = 90
        angles[2,1,0] = 135
        angles[2,1,1] = 135


