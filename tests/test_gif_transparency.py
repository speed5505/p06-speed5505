# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license

from io import BytesIO
from os.path import abspath, dirname, join

from PIL import Image
from tornado.testing import gen_test

from tests.handlers.test_base_handler import BaseImagingTestCase
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.importer import Importer

COURSE_IMAGES = abspath(join(dirname(__file__), "../course/images"))


class ResizedStickerGifKeepsTransparencyTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = COURSE_IMAGES
        cfg.STORAGE = "thumbor.storages.no_storage"
        cfg.ALLOW_UNSAFE_URL = True

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"

        return Context(server, cfg, importer)

    @gen_test
    async def test_resized_sticker_gif_has_transparent_corners(self):
        response = await self.async_fetch("/unsafe/240x160/sticker.gif")

        assert response.code == 200
        assert response.headers["Content-Type"] == "image/gif"

        image = Image.open(BytesIO(response.body))
        assert image.size == (240, 160)
        assert "transparency" in image.info

        rgba = image.convert("RGBA")
        width, height = rgba.size
        corners = [(0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)]
        for corner in corners:
            assert rgba.getpixel(corner)[3] == 0, f"corner {corner} is opaque"
        assert rgba.getpixel((width // 2, height // 2))[3] == 255
