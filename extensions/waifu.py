from typing import Literal
from datetime import datetime
from aiohttp import ClientSession

from discord import (
    app_commands as ac,
    Interaction,
    Embed,
    Color,
    ButtonStyle
)
from discord.app_commands import Choice, Group
from discord.ext.commands import Bot
from discord.ui import View, Button

from utils import get_lumberjack, cd_but_soymilk
from bot import Soybot

log = get_lumberjack('waifu')
waifu_im_api = 'https://api.waifu.im'


async def fetch_waifu(cs: ClientSession, url: str) -> dict:
    async with cs.get(url) as resp:
        data = await resp.json()

    image = data['images'][0]
    return image


def build_waifu_embed_view(title: str, image: dict) -> tuple[Embed, View]:
    tags = [t['name'] for t in image['tags']]
    embed = Embed(
        title=title,
        description=''.join([f'#{t}' for t in tags]),
        color=Color.from_str(image['dominant_color']),
        timestamp=datetime.fromisoformat(image['uploaded_at']),
    ).set_image(
        url=image['url'],
    ).set_footer(
        text='uploaded at'
    )
    view = View().add_item(Button(
        style=ButtonStyle.link,
        url=image['source'],
        label='查看圖源',
    ))

    return embed, view


class WaifuGroup(Group, name='waifu'):

    @ac.command(
        name='waifu-sfw',
        # description='waifu-sfw_desc'
    )
    @ac.describe(tag='tag')
    @ac.rename(tag='tag')
    # @ac.choices(
    #     tag=[
    #         Choice(
    #             name=option,
    #             value=tag_name
    #         ) for option, tag_name in {
    # '老婆': 'waifu',
    # '制服': 'uniform',
    # '女僕': 'maid',
    # '森美聲': 'mori-calliope',
    # '喜多川海夢': 'marin-kitagawa',
    # '原神 雷電將軍': 'raiden-shogun',
    # '大奶': 'oppai',
    # '自拍': 'selfies',
    #         }.items()
    #     ]
    # )
    @ac.checks.dynamic_cooldown(cd_but_soymilk)
    async def sfw_coro(
        self,
        intx: Interaction,
        tag: Literal[
            'waifu-sfw_waifu',
            'waifu-sfw_uniform',
            'waifu-sfw_maid',
            'waifu-sfw_mori-calliope',
            'waifu-sfw_marin-kitagawa',
            'waifu-sfw_raiden-shogun',
            'waifu-sfw_oppai',
            'waifu-sfw_selfies',
        ] = None
    ):
        await intx.response.defer(thinking=True)

        if tag is not None:
            title = tag.name
            url = f'{waifu_im_api}/search?included_tags={tag.value}'
        else:
            title = '隨機'
            url = f'{waifu_im_api}/search'

        bot: Soybot = intx.client
        try:
            image = await fetch_waifu(bot.cs, url)
            embed, view = build_waifu_embed_view(title, image)
            await intx.followup.send(embed=embed, view=view)
        except KeyError:
            await intx.followup.send('醒 你沒老婆')

    @ac.command(
        name='waifu-nsfw',
        # description='waifu-nsfw_desc',
        nsfw=True
    )
    @ac.describe(tag='tag')
    @ac.rename(tag='tag')
    # @ac.choices(
    #     tag=[
    #         Choice(
    #             name=option,
    #             value=tag_name
    #         ) for option, tag_name in {
    #             'Hentai': 'hentai',
    #             '人妻': 'milf',
    #             '咬': 'oral',
    #             '大奶': 'paizuri',
    #             'H': 'ecchi',
    #             '尻': 'ass',
    #             '色色': 'ero',
    #         }.items()
    #     ]
    # )
    @ac.checks.dynamic_cooldown(cd_but_soymilk)
    async def nsfw_coro(
        self,
        intx: Interaction,
        tag: Literal[
            'waifu-nsfw_hentai',
            'waifu-nsfw_milf',
            'waifu-nsfw_oral',
            'waifu-nsfw_paizuri',
            'waifu-nsfw_ecchi',
            'waifu-nsfw_ass',
            'waifu-nsfw_ero',
        ] = None
    ):
        if not intx.channel.nsfw:
            await intx.response.send_message(
                '😡😡請勿在非限制級頻道色色 **BONK!**\n' +
                '請至**限制級頻道**',
                ephemeral=True)
            return

        await intx.response.defer(thinking=True)

        url = f'{waifu_im_api}/search?is_nsfw=true'
        if tag is not None:
            title = tag.name
            url += f'&included_tags={tag.value}'
        else:
            title = '隨機'

        bot: Soybot = intx.client
        try:
            image = await fetch_waifu(bot.cs, url)
        except KeyError:
            await intx.followup.send('不可以色色')
            return

        embed, view = build_waifu_embed_view(title, image)

        await intx.followup.send(embed=embed, view=view)


async def setup(bot: Bot):
    bot.tree.add_command(WaifuGroup())
    log.info(f'{__name__} loaded')
