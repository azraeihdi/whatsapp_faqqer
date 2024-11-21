import time
import sys
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

driver = webdriver.Chrome()

def wait(t, method, selector, k):
    try:
        if k:
            WebDriverWait(driver, t).until(
                EC.presence_of_element_located((method, selector))
            )
        else:
            WebDriverWait(driver, t).until_not(
                EC.presence_of_element_located((method, selector))
            )
    except TimeoutException:
        print('Timeout')
        exit()

def chat(message):
    # ask and submit question
    driver.find_elements(By.XPATH, '//*[@role=\'textbox\']')[-1].send_keys(message)
    driver.find_element(By.XPATH, '//*[@aria-label=\'Send\']').click()
    time.sleep(1)
    # wait until message is received
    while not chat_wait(): time.sleep(3)
    # return message
    return chat_message(driver.find_elements(By.XPATH, '//*[@role=\'row\']')[-1].get_attribute('innerHTML'))
    # what if a document, or image, or sticker, etc.?

def chat_wait():
    # get latest row
    element = driver.find_elements(By.XPATH, '//*[@role=\'row\']')[-1]
    try:
         # just in case the system text appears, like in most business accounts ya know
         element.find_element(By.CLASS_NAME, 'message-in')
    except NoSuchElementException:
         return False
    # return element.find_element(By.TAG_NAME, 'div').get_attribute('data-id').startswith('false_')
    return True


def chat_message(element):
    soup = BeautifulSoup(element, 'html.parser')
    message_div = soup.find('div', class_='copyable-text')
    if not message_div:
        return "No text found"
    
    # Extract text from spans
    spans = message_div.find_all('span', dir='ltr')
    text_content = " ".join(span.get_text(strip=True) for span in spans)
    
    # Replace sequences to clean up unnecessary spaces
    return text_content.replace("\n", " ").strip()

def main(csv_file):
    #initialize
    df = pd.read_csv(csv_file, header=None)    
    if df.empty:
        print('Empty input')
        exit()
    driver.get('https://web.whatsapp.com');
    # wait for qr
    wait(60, By.TAG_NAME, 'canvas', True)
    print('Please scan the QR code to log in')
    # wait for log in
    wait(90, By.TAG_NAME, 'canvas', False)
    # wait for chat to appear
    wait(30, By.XPATH, '//*[@title=\'Chats\']', True)
    # link to the contact
    contact_number = df.loc[0,0]
    contact_link = f'https://web.whatsapp.com/send/?phone=6{contact_number}&text&type=phone_number&app_absent=0'
    driver.get(contact_link);
    time.sleep(10)

    ## chat test 
    try:
        for i in range(len(df)):
            if i == 0: continue # skip the number
            question = df.loc[i,0]
            # print(f'{question}')
            reply = chat(question)
            # print(f'\t{reply}')
            df.loc[i,1] = reply
    except:
        print('Error')
    finally:
        df.to_csv('output.csv', header=None, index=False)
        time.sleep(5)
        driver.quit()

if __name__ == "__main__":
    main(sys.argv[1])