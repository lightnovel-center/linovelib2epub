# setup TesseractOCR

[下载页面](https://tesseract-ocr.github.io/tessdoc/Installation.html)，选择合适的平台，然后下载合适的版本。

以 windows 平台，tesseract 5.5 版本 `tesseract-ocr-w64-setup-5.5.0.20241111.exe` 为例。

安装时，注意勾选简体中文、繁体中文、日语语言扩展包，因为日语轻小说就这三种语言最为常见。
将安装后的 tesseract 主文件夹（在 windows 系统中例如 `C:\Program Files\Tesseract-OCR`）加入到系统变量 PATH 或者用户变量
PATH。然后打开一个 terminal 验证是否可用。

```bash
>tesseract -v
tesseract v5.5.0.20241111
 leptonica-1.85.0
  libgif 5.2.2 : libjpeg 8d (libjpeg-turbo 3.0.4) : libpng 1.6.44 : libtiff 4.7.0 : zlib 1.3.1 : libwebp 1.4.0 : libopenjp2 2.5.2
 Found AVX2
 Found AVX
 Found FMA
 Found SSE4.1
 Found libarchive 3.7.7 zlib/1.3.1 liblzma/5.6.3 bz2lib/1.0.8 liblz4/1.10.0 libzstd/1.5.6
 Found libcurl/8.11.0 Schannel zlib/1.3.1 brotli/1.1.0 zstd/1.5.6 libidn2/2.3.7 libpsl/0.21.5 libssh2/1.11.0
```

如果能正常显示版本号，那就安装完毕了。