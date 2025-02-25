import os

import pygame

if __name__ == '__main__':
    in_tileset_name: str = "tileset.png"
    tile_size: int = 16
    out: str = "images/tiles/desert"
    ignore_empty: bool = True

    os.chdir('..');os.chdir('..');os.chdir('..')

    img = pygame.image.load(in_tileset_name)
    width, height = img.get_size()

    rows = width // tile_size
    columns = height // tile_size

    tiles: list[pygame.Surface] = []

    def load_tile(image: pygame.Surface, x: int, y: int) -> pygame.Surface|None:
       tile = pygame.Surface((tile_size, tile_size))
       has_color: bool = False

       x *= tile_size
       y *= tile_size

       for x_ in range(tile_size):
           for y_ in range(tile_size):
               i = x + x_
               j = y + y_

               col = image.get_at((i, j))
               if not has_color and col[0] + col[1] + col[2] > 0:
                   has_color = True

               tile.set_at((x_, y_), col)

       if ignore_empty and not has_color:
           return None

       return tile

    for xx in range(rows):
        for yy in range(columns):
            tile = load_tile(img, xx, yy)
            if tile is None:
                continue

            tiles.append(tile)

    os.mkdir(out)

    for i, tile in enumerate(tiles):
        pygame.image.save(tile, f"{out}/{i}.png")
