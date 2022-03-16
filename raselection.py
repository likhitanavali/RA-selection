import json
import asyncio
import aiohttp
import platform
from sklearn import mixture

url = "https://24zl01u3ff.execute-api.us-west-1.amazonaws.com/beta"
res = []

async def get_coins():
    """Makes asynchronous API call to the given url to get the Coin draws
    :return: None
    """
    async with aiohttp.ClientSession() as session:
        for i in range(30):
            response = await asyncio.create_task(session.get(url))
            res.append(await response.json())

def get_theta(coin_flips):
    """Calculates the theta values for two coins

    :param coin_flips: Dictionary with keys(0, 1) as coin type and value as the coin flips
    :return: 2 theta values for coin-0 and coin-1
    """
    thetaA = coin_flips[0].count(1)/len(coin_flips[0])
    thetaB = coin_flips[1].count(1)/len(coin_flips[1])
    return thetaA, thetaB

def main():
    if platform.system()=='Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) #bug with asyncio on windows
    loop = asyncio.new_event_loop()
    loop.run_until_complete(get_coins())
    loop.close()
    coin_flips = []
    if res:
        for i in res:
            if "body" in i.keys():
                body = json.loads(i["body"])
                coin_flips.append(body)
    gmm = mixture.GaussianMixture(n_components=2, max_iter=10000, covariance_type='tied', init_params = "random").fit(coin_flips)
    result = gmm.predict(coin_flips)
    labelled = {0:[], 1:[]}
    for i in range(len(coin_flips)):
        labelled[result[i]] += coin_flips[i]
    thetaA, thetaB = get_theta(labelled)
    print(f"ThetaA: {thetaA}, ThetaB: {thetaB}")

if __name__ == "__main__":
    main()
