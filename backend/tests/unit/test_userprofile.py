import pytest
from backend.utils.userprofile import get_user_profile, change_pass_help

def test_get_user_profile_WhenInputIsValid():
    # Test if a valid email is accepted
    email = "coinfunnoreply@gmail.com"
    data = get_user_profile(email)
    assert data['email_id'] == email
    assert data['username'] == 'Testaccount1'
    assert type(data)==dict

def test_get_user_profile_When_input_is_invalid():
    # Test if a invalid email is accepted
    email = "example@example.com"
    with pytest.raises(Exception, match="Couldn't fetch user profile data"):
        get_user_profile(email)
        



def test_change_pass_help_WhenNewPassIsNotEqualNewPassConfirm():
    # Test if a valid email is accepted
    with pytest.raises(Exception, match="The new password does not matches the confirm new password !"):
        change_pass_help("coinfunnoreply@gmail.com","Testaccount1Testaccount1","Testaccount1Testaccount1","Testaccount1Testaccount")

def test_change_pass_help_WhenNewPassIsNotValid():
    # Test if a valid email is accepted
    with pytest.raises(Exception, match="Please enter a valid password (should contain atleast 1 capital and 1 small alphabets and atleast 1 digit with length between 8-25)"):
        change_pass_help("coinfunnoreply@gmail.com","Testaccount1Testaccount1","Test1","Test1")

def test_change_pass_help_WhenCurrentPassIsNotValid():
    # Test if a valid email is accepted
    with pytest.raises(Exception, match="The current entered password does not matches the exisiting password"):
        change_pass_help("coinfunnoreply@gmail.com","Old","Testaccount1Testaccount1","Testaccount1Testaccount1")

def test_change_pass_help_WhenInputIsValid():
    assert change_pass_help("coinfunnoreply@gmail.com","Testaccount1Testaccount1","Testaccount1Testaccount1","Testaccount1Testaccount1")=='PASSWORD UPDATED SUCCESSFULLY'  
