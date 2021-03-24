import os

for _,_, files in os.walk('./musics'):
    for file in files:
        title, singer = file.rsplit('-', 1)
        title = title.strip()
        singer = singer.strip()
        os.rename(f'./musics/{file}', f'./musics/{title}-{singer}')