
from scrapper import WilliamScrapper,Bet365Scrapper,PaddypowerScrapper
from time import sleep

WILLIAM_URL='http://sports.williamhill.com/bet/en-gb/betlive/all'
BET365_URL='https://mobile.bet365.com/'
PADDYPOWER_URL='https://www.paddypower.com/inplay?tab=football'

scrapping_interval=5
game_array = []
scrappers=[]

scrappers.append(WilliamScrapper(WILLIAM_URL))
scrappers.append(Bet365Scrapper(BET365_URL))
scrappers.append(PaddypowerScrapper(PADDYPOWER_URL))
# scrappers.append(Bet365Scrapper(BET365_URL))

while True:
    for i in range(len(scrappers)):
        gameCount=scrappers[i].scrape(game_array)
        # print('{}   {}'.format(scrappers[i].url,gameCount))

    # out=open('out.pickle',"wb")
    # pickle.dump(game_array,out)
    # out.close()

    # inFile=open('out.pickle','rb')
    # game_array=pickle.load(inFile)

    print('--------------------------------')
    for i in range(len(game_array)):
        print('{:>64}:  '.format(game_array[i].game_name),end="")
        for j in range(len(scrappers)):
        # for j in range(3):
            oddsStr='{:8} {:8} {:8}'.format(game_array[i].home_odd[j],game_array[i].draw_odd[j],game_array[i].away_odd[j])
            print('    {}    '.format(oddsStr),end="")

        print(flush=True)
    sleep(scrapping_interval)







