import math
from pathlib import Path

import discord

from chat_exporter.ext.discord_utils import DiscordUtils
from chat_exporter.ext.html_generator import (
    fill_out,
    img_attachment,
    msg_attachment,
    audio_attachment,
    video_attachment,
    PARSE_MODE_NONE,
)


class Attachment:
    def __init__(self, attachment: discord.Attachment, guild, file_path):
        self.attachment = attachment
        self.guild = guild
        self.file_path = file_path
        self.file_name = None
        if self.file_path:
            self.file_name = file_path.split('/')[-1]

    async def flow(self):
        await self.build_attachment()
        return self.attachment

    async def build_attachment(self):
        if self.file_path:
            await self.attachment.save(Path(self.file_path), use_cached=True)

        if self.attachment.content_type is not None:
            if "image" in self.attachment.content_type:
                return await self.image()
            elif "video" in self.attachment.content_type:
                return await self.video()
            elif "audio" in self.attachment.content_type:
                return await self.audio()
        await self.file()

    async def image(self):
        self.attachment = await fill_out(self.guild, img_attachment, [
            ("ATTACH_URL", self.file_name or self.attachment.proxy_url, PARSE_MODE_NONE),
            ("ATTACH_URL_THUMB", self.file_name or self.attachment.proxy_url, PARSE_MODE_NONE)
        ])

    async def video(self):
        self.attachment = await fill_out(self.guild, video_attachment, [
            ("ATTACH_URL", self.file_name or self.attachment.proxy_url, PARSE_MODE_NONE)
        ])

    async def audio(self):
        file_icon = DiscordUtils.file_attachment_audio
        file_size = self.get_file_size(self.attachment.size)

        self.attachment = await fill_out(self.guild, audio_attachment, [
            ("ATTACH_ICON", file_icon, PARSE_MODE_NONE),
            ("ATTACH_URL", self.file_name or self.attachment.url, PARSE_MODE_NONE),
            ("ATTACH_BYTES", str(file_size), PARSE_MODE_NONE),
            ("ATTACH_AUDIO", self.file_name or self.attachment.proxy_url, PARSE_MODE_NONE),
            ("ATTACH_FILE", str(self.attachment.filename), PARSE_MODE_NONE)
        ])

    async def file(self):
        file_icon = await self.get_file_icon()

        file_size = self.get_file_size(self.attachment.size)

        self.attachment = await fill_out(self.guild, msg_attachment, [
            ("ATTACH_ICON", file_icon, PARSE_MODE_NONE),
            ("ATTACH_URL", self.file_name or self.attachment.url, PARSE_MODE_NONE),
            ("ATTACH_BYTES", str(file_size), PARSE_MODE_NONE),
            ("ATTACH_FILE", str(self.attachment.filename), PARSE_MODE_NONE)
        ])

    @staticmethod
    def get_file_size(file_size):
        if file_size == 0:
            return "0 bytes"
        size_name = ("bytes", "KB", "MB")
        i = int(math.floor(math.log(file_size, 1024)))
        p = math.pow(1024, i)
        s = round(file_size / p, 2)
        return "%s %s" % (s, size_name[i])

    async def get_file_icon(self) -> str:
        acrobat_types = "pdf"
        webcode_types = "html", "htm", "css", "rss", "xhtml", "xml"
        code_types = "py", "cgi", "pl", "gadget", "jar", "msi", "wsf", "bat", "php", "js"
        document_types = (
            "txt", "doc", "docx", "rtf", "xls", "xlsx", "ppt", "pptx", "odt", "odp", "ods", "odg", "odf", "swx",
            "sxi", "sxc", "sxd", "stw"
        )
        archive_types = (
            "br", "rpm", "dcm", "epub", "zip", "tar", "rar", "gz", "bz2", "7x", "deb", "ar", "Z", "lzo", "lz", "lz4",
            "arj", "pkg", "z"
        )

        extension = self.attachment.url.rsplit('.', 1)[1]
        if extension in acrobat_types:
            return DiscordUtils.file_attachment_acrobat
        elif extension in webcode_types:
            return DiscordUtils.file_attachment_webcode
        elif extension in code_types:
            return DiscordUtils.file_attachment_code
        elif extension in document_types:
            return DiscordUtils.file_attachment_document
        elif extension in archive_types:
            return DiscordUtils.file_attachment_archive
        else:
            return DiscordUtils.file_attachment_unknown
