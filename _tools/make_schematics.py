#!/usr/bin/env python3
"""Generate background schematics for the AquaFlow Energy site in the Rev B drawing style.

Sheet: A3 landscape, 1684 x 1191 units. Palatino title, Helvetica labels, thin ink lines,
header strip, scale bar, dimension lines, notes block, 'indicative, not to scale' footer.
Ink is currentColor so the site can tint it; no page background.

Run from anywhere:  python3 tools/make_schematics.py
Writes img/dwg/gen-*.svg next to the Rev B exports.
"""
import math, pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / 'img' / 'dwg'
W, H = 1684, 1191
SERIF = "Palatino,'Palatino Linotype','URW Palladio L',Georgia,serif"
SANS = "Helvetica,Arial,'Liberation Sans','DejaVu Sans',sans-serif"


class Sheet:
    def __init__(self, number, title, subtitle):
        self.parts = []
        self.title = title
        self.add(f'<text x="72" y="104" font-family="{SERIF}" font-size="41" fill="currentColor">{title}</text>')
        self.add('<rect x="70" y="150" width="1544" height="955" fill="none" stroke="currentColor" stroke-width="1.6"/>')
        self.add('<line x1="70" y1="206" x2="1614" y2="206" stroke="currentColor" stroke-width="1.4"/>')
        self.add('<line x1="70" y1="950" x2="1614" y2="950" stroke="currentColor" stroke-width="1.4"/>')
        self.text(104, 187, str(number), 19)
        self.text(196, 187, subtitle, 19)
        self.text(1150, 187, 'REV B', 19)
        self.text(1330, 187, 'AQUA FLOW ENERGY', 19)
        self.text(1612, 1088, "INDICATIVE ARTIST'S ILLUSTRATION – NOT TO SCALE", 15, anchor='end')
        self.text(1612, 1064, 'Dimensions to be confirmed by survey and detailed design', 13, anchor='end')

    def add(self, s):
        self.parts.append(s)

    def text(self, x, y, s, size=14, anchor='start', family=None, weight='normal', rotate=None):
        fam = family or SANS
        tr = f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ''
        s = s.replace('&', '&amp;').replace('<', '&lt;')
        self.add(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="currentColor"{tr}>{s}</text>')

    def line(self, x1, y1, x2, y2, w=1.2, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="currentColor" stroke-width="{w}"{d}/>')

    def rect(self, x, y, w, h, sw=1.2, dash=None, fill='none'):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" stroke="currentColor" stroke-width="{sw}"{d}/>')

    def circle(self, cx, cy, r, sw=1.2, dash=None, fill='none'):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="currentColor" stroke-width="{sw}"{d}/>')

    def path(self, d, sw=1.2, fill='none', dash=None):
        da = f' stroke-dasharray="{dash}"' if dash else ''
        self.add(f'<path d="{d}" fill="{fill}" stroke="currentColor" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"{da}/>')

    def arrow(self, x1, y1, x2, y2, w=1.2, head=9):
        self.line(x1, y1, x2, y2, w)
        a = math.atan2(y2 - y1, x2 - x1)
        for s in (1, -1):
            self.line(x2, y2, x2 - head * math.cos(a - s * 0.42), y2 - head * math.sin(a - s * 0.42), w)

    def dim(self, x1, y1, x2, y2, label, offset=28, size=13):
        """Dimension line parallel to (x1,y1)->(x2,y2), offset to the left-hand side."""
        a = math.atan2(y2 - y1, x2 - x1)
        nx, ny = -math.sin(a) * offset, math.cos(a) * offset
        ax, ay, bx, by = x1 + nx, y1 + ny, x2 + nx, y2 + ny
        self.line(x1, y1, ax + nx * 0.25, ay + ny * 0.25, 0.8)
        self.line(x2, y2, bx + nx * 0.25, by + ny * 0.25, 0.8)
        self.line(ax, ay, bx, by, 0.9)
        for px, py in ((ax, ay), (bx, by)):  # oblique ticks
            self.line(px - 4, py + 4, px + 4, py - 4, 1.1)
        mx, my = (ax + bx) / 2 + nx * 0.55, (ay + by) / 2 + ny * 0.55
        rot = math.degrees(a)
        if rot > 90 or rot < -90:
            rot += 180
        self.text(mx, my + 4, label, size, anchor='middle', rotate=rot if abs(rot) > 1 else None)

    def scalebar(self, x, y, unit_px, labels, caption):
        for i in range(len(labels) - 1):
            self.rect(x + i * unit_px, y, unit_px, 8, 0.8, fill='currentColor' if i % 2 == 0 else 'none')
        for i, l in enumerate(labels):
            self.text(x + i * unit_px, y - 6, l, 12, anchor='middle')
        self.text(x + len(labels) * unit_px - unit_px + 24, y + 8, caption, 12)

    def notes(self, title, lines, x=90, y=985):
        self.text(x, y, title, 14, weight='bold')
        for i, l in enumerate(lines):
            self.text(x, y + 22 + i * 18, '–  ' + l, 12.5)

    def label(self, x, y, s, size=13):
        self.text(x, y, s, size)

    def leader(self, x1, y1, x2, y2, s, size=12.5, anchor='start'):
        self.line(x1, y1, x2, y2, 0.8)
        self.circle(x1, y1, 2.2, 0.8, fill='currentColor')
        self.text(x2 + (6 if anchor == 'start' else -6), y2 + 4, s, size, anchor=anchor)

    def save(self, name):
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" style="color:#A9C5DB">\n'
               + '\n'.join(self.parts) + '\n</svg>\n')
        (OUT / name).write_text(svg)
        print(name, len(svg), 'bytes')


# ---------------------------------------------------------------- 1. tri-blade rotor
def tri_blade():
    s = Sheet(13, 'Tri-blade river rotor – front elevation, side elevation and hub detail', 'Tri-Blade River Rotor – Ø 3 000 for 1.5 to 3.0 m/s')
    cx, cy, R = 470, 560, 260
    s.text(cx, 262, 'FRONT ELEVATION', 14, anchor='middle')
    s.circle(cx, cy, R, 0.8, dash='8 6')          # swept circle
    s.circle(cx, cy, 46, 1.4)                      # hub
    s.circle(cx, cy, 22, 1.0)
    for k in range(3):
        a0 = math.radians(90 + k * 120)
        # a curved blade: two arcs from hub to tip with sweep
        def pt(r, da):
            a = a0 + da
            return cx + r * math.cos(a), cy - r * math.sin(a)
        p1 = pt(46, -0.25); p2 = pt(R, 0.28); p3 = pt(R, 0.08); p4 = pt(46, -0.05)
        c1 = pt(170, -0.05); c2 = pt(170, 0.26)
        s.path(f'M{p1[0]:.1f},{p1[1]:.1f} Q{c1[0]:.1f},{c1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} L{p3[0]:.1f},{p3[1]:.1f} Q{c2[0]:.1f},{c2[1]:.1f} {p4[0]:.1f},{p4[1]:.1f} Z', 1.3)
        rib = pt(150, 0.08); s.line(*pt(60, -0.1), *rib, 0.7)
    s.line(cx - R - 20, cy, cx + R + 20, cy, 0.6, dash='18 6 3 6')
    s.line(cx, cy - R - 20, cx, cy + R + 20, 0.6, dash='18 6 3 6')
    s.dim(cx - R, cy + R + 60, cx + R, cy + R + 60, 'Ø 3 000 swept', offset=0)
    s.leader(cx + 30, cy - 30, cx + 150, cy - 330, 'HUB – stainless, keyed to shaft')
    s.leader(*((cx + R * 0.8 * math.cos(math.radians(30)), cy - R * 0.8 * math.sin(math.radians(30)))), cx + 330, cy - 200, 'BLADE – recycled polymer skin on stainless ribs')
    s.leader(cx - 60, cy + 150, cx - 330, cy + 260, 'ROTATION – 30 to 60 rpm', anchor='end')
    # side elevation
    sx, sy = 1080, 560
    s.text(sx, 262, 'SIDE ELEVATION', 14, anchor='middle')
    s.rect(sx - 40, sy - 46, 80, 92, 1.4)                       # hub
    s.line(sx + 40, sy, sx + 300, sy, 2.2)                      # shaft
    s.rect(sx + 300, sy - 70, 150, 140, 1.4)                    # pod
    s.text(sx + 375, sy - 80, 'POD – gearbox + alternator', 12, anchor='middle')
    for ang in (-1, 1):
        s.path(f'M{sx - 40},{sy - 20 * ang} C{sx - 110},{sy - 60 * ang} {sx - 150},{sy - 160 * ang} {sx - 120},{sy - 260 * ang} L{sx - 60},{sy - 262 * ang} C{sx - 80},{sy - 170 * ang} {sx - 60},{sy - 80 * ang} {sx - 20},{sy - 46 * ang} Z', 1.3)
    s.path(f'M{sx - 40},{sy + 46} C{sx - 60},{sy + 120} {sx - 10},{sy + 200} {sx + 10},{sy + 262} L{sx + 50},{sy + 258} C{sx + 20},{sy + 190} {sx + 20},{sy + 120} {sx + 40},{sy + 46} Z', 1.3)
    s.dim(sx - 150, sy + 300, sx + 450, sy + 300, '2 150 overall', offset=0)
    s.dim(sx + 300, sy - 70, sx + 300, sy + 70, '1 000', offset=-24)
    s.arrow(sx - 300, sy - 180, sx - 200, sy - 180, 1.2); s.text(sx - 300, sy - 192, 'FLOW  U = 1.5–3.0 m/s', 12.5)
    s.arrow(sx - 300, sy + 180, sx - 200, sy + 180, 1.2)
    s.scalebar(1180, 905, 60, ['0', '0.5', '1', '1.5', '2'], 'metres')
    s.notes('Materials / comments:', [
        'Blades: three, pressed recycled-polymer skin over stainless ribs, washable, replaced at the six-monthly lift.',
        'Hub and shaft: stainless; the shaft is the only moving part outside the sealed pod.',
        'Rotor is slow and enclosed within its swept circle by the duct ring (not shown); fish pass around it.',
        'Rated 250 kW at 2.5 m/s with Cp 0.35; blade set is swapped for the local speed band.'])
    s.save('gen-tri-blade.svg')


# ---------------------------------------------------------------- 2. spiral blade development
def spiral():
    s = Sheet(14, 'Archimedes spiral rotor – helix development and pitch', 'Spiral Rotor – Helix Development, 1 000 Ø for 0.5 to 1.5 m/s')
    x0, y0, L, R = 230, 560, 820, 150
    s.text(x0 + L / 2, 262, 'SIDE ELEVATION – TWO-START HELIX', 14, anchor='middle')
    s.line(x0 - 60, y0, x0 + L + 60, y0, 0.6, dash='18 6 3 6')
    s.rect(x0, y0 - 18, L, 36, 1.4)  # core
    turns = 3.0
    for start in (0, math.pi):
        pts = []
        for i in range(0, 241):
            t = i / 240
            a = start + t * turns * 2 * math.pi
            x = x0 + t * L
            y = y0 - R * math.sin(a)
            pts.append((x, y))
        d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts)
        s.path(d, 1.3)
        # hidden half (behind core) lighter
        pts2 = [(x, y0 + (y0 - y)) for x, y in pts]
        d2 = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts2)
        s.path(d2, 0.7, dash='5 5')
    pitch = L / turns
    s.dim(x0, y0 - R - 40, x0 + pitch, y0 - R - 40, 'PITCH 1 000', offset=0)
    s.dim(x0 + L + 40, y0 - R, x0 + L + 40, y0 + R, 'Ø 1 000', offset=-26)
    s.dim(x0, y0 + R + 60, x0 + L, y0 + R + 60, '3 000 length', offset=0)
    s.arrow(x0 - 190, y0 - 90, x0 - 90, y0 - 90); s.text(x0 - 190, y0 - 102, 'FLOW U = 0.5–1.5 m/s', 12.5)
    # end view
    ex, ey = 1320, 560
    s.text(ex, 262, 'END VIEW', 14, anchor='middle')
    s.circle(ex, ey, R, 1.3); s.circle(ex, ey, 18, 1.3)
    for k in range(2):
        pts = []
        for i in range(0, 121):
            t = i / 120
            a = k * math.pi + t * math.pi * 2
            r = 18 + (R - 18) * t
            pts.append((ex + r * math.cos(a), ey + r * math.sin(a)))
        s.path('M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts), 1.1)
    s.leader(ex + 100, ey - 100, ex + 150, ey - 200, 'TWO STARTS, 180° APART')
    s.leader(x0 + 400, y0 - 100, x0 + 480, y0 - 230, 'BLADE – polymer skin on helical stainless rib')
    s.scalebar(1180, 905, 60, ['0', '0.25', '0.5', '0.75', '1'], 'metres')
    s.notes('Materials / comments:', [
        'Slow open-flow rotor for rivers and channels below 1.5 m/s; open space between flights lets fish through.',
        'Helix pitch and diameter set the tip-speed ratio; the literature puts shrouded spirals at Cp 0.35 to 0.45.',
        'Core is a sealed stainless tube on the drive shaft; flights are bolted to it and replaced at service.',
        'Draws on the Rev B 07A and 07B vertical units; this sheet shows the horizontal variant for shallow reaches.'])
    s.save('gen-spiral.svg')


# ---------------------------------------------------------------- 3. drivetrain configuration
def drivetrain():
    s = Sheet(15, 'Drivetrain configuration – shaft, gearbox, alternator and switching', 'Drivetrain – One Shaft Line, Catalogue Parts, 100 kW to 2 MW')
    y = 520
    s.text(140, 262, 'SECTION THROUGH POD', 14)
    # rotor hub at left
    s.rect(120, y - 60, 90, 120, 1.4); s.text(165, y + 150, 'HUB', 12, anchor='middle')
    s.line(210, y, 420, y, 2.6); s.text(315, y - 16, 'DRIVE SHAFT Ø 150', 11.5, anchor='middle')
    for bx in (260, 380):
        s.rect(bx - 14, y - 34, 28, 68, 1.2); s.line(bx - 14, y - 34, bx + 14, y + 34, 0.6); s.line(bx + 14, y - 34, bx - 14, y + 34, 0.6)
    s.text(320, y + 60, 'MARINE SEAL + BEARING (2)', 11.5, anchor='middle')
    s.rect(420, y - 110, 230, 220, 1.5); s.text(535, y - 10, 'GEARBOX', 14, anchor='middle'); s.text(535, y + 14, '30–60 rpm  →  1 500 rpm', 12, anchor='middle'); s.text(535, y + 34, 'ratio 25:1 to 50:1', 11.5, anchor='middle')
    for k in range(5):  # gear teeth hint
        s.circle(470 + k * 0, y + 0, 1, 0)
    s.circle(470, y - 60, 30, 0.9); s.circle(520, y - 60, 18, 0.9); s.circle(600, y + 55, 36, 0.9); s.circle(548, y + 55, 14, 0.9)
    s.line(650, y, 720, y, 2.2); s.rect(700, y - 20, 36, 40, 1.0); s.text(718, y + 60, 'FLEXIBLE COUPLING', 11.5, anchor='middle')
    s.rect(736, y - 130, 320, 260, 1.5); s.text(896, y - 40, 'ALTERNATOR', 14, anchor='middle'); s.text(896, y - 16, '4-pole · 1 500 rpm · 50/60 Hz', 12, anchor='middle'); s.text(896, y + 8, '100 kW · 250 kW · 500 kW · 1 MW', 12, anchor='middle')
    for k in range(9):
        s.line(760 + k * 34, y + 40, 760 + k * 34, y + 110, 0.7)
    s.text(896, y + 128, 'cooling fins', 11, anchor='middle')
    s.line(1056, y - 80, 1130, y - 80, 1.4); s.rect(1130, y - 120, 150, 80, 1.3); s.text(1205, y - 92, 'BREAKERS', 12, anchor='middle'); s.text(1205, y - 76, '+ METERING', 12, anchor='middle')
    s.line(1280, y - 80, 1340, y - 80, 1.4); s.rect(1340, y - 130, 170, 100, 1.3); s.text(1425, y - 96, 'CONVERTER', 12, anchor='middle'); s.text(1425, y - 80, '+ TRANSFORMER', 12, anchor='middle'); s.text(1425, y - 64, 'step-up to 11 kV', 11, anchor='middle')
    s.arrow(1425, y - 30, 1425, y + 80, 1.4); s.text(1425, y + 100, 'CABLE TO SHORE / GRID', 12, anchor='middle')
    # pod envelope
    s.rect(400, y - 170, 700, 340, 1.0, dash='10 6'); s.text(750, y - 180, 'SEALED POD ENVELOPE 2 000 × 1 000 × 1 500 – lifts out as one piece', 12, anchor='middle')
    s.dim(400, y + 210, 1100, y + 210, '2 000', offset=0)
    s.dim(1130, y - 170, 1130, y + 170, '1 500', offset=-26)
    s.arrow(60, y, 115, y, 1.3); s.text(60, y - 14, 'TORQUE IN', 11.5)
    # sizing table
    tx, ty = 120, 760
    s.text(tx, ty - 8, 'UNIT SIZES – ONE DRIVETRAIN FAMILY', 13, weight='bold')
    cols = ['Unit', 'Rotor Ø', 'Pods', 'Alternators', 'Gearbox', 'Price band']
    rows = [['50 kW', '2 000', '1', '1 × 50 kW', '25:1', 'list'], ['100 kW', '3 000', '1', '1 × 100 kW', '30:1', 'list'], ['250 kW', '4 500', '1', '1 × 250 kW', '35:1', 'list'],
            ['500 kW', '6 000', '2', '2 × 250 kW', '40:1', 'tranche'], ['1 MW', '8 000', '2', '2 × 500 kW', '45:1', 'tranche'], ['2 MW', '10 000', '3', '4 rotors / shaft', '50:1', 'per project']]
    cw = [90, 100, 70, 150, 100, 110]
    x = tx
    for c, w in zip(cols, cw):
        s.text(x, ty + 14, c, 11.5, weight='bold'); x += w
    s.line(tx, ty + 20, tx + sum(cw), ty + 20, 0.8)
    for r_i, r in enumerate(rows):
        x = tx
        for c, w in zip(r, cw):
            s.text(x, ty + 38 + r_i * 17, c, 11.5); x += w
    s.notes('Materials / comments:', [
        'All six sizes share the shaft, seal, gearbox and alternator families; only the ratings change with capacity.',
        'Gearbox and alternator are catalogue genset items (NORD, SEW, WEG, Leroy-Somer class); AFE adds the pod, blades and legs.',
        'Pod lifts out on four eyes for service; a spare pod goes straight back in.',
        'Switching, protection relays and telemetry sit in the switchgear shed ashore.'], x=760)
    s.save('gen-drivetrain.svg')


# ---------------------------------------------------------------- 4. unit range (sizes sheet)
def sizes():
    s = Sheet(16, 'Unit range – six capacities, swept diameters and power at 2.5 m/s', 'Unit Range – Swept Area and Rated Output, Six Core Models')
    units = [('50 kW', 2.0), ('100 kW', 3.0), ('250 kW', 4.5), ('500 kW', 6.0), ('1 MW', 8.0), ('2 MW', 10.0)]
    k = 42  # px per metre
    x = 150; base = 700
    s.line(90, base, 1600, base, 1.0); s.text(1600, base + 18, 'RIVER BED / SEAT LEVEL', 11, anchor='end')
    for name, d in units:
        r = d * k / 2
        cx = x + r
        s.circle(cx, base - r - 20, r, 1.3)
        s.circle(cx, base - r - 20, r * 0.12, 1.0)
        s.line(cx - r * 0.12, base - r - 20, cx + r * 0.12, base - r - 20, 0.8)
        for leg in (-0.6, 0.6):
            s.line(cx + leg * r, base - 20, cx + leg * r, base, 1.2)
        s.text(cx, base - 2 * r - 44, name, 16, anchor='middle', family=SERIF)
        s.text(cx, base - 2 * r - 26, f'Ø {d:.0f} m', 12, anchor='middle')
        s.text(cx, base + 40, f'A = {math.pi * (d / 2) ** 2:,.1f} m²', 11.5, anchor='middle')
        s.text(cx, base + 58, f'P = {0.5 * 1025 * math.pi * (d / 2) ** 2 * 2.5 ** 3 * 0.35 / 1000:,.0f} kW at 2.5 m/s', 11.5, anchor='middle')
        x += 2 * r + 60
    s.text(90, 262, 'FRONT ELEVATIONS – SAME SCALE', 14)
    s.text(1360, 262, 'P = ½ · ρ · A · U³ · Cp     ρ = 1 025 kg/m³     Cp = 0.35', 12.5)
    s.rect(1100, 780, 480, 150, 0.9)
    s.text(1120, 804, 'CONTAINER CHECK', 12.5, weight='bold')
    s.text(1120, 826, 'Blades nest; hubs, pods, legs and cable pack in a 40 ft ISO container.', 11.5)
    s.text(1120, 844, 'Assembly on site in about four hours with a gantry.', 11.5)
    s.text(1120, 862, 'Service depth 5–25 m; river units ≥ 2 m water under walkways.', 11.5)
    s.text(1120, 880, 'Rated outputs assume the design speed; blade set chosen per site.', 11.5)
    s.scalebar(140, 905, 42, ['0', '1', '2', '3', '4', '5'], 'metres')
    s.notes('Materials / comments:', [
        'Six capacities, one drivetrain family. The 50 kW unit carries the fixed parts over the fewest kilowatts, so it costs most per megawatt.',
        'Swept diameters are planning figures; the 2 MW unit uses four rotors on one shaft line in a steel cradle (see sheet 15).',
        'Power shown is rotor output before gearbox and alternator losses.'], x=640)
    s.save('gen-sizes.svg')


# ---------------------------------------------------------------- 5. equations and test speeds
def equations():
    s = Sheet(17, 'Design equations and the ten test speeds', 'Hydrokinetic Power – Working Equations and Test Matrix')
    x = 110
    s.text(x, 270, 'POWER IN A MOVING FLUID', 13, weight='bold')
    s.text(x, 316, 'P = ½ · ρ · A · U³ · Cp', 34, family=SERIF)
    s.text(x, 346, 'P  power at the rotor, W       ρ  fluid density, kg/m³       A  swept area, m²       U  flow speed, m/s       Cp  power coefficient', 12)
    s.text(x, 392, 'Betz limit:   Cp,max = 16 ⁄ 27 = 0.593          AFE design value:  Cp = 0.35 (shrouded 0.35–0.45, Darrieus 0.20–0.35)', 13, family=SERIF)
    s.text(x, 440, 'DENSITY RATIO', 13, weight='bold')
    s.text(x, 482, 'ρ sea ⁄ ρ air  =  1 025 ⁄ 1.225  ≈  837        ⇒ equal power per m² at   U water = U wind ÷ ∛837 ≈ U wind ÷ 9.4', 15, family=SERIF)
    s.text(x, 506, 'A 12 m/s wind and a 1.3 m/s current carry about the same power per square metre.', 12)
    s.text(x, 554, 'ROTOR SIZE FOR A TARGET OUTPUT', 13, weight='bold')
    s.text(x, 594, 'A = P ⁄ (½ · ρ · U³ · Cp)          D = 2 · √(A ⁄ π)          e.g. 100 kW at 2.5 m/s:  A = 35.7 m²,  D = 6.7 m', 15, family=SERIF)
    s.text(x, 640, 'TIP-SPEED RATIO AND SHAFT SPEED', 13, weight='bold')
    s.text(x, 680, 'λ = ω · R ⁄ U          n = 60 · λ · U ⁄ (2 · π · R)          λ 1.5–2.5 for slow spirals,  4–6 for tri-blade rotors  →  30–60 rpm at the hub', 15, family=SERIF)
    s.text(x, 726, 'SITE SPEED BY DRIFT', 13, weight='bold')
    s.text(x, 764, 'U ≈ drift distance ⁄ time:   100 m in 60 s = 1.67 m/s ≈ 3.2 kn         1 kn = 0.514 m/s', 15, family=SERIF)
    # test matrix table (right)
    tx, ty = 1010, 270
    s.text(tx, ty, 'TEN TEST SPEEDS – POWER PER m² OF ROTOR (ρ 1 025, Cp 0.35)', 13, weight='bold')
    s.text(tx, ty + 28, 'U (m/s)', 12, weight='bold'); s.text(tx + 110, ty + 28, 'knots', 12, weight='bold'); s.text(tx + 200, ty + 28, 'kW/m²', 12, weight='bold'); s.text(tx + 300, ty + 28, 'D for 100 kW', 12, weight='bold'); s.text(tx + 440, ty + 28, 'vs wind 12 m/s', 12, weight='bold')
    s.line(tx, ty + 34, tx + 560, ty + 34, 0.8)
    wind = 0.5 * 1.225 * 12 ** 3 * 0.35
    for i, u in enumerate([0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]):
        pa = 0.5 * 1025 * u ** 3 * 0.35
        d = 2 * math.sqrt(100000 / pa / math.pi)
        yy = ty + 56 + i * 22
        s.text(tx, yy, f'{u:.1f}', 12.5); s.text(tx + 110, yy, f'{u / 0.514:.1f}', 12.5); s.text(tx + 200, yy, f'{pa / 1000:.2f}', 12.5); s.text(tx + 300, yy, f'{d:.1f} m', 12.5); s.text(tx + 440, yy, f'{pa / wind:.2f} ×', 12.5)
    s.line(tx, ty + 56 + 10 * 22 - 14, tx + 560, ty + 56 + 10 * 22 - 14, 0.8)
    # small curve P/A vs U
    gx, gy, gw, gh = 1010, 560, 560, 300
    s.rect(gx, gy, gw, gh, 0.9)
    s.text(gx, gy - 8, 'kW/m² against U (cubic)', 12)
    pts = []
    for i in range(0, 101):
        u = 0.5 + 4.5 * i / 100
        pa = 0.5 * 1025 * u ** 3 * 0.35 / 1000
        pts.append((gx + gw * (u - 0.5) / 4.5, gy + gh - gh * pa / 22.4))
    s.path('M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts), 1.6)
    for u in (1, 2, 3, 4, 5):
        xx = gx + gw * (u - 0.5) / 4.5
        s.line(xx, gy + gh, xx, gy + gh + 6, 0.8); s.text(xx, gy + gh + 20, f'{u}', 11, anchor='middle')
    for pa in (5, 10, 15, 20):
        yy = gy + gh - gh * pa / 22.4
        s.line(gx - 6, yy, gx, yy, 0.8); s.text(gx - 10, yy + 4, f'{pa}', 11, anchor='end')
    s.text(gx + gw, gy + gh + 36, 'U, m/s', 11, anchor='end')
    s.notes('Comments:', [
        'Power rises with the cube of speed: doubling the current gives eight times the power per square metre.',
        'The ten test speeds are the laboratory and field matrix for the prototype programme with AetherFab at the University of Melbourne.',
        'Wind comparison uses the same Cp for both machines and is illustrative only.'])
    s.save('gen-equations.svg')


# ---------------------------------------------------------------- 6. duct / shroud section
def duct():
    s = Sheet(18, 'Ducted rotor – shroud section, inlet screen and flow acceleration', 'Duct and Shroud – Section on Centreline, 250 kW River Unit')
    cx, cy = 700, 560
    s.text(cx, 262, 'SECTION A–A', 14, anchor='middle')
    # duct profile: converging inlet, throat, diffuser
    top = f'M{cx - 420},{cy - 250} C{cx - 300},{cy - 240} {cx - 200},{cy - 190} {cx - 120},{cy - 170} L{cx + 80},{cy - 170} C{cx + 200},{cy - 175} {cx + 320},{cy - 230} {cx + 420},{cy - 270}'
    bot = f'M{cx - 420},{cy + 250} C{cx - 300},{cy + 240} {cx - 200},{cy + 190} {cx - 120},{cy + 170} L{cx + 80},{cy + 170} C{cx + 200},{cy + 175} {cx + 320},{cy + 230} {cx + 420},{cy + 270}'
    s.path(top, 1.8); s.path(bot, 1.8)
    # wall thickness
    s.path(top.replace(f'{cy - 250}', f'{cy - 236}').replace(f'{cy - 240}', f'{cy - 226}').replace(f'{cy - 190}', f'{cy - 176}').replace(f'{cy - 170}', f'{cy - 156}').replace(f'{cy - 175}', f'{cy - 161}').replace(f'{cy - 230}', f'{cy - 216}').replace(f'{cy - 270}', f'{cy - 256}'), 0.9)
    s.path(bot.replace(f'{cy + 250}', f'{cy + 236}').replace(f'{cy + 240}', f'{cy + 226}').replace(f'{cy + 190}', f'{cy + 176}').replace(f'{cy + 170}', f'{cy + 156}').replace(f'{cy + 175}', f'{cy + 161}').replace(f'{cy + 230}', f'{cy + 216}').replace(f'{cy + 270}', f'{cy + 256}'), 0.9)
    # rotor at throat
    s.line(cx - 20, cy - 156, cx - 20, cy + 156, 2.2); s.rect(cx - 40, cy - 40, 40, 80, 1.3)
    s.line(cx, cy, cx + 260, cy, 2.0); s.rect(cx + 260, cy - 70, 140, 140, 1.3); s.text(cx + 330, cy + 100, 'POD', 12, anchor='middle')
    # inlet screen
    for k in range(-5, 6):
        s.line(cx - 400, cy + k * 44 - 6, cx - 360, cy + k * 44 + 6, 0.9)
    s.text(cx - 380, cy - 290, 'INLET SCREEN – 150 mm bars, raked', 12, anchor='middle')
    # flow arrows
    for yy in (-120, -40, 40, 120):
        s.arrow(cx - 560, cy + yy, cx - 470, cy + yy, 1.1)
    s.text(cx - 560, cy - 150, 'U∞ = 2.0 m/s', 12.5)
    for yy in (-90, 0, 90):
        s.arrow(cx + 440, cy + yy * 1.6, cx + 540, cy + yy * 1.8, 1.0)
    s.text(cx + 440, cy + 220, 'DIFFUSER – pressure recovery', 12)
    s.text(cx - 20, cy - 200, 'THROAT  U ≈ 1.4 · U∞', 12.5, anchor='middle')
    s.dim(cx - 120, cy - 170, cx + 80, cy - 170, '1 200 throat', offset=-18)
    s.dim(cx - 420, cy - 250, cx - 420, cy + 250, 'Ø 3 000 inlet', offset=30)
    s.dim(cx + 420, cy - 270, cx + 420, cy + 270, 'Ø 3 200 outlet', offset=-30)
    s.dim(cx - 420, cy + 330, cx + 420, cy + 330, '4 200 overall', offset=0)
    s.scalebar(1180, 905, 60, ['0', '0.5', '1', '1.5', '2'], 'metres')
    s.notes('Materials / comments:', [
        'Shroud: rolled recycled-polymer panels on a stainless ring frame; bolted segments for container shipping.',
        'The converging inlet raises throat speed about 1.4×, which the cube law turns into roughly 2.7× the power per m² of rotor.',
        'Screen bars keep fish and flotsam out of the blade zone; spacing set with the fisheries regulator during trials.',
        'Duct also carries the unit\'s lifting points and the clamps for pylon or leg mounting.'])
    s.save('gen-duct.svg')


# ---------------------------------------------------------------- 7. pylon-mounted unit
def pylon():
    s = Sheet(19, 'River unit on a bridge pylon – elevation with water levels', 'Pylon Mount – Lee-Side Unit, Normal and Flood Water Levels')
    # pylon
    px, top, bed = 760, 230, 900
    s.rect(px - 70, top, 140, bed - top, 1.6)
    s.rect(px - 110, top, 220, 40, 1.6); s.text(px, top - 10, 'BRIDGE DECK / PIER CAP', 12, anchor='middle')
    for yy in range(top + 80, bed, 60):
        s.line(px - 70, yy, px + 70, yy, 0.5)
    # bed
    s.path(f'M100,{bed} C300,{bed - 20} 500,{bed + 12} {px - 70},{bed} M{px + 70},{bed} C1000,{bed + 10} 1300,{bed - 14} 1600,{bed}', 1.6)
    for xx in range(120, 1600, 40):
        s.line(xx, bed + 10, xx - 14, bed + 24, 0.6)
    # water levels
    for lvl, name, dash in ((560, 'NORMAL WATER LEVEL  ▽', None), (380, 'FLOOD LEVEL  ▽', '10 6')):
        s.line(100, lvl, 1600, lvl, 1.0, dash=dash); s.text(110, lvl - 8, name, 12)
    # unit on lee side (right)
    ux, uy = px + 70 + 60, 700
    s.line(px + 70, 600, ux + 40, 600, 1.4); s.line(px + 70, 800, ux + 40, 800, 1.4)
    s.rect(ux + 40, 600, 24, 200, 1.4)  # mounting frame
    s.circle(ux + 170, uy, 110, 1.4); s.circle(ux + 170, uy, 16, 1.2)
    s.line(ux + 64, uy, ux + 150, uy, 2.0)
    for a in (0, 120, 240):
        s.line(ux + 170, uy, ux + 170 + 100 * math.cos(math.radians(a)), uy - 100 * math.sin(math.radians(a)), 1.3)
    s.rect(ux + 290, uy - 60, 130, 120, 1.3); s.text(ux + 355, uy + 90, 'POD', 12, anchor='middle')
    s.line(ux + 280, uy, ux + 290, uy, 2.0)
    # vertical runner for lifting
    s.line(ux + 52, 300, ux + 52, 600, 0.8, dash='4 5'); s.text(ux + 60, 320, 'RUNNER – unit lifts clear of flood', 11.5)
    s.arrow(ux + 52, 590, ux + 52, 420, 1.0)
    # flow
    for yy in (620, 700, 780):
        s.arrow(260, yy, 380, yy, 1.1)
    s.text(260, 600, 'FLOW 1.5–3.0 m/s', 12.5)
    s.text(px, 680, 'PYLON', 12, anchor='middle', rotate=-90)
    s.dim(1600 - 40, 560, 1600 - 40, bed, '≥ 5 000 at pod', offset=-28)
    s.dim(1600 - 100, 380, 1600 - 100, 560, 'flood rise', offset=-28)
    s.dim(ux + 40, 940, ux + 420, 940, '3 800 unit + pod', offset=0)
    s.leader(px + 70 + 30, 600, px + 250, 480, 'CLAMP FRAME – no drilling into pier')
    s.leader(ux + 290 + 65, uy - 60, ux + 500, 520, 'CABLE – up the pier to the deck tray')
    s.scalebar(1180, 905, 50, ['0', '1', '2', '3', '4'], 'metres')
    s.notes('Materials / comments:', [
        'Unit sits in the lee of the pier where the flow has re-formed; two or more per pier on wide rivers.',
        'Clamp frame on stainless runners: the unit is winched up to the cap for service or ahead of a flood or debris raft.',
        'Cable runs up the pier to a deck cable tray, then to the switchgear shed at the abutment.',
        'Minimum two metres of water under walkways for slung units; five metres of clear water for fully submerged units.'])
    s.save('gen-pylon.svg')


# ---------------------------------------------------------------- 8. tidal array plan
def array():
    s = Sheet(20, 'Tidal entrance array – plan of four units and cable to shore', 'Array Plan – Four 250 kW Units in a Tidal Channel, 1 MW')
    # channel banks
    s.path('M100,300 C400,260 700,330 1000,290 S1400,260 1600,300', 1.6)
    s.path('M100,860 C400,900 700,830 1000,870 S1400,900 1600,860', 1.6)
    for xx in range(120, 1600, 60):
        s.line(xx, 290 - 10, xx - 12, 270, 0.6); s.line(xx, 870 + 10, xx - 12, 890, 0.6)
    s.text(110, 250, 'NORTH SPIT', 12); s.text(110, 925, 'SOUTH SPIT', 12)
    # units
    D = 120
    for i in range(4):
        cx = 420 + i * 3 * D * 0.8; cy = 580 + (i % 2) * 60 - 30
        s.circle(cx, cy, D / 2, 1.3); s.circle(cx, cy, 8, 1.0)
        s.rect(cx - 10, cy - D / 2 - 40, 20, 40, 1.0)
        s.text(cx, cy + D / 2 + 22, f'U-0{i + 1}  250 kW', 11.5, anchor='middle')
        if i < 3:
            s.dim(cx, 420, cx + 3 * D * 0.8, 420, '3 D', offset=0)
    # cable
    s.path('M420,520 L420,470 L1380,470 L1380,330', 1.1, dash='8 5'); s.text(900, 462, 'ARRAY CABLE – buried, to shore riser', 11.5, anchor='middle')
    s.rect(1340, 290, 80, 40, 1.2); s.text(1380, 282, 'SWITCHGEAR', 11, anchor='middle')
    # flow arrows ebb/flood
    for yy in (520, 640):
        s.arrow(180, yy, 300, yy, 1.2)
    s.text(180, 500, 'FLOOD  1.7 m/s', 12.5)
    for yy in (700, 760):
        s.arrow(1500, yy, 1380, yy, 1.2)
    s.text(1500, 790, 'EBB  1.6 m/s', 12.5, anchor='end')
    s.text(1380, 250, 'SHORE', 12, anchor='middle')
    # depth contours
    for d, yy in ((5, 400), (10, 480), (15, 560), (10, 700), (5, 780)):
        s.path(f'M120,{yy} C500,{yy - 20} 900,{yy + 15} 1580,{yy}', 0.6, dash='3 6'); s.text(1585, yy + 4, f'{d} m', 10.5)
    # shipping lane
    s.rect(100, 200, 1500, 50, 0.8, dash='12 6'); s.text(850, 230, 'SHIPPING LANE – units kept clear', 11.5, anchor='middle')
    s.scalebar(1180, 905, 40, ['0', '25', '50', '75', '100'], 'metres')
    s.text(1430, 640, 'N', 16, anchor='middle', family=SERIF); s.arrow(1430, 700, 1430, 655, 1.4)
    s.notes('Comments:', [
        'Spacing about three diameters across the channel and staggered so each unit sees clean water on both tides.',
        'Tide runs about 20 hours in 24; slack water 20 to 30 minutes at each turn, covered by a second entrance or a small battery.',
        'Drift survey by boat sets the layout: a buoy for direction, GPS drift for speed, 100 m in 60 s ≈ 1.7 m/s.',
        'Units sit below 5 m, clear of the lane; divers service from a workboat every six months.'])
    s.save('gen-array.svg')


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for fn in (tri_blade, spiral, drivetrain, sizes, equations, duct, pylon, array):
        fn()
