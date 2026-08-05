import sys
import os

path = r'c:\Users\SunilKumarKethananei\Videos\Python_gae\game\game.py'
out_path = r'c:\Users\SunilKumarKethananei\Videos\Python_gae\game\new_game.py'

with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_main = False

for i, line in enumerate(lines):
    if line.startswith('import pygame'):
        new_lines.append('import asyncio\n')
        new_lines.append(line)
    elif line.startswith('# Setup Game'):
        new_lines.append('async def main():\n')
        new_lines.append('    global current_level, player, platforms, enemies, spikes, npc, camera_x, game_over, game_won, dialogue_active, dialogue_index, enter_pressed, restart_button_rect, btn_left, btn_right, btn_jump\n')
        new_lines.append('    ' + line)
        in_main = True
    elif in_main:
        if line.startswith('    pygame.display.update()'):
            new_lines.append('        pygame.display.update()\n')
            new_lines.append('        await asyncio.sleep(0)\n')
        elif line.startswith('pygame.quit()'):
            new_lines.append('    pygame.quit()\n\n')
            new_lines.append('if __name__ == "__main__":\n')
            new_lines.append('    asyncio.run(main())\n')
        elif line.strip() == '':
            new_lines.append(line)
        else:
            new_lines.append('    ' + line)
    else:
        new_lines.append(line)

with open(out_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
