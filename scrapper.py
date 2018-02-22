from difflib import SequenceMatcher
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

SITE_COUNT=4
WAIT_LOADING_TIME=10

SITE_INDEX_WILLIAM=0
SITE_INDEX_BET365=1
SITE_INDEX_PADDYPOWER=2
SITE_INDEX_SKYBET=3

GAME_NAME_SIMILARITY_THRESHOLD=0.6

# calculate the similarity of game name
def isGameNameSimilar(a,b):
    return True if SequenceMatcher(None, a, b).ratio()>GAME_NAME_SIMILARITY_THRESHOLD else False

class Game():
    def __init__(self,_site_index,_game_name='',_home_odd='',_draw_odd='',_away_odds=''):
        self.game_name=_game_name
        self.home_odd=['' for i in range(SITE_COUNT)]
        self.draw_odd=['' for i in range(SITE_COUNT)]
        self.away_odd=['' for i in range(SITE_COUNT)]
        self.home_odd[_site_index]=_home_odd
        self.draw_odd[_site_index]=_draw_odd
        self.away_odd[_site_index]=_away_odds

class Scrapper():
    '''
    abstract class for all scrapper
    '''
    url = ''
    driver = None
    site_index = 0

    def __str__(self):
        return self.url

    def __init__(self, _url):
        assert _url
        self.url = _url
        self.driver = webdriver.Firefox()
        self.driver.get(_url)
        self.site_index=0

    def scrape(self, game_array):
        pass


class WilliamScrapper(Scrapper):

    def __init__(self, _url):
        super(WilliamScrapper, self).__init__(_url)
        self.site_index = SITE_INDEX_WILLIAM
        okBtn = self.driver.find_element_by_id('yesBtn')
        if okBtn:
            okBtn.click()

    def scrape(self, game_array):
        scrapped_count=0
        football_ele = self.driver.find_element_by_id('ip_sport_9_types')
        if not football_ele:
            return False
        leagues = football_ele.find_elements_by_xpath('div')

        for league in leagues:
            games=league.find_element_by_class_name('tableData').find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
            for one_game_info in games:
                tokens=one_game_info.text.split('\n')
                if len(tokens)==7:
                    found=False
                    for i in range(len(game_array)):
                        if isGameNameSimilar(game_array[i].game_name,tokens[2]):
                            game_array[i].home_odd[self.site_index] = tokens[3]
                            game_array[i].draw_odd[self.site_index] = tokens[4]
                            game_array[i].away_odd[self.site_index] = tokens[5]
                            found=True
                            break
                    if not found:
                        game=Game(self.site_index,tokens[2],tokens[3],tokens[4],tokens[5])
                        game_array.append(game)
                    scrapped_count+=1
        return scrapped_count

class Bet365Scrapper(Scrapper):
    def __init__(self, _url):
        super(Bet365Scrapper, self).__init__(_url)
        self.site_index = SITE_INDEX_BET365

    def scrape(self,game_array):
        scrapped_count = 0

        # try:
        #     WebDriverWait(self.driver, WAIT_LOADING_TIME).until(EC.presence_of_element_located((By.CLASS_NAME, 'b365FooterLogo set')))
        # except TimeoutException:
        #     return False

        sport_categorys= self.driver.find_elements_by_class_name('iph-InPlayLauncherClassification ')

        for sport_block in sport_categorys:
            sport_category=sport_block.find_element_by_class_name('ipl-InPlayLauncherClassificationHeader-Title ')
            assert sport_category
            if sport_category.text=='Soccer':
                games=sport_block.find_element_by_class_name('ipl-InPlayLauncherClassificationContainer ').find_elements_by_xpath('div')
                for one_game_info in games:
                    tokens=one_game_info.text.split('\n')
                    if len(tokens)==8:
                        found=False
                        game_name=tokens[0]+' v '+tokens[1]
                        for i in range(len(game_array)):
                            if isGameNameSimilar(game_array[i].game_name,game_name):
                                game_array[i].home_odd[self.site_index] = tokens[5]
                                game_array[i].draw_odd[self.site_index] = tokens[6]
                                game_array[i].away_odd[self.site_index] = tokens[7]
                                found = True
                                break
                        if not found:
                            game = Game(self.site_index, game_name, tokens[5], tokens[6], tokens[7])
                            game_array.append(game)
                        scrapped_count += 1
        return scrapped_count




class PaddypowerScrapper(Scrapper):
    def __init__(self, _url):
        super(PaddypowerScrapper, self).__init__(_url)
        self.site_index = SITE_INDEX_PADDYPOWER

    def scrape(self, game_array):
        scrapped_count=0

        try:
            WebDriverWait(self.driver, WAIT_LOADING_TIME).until(EC.element_to_be_clickable((By.CLASS_NAME, 'avb-coupon__item')))
        except TimeoutException:
            return False

        games=self.driver.find_element_by_class_name('card-container').find_elements_by_class_name('avb-coupon__item')

        for one_game_info in games:
            home_name_ele = one_game_info.find_element_by_class_name('ui-scoreboard-runner__home')
            away_name_ele = one_game_info.find_element_by_class_name('ui-scoreboard-runner__away')
            odds=one_game_info.find_elements_by_class_name('btn-odds')

            found=False
            game_name=home_name_ele.text+' v '+away_name_ele.text
            for i in range(len(game_array)):
                if isGameNameSimilar(game_array[i].game_name,game_name):
                    game_array[i].home_odd[self.site_index] = odds[0].text
                    game_array[i].draw_odd[self.site_index] = odds[1].text
                    game_array[i].away_odd[self.site_index] = odds[2].text
                    found=True
                    break
            if not found:
                game = Game(self.site_index, game_name, odds[0].text, odds[1].text, odds[2].text)
                game_array.append(game)
            scrapped_count += 1
        return scrapped_count
