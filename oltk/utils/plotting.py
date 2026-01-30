def generate_purple_lin_scale(n_points):
    colors = []

    r1, g1, b1 = int("E8", 16), int("D9", 16), int("FF", 16)
    r2, g2, b2 = int("4B", 16), int("00", 16), int("82", 16)

    for i in range(n_points):
        t = i / (n_points - 1)


        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)

        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        colors.append(hex_color)

    return colors

def generate_purple_with_fade_lin_scale(n_points, min_alpha=0.25, max_alpha=0.95):
    colors = []

    r1, g1, b1 = int("E8", 16), int("D9", 16), int("FF", 16)
    r2, g2, b2 = int("4B", 16), int("00", 16), int("82", 16)

    for i in range(n_points):
        t = i / (n_points - 1)
        
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)

        alpha = min_alpha + (max_alpha - min_alpha) * t
        
        rgba_color = f"rgba({r}, {g}, {b}, {alpha:.3f})"
        colors.append(rgba_color)
    
    return colors


#Need to make them customizable - generate ruby, saphire, obsidian and emerald colour schemes