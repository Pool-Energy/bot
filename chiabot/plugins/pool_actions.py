import aiohttp
import logging
import datetime

from chiabot.plugin import PluginBase

logger = logging.getLogger('pool_actions')


class PoolActions(PluginBase):

    NAME = 'pool_actions'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self, client):
        logger.info(f"Bot {client.user} is ready and now read messages in channel {self.config['pool_actions']['channel']}")

    async def on_message(self, client, message):
        channel_id = self.config['pool_actions'].get('channel_id') or None

        if channel_id is not None and message.channel.id != channel_id:
            return

        # help
        if message.content.startswith(('!help', '!commands')):
            await message.channel.send(
                '```'
                '!stats - Get pool statistics\n'
                '!farmer <launcher_id> - Get information about a farmer\n'
                '```'
            )

        # stats
        if message.content.startswith('!stats'):
            json = await self.get_stats()
            if not json:
                return

            async with aiohttp.request("POST", self.config['pool_actions']['webhook'], json={
                    'username': 'Pool.Energy Bot',
                    'embeds': [{
                        'color': 2522040,
                        'fields': [
                            {
                                'name': 'Pool Size',
                                'value': f"{round(json['pool_space'] / 1024 ** 5, 2)} PiB",
                                'inline': True
                            },
                            {
                                'name': 'Farmer(s)',
                                'value': f"{json['farmers_active']}",
                                'inline': True
                            },
                            {
                                'name': 'XCH Price',
                                'value': f"${json['xch_current_price']['usd']} / {json['xch_current_price']['eur']}€",
                                'inline': True
                            },
                            {
                                'name': 'Average Effort',
                                'value': f"{round(json['average_effort'], 2)}%",
                                'inline': True
                            },
                            {
                                'name': 'Pool Wallet Sync',
                                'value': f"{'Yes' if json['pool_wallets'][0]['synced'] else 'No'}",
                                'inline': True
                            },
                            {
                                'name': 'Fee Wallet Sync',
                                'value': f"{'Yes' if json['pool_wallets'][1]['synced'] else 'No'}",
                                'inline': True
                            }
                        ],
                        'footer': {
                            'text': 'Powered by pool.energy'
                        },
                        'timestamp': str(datetime.datetime.now(datetime.UTC))
                    }]
                }) as r:
                    if r.status != 204:
                        logger.warning(f"Invalid discord response: {r.status}, {r.content}")
                    pass

        # farmer
        if message.content.startswith('!farmer '):
            launcher = message.content.split('!farmer ')[1].strip()
            if launcher.startswith('0x'):
                launcher = launcher[2:]

            json = await self.get_launcher(launcher)
            if not json:
                return

            async with aiohttp.request("POST", self.config['pool_actions']['webhook'], json={
                    'username': 'Pool.Energy Bot',
                    'embeds': [{
                        'color': 2522040,
                        'fields': [
                            {
                                'name': 'Name',
                                'value': f"{json['name'] or 'Unknown'}",
                                'inline': True
                            },
                            {
                                'name': 'State',
                                'value': f"{'✅ Online' if json['is_pool_member'] else '❌ Offline'}",
                            },
                            {
                                'name': 'Launcher ID',
                                'value': f"{json['launcher_id']}",
                            },
                            {
                                'name': 'Points',
                                'value': f"{json['points_pplns']}",
                                'inline': True
                            },
                            {
                                'name': 'Difficulty',
                                'value': f"{json['difficulty']}",
                                'inline': True
                            },
                            {
                                'name': 'Block(s)',
                                'value': f"{json['blocks']['total']}",
                                'inline': True
                            },
                            {
                                'name': 'Harvester(s)',
                                'value': f"{json['partials']['harvesters']}",
                                'inline': True
                            },
                            {
                                'name': 'Partial(s)',
                                'value': f"{json['partials']['total']}",
                                'inline': True
                            },
                            {
                                'name': 'Estimated Size',
                                'value': f"{round(json['estimated_size'] / 1024 ** 4, 2)} TiB",
                                'inline': True
                            }
                        ],
                        'thumbnail': {
                            'url': f"{json['picture_url'] or ''}"
                        },
                        'footer': {
                            'text': 'Powered by pool.energy'
                        },
                        'timestamp': str(datetime.datetime.now(datetime.UTC))
                    }]
                }) as r:
                    if r.status != 204:
                        logger.warning(f"Invalid discord response: {r.status}, {r.content}")
                    pass

    async def get_launcher(self, launcher_id):
        if not launcher_id:
            return
        async with aiohttp.request("GET", f"{self.config['global']['baseapi']}/launcher/{launcher_id}/") as r:
            if r.status != 200:
                logger.warning(f"Launcher with id {launcher_id} not found: {r.status}, {r.content}")
                return
            return await r.json()
        
    async def get_stats(self):
        async with aiohttp.request("GET", f"{self.config['global']['baseapi']}/stats") as r:
            if r.status != 200:
                logger.warning(f"Invalid response from pool stats api: {r.status}, {r.content}")
                return
            return await r.json()
