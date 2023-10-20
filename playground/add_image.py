from linovelib2epub.models import LightNovelChapter, LightNovelImage

light_novel_chapter = LightNovelChapter(chapter_id=1)
light_novel_chapter.add_illustration(LightNovelImage(remote_src="1"))
light_novel_chapter.add_illustration(LightNovelImage(remote_src="2"))
light_novel_chapter.add_illustration(LightNovelImage(remote_src="3"))

print(light_novel_chapter.illustrations)
