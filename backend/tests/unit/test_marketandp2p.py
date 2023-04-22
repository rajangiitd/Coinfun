import pytest ,os , base64
from backend.utils.marketandp2p import get_market_data, get_fav_crypto_list, get_fav_page_data, get_p2p_buy_page_data ,get_p2p_sell_page_data, form_graph

def test_get_market_deta_WhenInputIsValid():
    assert type(get_market_data("coinfunnoreply3@gmail.com")) == list

def test_get_market_data_WhenInputIsNone():
    assert type(get_market_data()) == list

def test_get_market_data_WhenInvalidFilenameisGiven():
    with pytest.raises(Exception, match="Market data could not be fetched!"):
        get_market_data("example.exmaple","example.exmaple")
        


def test_get_fav_crypto_list_WhenFavListIsNonEmpty():
    assert type(get_fav_crypto_list("coinfunnoreply@gmail.com")) == list

def test_get_fav_crypto_list_WhenFavListIsEmpty():
    with pytest.raises(Exception, match="You do not have any favourite crypto currencies!"):
        get_fav_crypto_list("coinfunnoreply2@gmail.com")



def test_get_fav_page_data_WhenFavListIsNonEmpty():
    assert type(get_fav_page_data("coinfunnoreply@gmail.com"))== list

def test_get_fav_page_data_WhenFavListIsEmpty():
    with pytest.raises(Exception, match="You do not have any favourite crypto currencies!"):
        get_fav_page_data("coinfunnoreply2@gmail.com")



def test_p2p_buy_page_data_get():
    assert type(get_p2p_buy_page_data()) == list



def test_p2p_sell_page_data_get():
    assert type(get_p2p_sell_page_data()) == list



def test_form_graph_WhenInputIsValid():
    data = form_graph("BTC", "1m")
    assert type(data[0]) == str
    assert type(data[1]) == dict

def test_form_graph_WhenInputIsInValid():
    with pytest.raises(Exception):
        data = form_graph("example", "1m")