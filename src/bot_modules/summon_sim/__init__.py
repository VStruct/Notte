import hook
import logging
import discord
from . import core, db, image

logger = logging.getLogger(__name__)


async def on_init(discord_client):
    db.create_db()

    hook.Hook.get("public!tenfold").attach(tenfold_summon)
    hook.Hook.get("public!single").attach(single_summon)
    hook.Hook.get("public!showcase").attach(select_showcase)


async def select_showcase(message, args):
    """
    Selects a showcase to summon on. To select a showcase, use `showcase <showcase>`.
    To get information about your currently selected showcase, use `showcase`.
    To get a list of showcases, use `showcase list`.
    To get information about a showcase, use `showcase info <showcase>`.
    To select a generic showcase without any rate-up units or dragons, use `showcase none`.

    **Note:** Showcases as represented in the summoning simulator aren't historically accurate. This means:
     - All currently available permanent units are able to be pulled as off-focus units
     - Wyrmprints aren't summonable in the showcases which featured them
     - Showcases which appeared prior to the 5★ dragon rate change on July 31st, 2019 will use the new dragon rates
    """
    args = args.strip()
    if args == "list":
        await message.channel.send(", ".join(sc.name for sc in core.get_summonable_showcase_list()))
    elif args.split(" ")[0].lower() == "info" or not args:
        showcase_name = args[5:].strip()
        if not showcase_name:
            showcase_info, showcase = db.get_current_showcase_info(message.channel.id, message.author.id)
            if showcase == core.get_summonable_showcase("none"):
                await message.channel.send(showcase_info)
            else:
                await message.channel.send(showcase_info, embed=showcase.get_embed())
        else:
            showcase = core.get_summonable_showcase(showcase_name)
            if showcase and showcase != core.get_summonable_showcase("none"):
                await message.channel.send(embed=showcase.get_embed())
            else:
                await message.channel.send("I don't know that showcase! Use `showcase list` to see the list of showcases.")
    else:
        showcase = core.get_summonable_showcase(args)
        if showcase:
            await message.channel.send(db.set_showcase(message.channel.id, message.author.id, showcase))
        else:
            await message.channel.send("I don't know that showcase! Use `showcase list` to see the list of showcases.")


async def tenfold_summon(message, args):
    """
    Simulates a tenfold summon on your current showcase.
    To choose a showcase to summon on, use the `showcase` command.
    """
    results, text = db.perform_summon(message.channel.id, message.author.id, is_tenfold=True)
    with image.get_tenfold_image_fp(results) as fp:
        await message.channel.send(text, file=discord.File(fp, filename="tenfold.png"))


async def single_summon(message, args):
    """
    Simulates a single summon on your current showcase.
    To choose a showcase to summon on, use the `showcase` command.
    """
    result, text = db.perform_summon(message.channel.id, message.author.id, is_tenfold=False)
    with image.get_single_image_fp(result) as fp:
        await message.channel.send(text, file=discord.File(fp, filename="single.png"))


hook.Hook.get("on_init").attach(on_init)
