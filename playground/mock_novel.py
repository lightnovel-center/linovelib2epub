from linovelib2epub.linovel import *

new_novel = LightNovel()

new_volume = LightNovelVolume(vid=0)
new_volume.title = 'volume'

new_volume.add_chapter(cid=0, title='chapter_title', content='chapter_content')

new_novel.add_volume(vid=new_volume.vid, title=new_volume.title, chapters=new_volume.chapters)

print(new_novel.volumes)
