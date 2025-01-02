import cairo
from timcam.cairo_pil import to_pil


def test_argb32():
    # Size chosen with the hope it not being a multiple of 4 is more likely to
    # test unusual stride
    img = cairo.ImageSurface(cairo.FORMAT_ARGB32, 21, 20)
    ctx = cairo.Context(img)

    # excluding right and bottom lines
    ctx.rectangle(0, 0, 20, 19)
    ctx.set_source_rgb(0, 0, 0)
    ctx.fill()

    # without changing the matrix, this should be upper-left
    ctx.rectangle(0, 0, 10, 10)
    ctx.set_source_rgb(1, 0, 0)
    ctx.fill()
    pil_image = to_pil(img)
    assert pil_image.getpixel((0, 0)) == (255, 0, 0, 255)
    assert pil_image.getpixel((19, 0)) == (0, 0, 0, 255)
    assert pil_image.getpixel((0, 18)) == (0, 0, 0, 255)
    assert pil_image.getpixel((20, 19)) == (0, 0, 0, 0)


def test_rgb24():
    # Size chosen with the hope it not being a multiple of 4 is more likely to
    # test unusual stride
    img = cairo.ImageSurface(cairo.FORMAT_RGB24, 21, 20)
    ctx = cairo.Context(img)

    # excluding right and bottom lines
    ctx.rectangle(0, 0, 21, 20)
    ctx.set_source_rgb(0, 0, 0)
    ctx.fill()

    # without changing the matrix, this should be upper-left
    ctx.rectangle(0, 0, 10, 10)
    ctx.set_source_rgb(1, 0, 0)
    ctx.fill()
    pil_image = to_pil(img)
    assert pil_image.getpixel((0, 0)) == (255, 0, 0)
    assert pil_image.getpixel((20, 0)) == (0, 0, 0)
    assert pil_image.getpixel((0, 19)) == (0, 0, 0)
    assert pil_image.getpixel((20, 19)) == (0, 0, 0)
