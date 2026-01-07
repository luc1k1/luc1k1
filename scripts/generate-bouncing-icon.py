#!/usr/bin/env python3
"""
Generate a bouncing icon animation SVG with physics-based movement,
changing icons on collision, and random gradient backgrounds.
"""

import random
import math
from datetime import datetime

# Configuration
CANVAS_WIDTH = 400
CANVAS_HEIGHT = 400
ICON_SIZE = 60
ANIMATION_DURATION = 10  # seconds
ICON_SET = ['🚀', '💎', '⚡', '🔥', '💫', '🎮', '🎯', '🌟', '✨', '🎨', '🌈', '👾']

# Color palettes for gradients
COLOR_PALETTES = [
    ['#667eea', '#764ba2'],
    ['#f093fb', '#f5576c'],
    ['#4facfe', '#00f2fe'],
    ['#43e97b', '#38f9d7'],
    ['#fa709a', '#fee140'],
    ['#30cfd0', '#330867'],
    ['#a8edea', '#fed6e3'],
    ['#ff9a9e', '#fecfef'],
    ['#ffecd2', '#fcb69f'],
    ['#ff6e7f', '#bfe9ff'],
    ['#e0c3fc', '#8ec5fc'],
    ['#fbc2eb', '#a6c1ee'],
]


def generate_random_gradient():
    """Generate random gradient colors from palette."""
    palette = random.choice(COLOR_PALETTES)
    angle = random.randint(0, 360)
    return palette[0], palette[1], angle


def calculate_bounces(start_x, start_y, vel_x, vel_y, duration, fps=60):
    """
    Calculate bouncing trajectory with icon changes on collision.
    Returns list of keyframes with position and icon index.
    """
    frames = []
    x, y = start_x, start_y
    vx, vy = vel_x, vel_y
    icon_index = 0
    
    # Boundaries (accounting for icon size)
    min_x, max_x = ICON_SIZE / 2, CANVAS_WIDTH - ICON_SIZE / 2
    min_y, max_y = ICON_SIZE / 2, CANVAS_HEIGHT - ICON_SIZE / 2
    
    total_frames = int(duration * fps)
    
    for frame in range(total_frames):
        # Store current state
        progress = frame / total_frames * 100
        frames.append({
            'progress': progress,
            'x': x,
            'y': y,
            'icon_index': icon_index
        })
        
        # Update position
        x += vx
        y += vy
        
        # Check collisions and bounce
        bounced = False
        if x <= min_x or x >= max_x:
            vx = -vx
            x = max(min_x, min(max_x, x))
            bounced = True
        
        if y <= min_y or y >= max_y:
            vy = -vy
            y = max(min_y, min(max_y, y))
            bounced = True
        
        # Change icon on collision
        if bounced:
            icon_index = (icon_index + 1) % len(ICON_SET)
    
    return frames


def generate_svg_animation():
    """Generate the complete SVG with bouncing animation."""
    # Random starting position and velocity
    start_x = random.uniform(ICON_SIZE, CANVAS_WIDTH - ICON_SIZE)
    start_y = random.uniform(ICON_SIZE, CANVAS_HEIGHT - ICON_SIZE)
    vel_x = random.uniform(2, 4) * random.choice([-1, 1])
    vel_y = random.uniform(2, 4) * random.choice([-1, 1])
    
    # Generate gradient colors
    color1, color2, angle = generate_random_gradient()
    
    # Calculate trajectory
    frames = calculate_bounces(start_x, start_y, vel_x, vel_y, ANIMATION_DURATION)
    
    # Sample frames for keyframes (use every 15th frame to keep SVG size reasonable)
    sampled_frames = [frames[i] for i in range(0, len(frames), 15)]
    if frames[-1] not in sampled_frames:
        sampled_frames.append(frames[-1])
    
    # Build CSS animation keyframes for position
    position_keyframes = []
    for frame in sampled_frames:
        position_keyframes.append(
            f"  {frame['progress']:.2f}% {{ transform: translate({frame['x']:.2f}px, {frame['y']:.2f}px); }}"
        )
    
    # Build icon change keyframes
    icon_keyframes = []
    current_icon = 0
    for i, frame in enumerate(sampled_frames):
        if frame['icon_index'] != current_icon or i == 0:
            current_icon = frame['icon_index']
            # Set visibility for this icon at this progress point
            for icon_idx in range(len(ICON_SET)):
                opacity = '1' if icon_idx == current_icon else '0'
                icon_keyframes.append(
                    f"  {frame['progress']:.2f}% {{ .icon-{icon_idx} {{ opacity: {opacity}; }} }}"
                )
    
    # Generate SVG
    svg_content = f'''<svg width="{CANVAS_WIDTH}" height="{CANVAS_HEIGHT}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%" gradientTransform="rotate({angle})">
      <stop offset="0%" style="stop-color:{color1};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{color2};stop-opacity:1" />
    </linearGradient>
    
    <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
      <feOffset dx="2" dy="2" result="offsetblur"/>
      <feComponentTransfer>
        <feFuncA type="linear" slope="0.3"/>
      </feComponentTransfer>
      <feMerge>
        <feMergeNode/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    
    <style>
      @keyframes bounce {{
{chr(10).join(position_keyframes)}
      }}
      
      .icon-container {{
        animation: bounce {ANIMATION_DURATION}s linear infinite;
        transform-origin: center;
      }}
      
      .icon {{
        transition: opacity 0.1s;
      }}
'''
    
    # Add individual icon opacity animations
    for icon_idx in range(len(ICON_SET)):
        icon_keyframes_for_idx = []
        current_shown = 0
        for frame in sampled_frames:
            opacity = '1' if frame['icon_index'] == icon_idx else '0'
            icon_keyframes_for_idx.append(
                f"        {frame['progress']:.2f}% {{ opacity: {opacity}; }}"
            )
        
        svg_content += f'''      
      @keyframes icon-anim-{icon_idx} {{
{chr(10).join(icon_keyframes_for_idx)}
      }}
      
      .icon-{icon_idx} {{
        animation: icon-anim-{icon_idx} {ANIMATION_DURATION}s step-end infinite;
      }}
'''
    
    svg_content += '''    </style>
  </defs>
  
  <!-- Background -->
  <rect width="100%" height="100%" rx="20" ry="20" fill="url(#bgGradient)"/>
  
  <!-- Bouncing icons -->
  <g class="icon-container" filter="url(#shadow)">
'''
    
    # Add all icons as text elements
    for idx, icon in enumerate(ICON_SET):
        svg_content += f'''    <text class="icon icon-{idx}" x="{-ICON_SIZE/2}" y="{ICON_SIZE/4}" font-size="{ICON_SIZE}" text-anchor="middle">{icon}</text>
'''
    
    svg_content += '''  </g>
</svg>'''
    
    return svg_content


def main():
    """Main function to generate and save the SVG."""
    svg_content = generate_svg_animation()
    
    # Save to file
    output_file = 'bouncing-icon.svg'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    print(f"Generated {output_file} successfully!")
    print(f"Timestamp: {datetime.now().isoformat()}")


if __name__ == '__main__':
    main()
