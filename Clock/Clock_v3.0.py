import time, math, os

def clear(): os.system('clear')

def draw_hand(angle, length, char):
    x = y = 0
    for i in range(1, length+1):
        nx = int(12 + i * math.sin(angle) * 0.6)
        ny = int( 6 - i * math.cos(angle) * 0.3)
        if 0 <= nx < 24 and 0 <= ny < 12:
            face[ny] = face[ny][:nx] + char + face[ny][nx+1:]

while True:
    t = time.localtime()
    h, m, s = t.tm_hour % 12, t.tm_min, t.tm_sec

    face = ["+----------------------+",
            "|                      |",
            "|        12            |",
            "|                      |",
            "|   9        3         |",
            "|                      |",
            "|        6             |",
            "|                      |",
            "|                      |",
            "|                      |",
            "|                      |",
            "+----------------------+"]
    face = list(face)

    s_ang = math.radians(s * 6 - 90)
    m_ang = math.radians(m * 6 + s*0.1 - 90)
    h_ang = math.radians(h * 30 + m*0.5 - 90)

    draw_hand(h_ang, 4, 'H')
    draw_hand(m_ang, 6, 'M')
    draw_hand(s_ang, 8, 'S')

    clear()
    print("\n".join(face))
    print(" %02d:%02d:%02d" % (h or 12, m, s))
    time.sleep(1)
